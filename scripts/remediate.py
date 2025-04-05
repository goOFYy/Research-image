#!/usr/bin/env python3
import json
import os
import re
import sys
import requests

DOCKERFILE   = "Dockerfile"
PACKAGE_JSON = "package.json"
GITHUB_API   = "https://api.github.com"

def load_json(path):
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)

def write_json(path, data):
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)

def parse_image_ref(image_ref):
    _, remainder = image_ref.split('/', 1)
    owner_repo, _ = remainder.rsplit(':', 1)
    return owner_repo.split('/', 1)

def fetch_latest_ghcr_tag(owner, pkg, token):
    url = f"{GITHUB_API}/users/{owner}/packages/container/{pkg}/versions"
    headers = {
        "Accept":        "application/vnd.github+json",
        "Authorization": f"Bearer {token}"
    }
    tags = []
    page = 1
    while True:
        resp = requests.get(url, headers=headers, params={"per_page":100, "page":page})
        resp.raise_for_status()
        versions = resp.json()
        if not versions:
            break
        for v in versions:
            tags.extend(v.get("metadata", {}).get("container", {}).get("tags", []))
        page += 1
    if not tags:
        raise RuntimeError("No tags found in GHCR")
    return sorted(tags)[-1]

def bump_dockerfile(plan):
    image_ref = plan.get("base_image")
    if not image_ref:
        print("ℹ️ No base_image; skipping base image bump")
        return False

    owner, pkg = parse_image_ref(image_ref)
    token = os.getenv("GHCR_TOKEN")
  
   
    if not token:
        sys.exit("❌ GHCR_TOKEN not set in environment")

    latest = fetch_latest_ghcr_tag(owner, pkg, token)
    new_ref = f"ghcr.io/{owner}/{pkg}:{latest}"

    content = open(DOCKERFILE, 'r', encoding='utf-8').read()
    new_content, count = re.subn(
        r'^\s*FROM\s+[^\s]+',
        f"FROM {new_ref}",
        content,
        flags=re.IGNORECASE | re.MULTILINE
    )
    if count == 0:
        raise RuntimeError("No FROM line found in Dockerfile")
    if new_content != content:
        open(DOCKERFILE, 'w', encoding='utf-8').write(new_content)
        print(f"✅ Dockerfile FROM updated to {new_ref}")
        return True
    print("ℹ️ Dockerfile already up-to-date")
    return False

def clean_version_spec(spec):
    """Strip leading '>=' from a version specifier."""
    if isinstance(spec, str):
        return re.sub(r'^>=\s*', '', spec).strip()
    return spec

def clean_all_ge(data):
    """
    Strip leading '>=' from all dependencies and devDependencies in package.json.
    """
    changed = False
    for section in ("dependencies", "devDependencies"):
        deps = data.get(section, {})
        for pkg, spec in list(deps.items()):
            new_spec = clean_version_spec(spec)
            if new_spec != spec:
                print(f"🔄 Cleaning {section}: {pkg} '{spec}' → '{new_spec}'")
                deps[pkg] = new_spec
                changed = True
    return changed

def bump_npm_packages(plan):
    data = load_json(PACKAGE_JSON)
    changed = False

    # 1) Strip leading '>=' from existing package.json entries
    print("🔧 Stripping all leading '>=' from package.json...")
    if clean_all_ge(data):
        changed = True
        write_json(PACKAGE_JSON, data)
        print("✅ Removed all '>=' operators from package.json")
    else:
        print("ℹ️ No '>=' operators found in package.json to remove")

    # 2) Handle CVE-based bumps, stripping '>=' from FixedVersion
    vulns = plan.get("app_vulnerabilities", [])
    pkg_fixed = {}
    for v in vulns:
        pkg = v.get("PkgName")
        fixed = v.get("FixedVersion")
        if pkg and fixed:
            # Clean the FixedVersion before storing it
            cleaned_fixed = clean_version_spec(fixed)
            if pkg not in pkg_fixed or cleaned_fixed > pkg_fixed[pkg]:
                pkg_fixed[pkg] = cleaned_fixed

    if pkg_fixed:
        print("🔧 Bumping vulnerable packages to fixed versions...")
        for section in ("dependencies", "devDependencies"):
            deps = data.get(section, {})
            for pkg, fixed in pkg_fixed.items():
                if pkg in deps:
                    old = deps[pkg]
                    if old != fixed:
                        print(f"🔄 {section}: {pkg} '{old}' → '{fixed}'")
                        deps[pkg] = fixed
                        changed = True

    if changed:
        write_json(PACKAGE_JSON, data)
        print("✅ package.json fully updated")
    else:
        print("ℹ️ package.json already up-to-date (no changes)")

    return changed

def main(plan_path):
    plan = load_json(plan_path)
    bump_dockerfile(plan)
    bump_npm_packages(plan)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: remediate.py <remediation_plan.json>")
    main(sys.argv[1])
