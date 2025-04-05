import json
import sys
import re

DOCKERFILE = "Dockerfile"
def extract_base_from_dockerfile(path="DOCKERFILE"):
    """
    Reads Dockerfile and returns the base image reference from the FROM line
 
    """
    pattern = re.compile(r'^\s*FROM\s+([^\s]+)', re.IGNORECASE)
    with open(path, 'r', encoding='utf-8') as f:
        for line in f:
            m = pattern.match(line)
            if m:
                return m.group(1)
def analyze_trivy_report(report_path):
    with open(report_path, 'r', encoding='utf-8') as f:
        report = json.load(f)

    image_ref = extract_base_from_dockerfile(DOCKERFILE)
    base_vulnerabilities = []
    app_vulnerabilities = []

    # Trivy's JSON output typically contains a "Results" key that is a list.
    # Each result has a "Target" field (the scanned component, e.g., a base image or application package).
    for result in report.get("Results", []):
        Class = result.get("Class", "")
        vulns = result.get("Vulnerabilities", [])
     
        if not vulns:
            continue
        
        # Example logic: if the target string contains "ubuntu:" or your base image name, treat it as a base image vulnerability.
        # Otherwise, consider it an application layer vulnerability.
        if "os-pkgs" in Class:
            base_vulnerabilities.extend(vulns)
        else:
            app_vulnerabilities.extend(vulns)

    remediation_plan = {
        "base_image": image_ref,
        "base_vulnerabilities": base_vulnerabilities,
        "app_vulnerabilities": app_vulnerabilities
    }
    for result in report.get("Results", []):
        target = result.get("Target", "")
        print(f"Found target: {target}")

    with open("remediation_plan.json", "w") as f:
        json.dump(remediation_plan, f, indent=2)
    print("Remediation plan written to remediation_plan.json")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python analyze_vulnerabilities.py <trivy-report.json>")
        sys.exit(1)
    
    report_path = sys.argv[1]
    analyze_trivy_report(report_path)
