# Research Image Vulnerability Demo

GitHub Workflow Status
This repository demonstrates a Docker image build, vulnerability scanning with Trivy, and automated remediation using GitHub Actions. 

## Contents

* Dockerfile: Builds an image with known vulnerable Node.js packages.
* package.json: Specifies the dependencies with outdated, vulnerable versions.
* GitHub Actions Workflow: Automates building, scanning, analyzing, and remediating vulnerabilities.
* Script: python scripts used in the workflow to analyze and remediate

## Workflow

The GitHub Actions workflow (.github/workflows/pr.yml) performs the following:

1. Build: Builds the Docker image and saves it as an artifact.
2. Scan: Loads the image, scans it with Trivy, and displays results in the workflow summary.
3. Analyze: Generates a remediation plan (placeholder).
4. Remediate: Applies fixes and comments on the PR (requires owner PAT).

## Examples:

### base-1:

![oldimage](https://github.com/user-attachments/assets/2001148a-b241-4e13-bb5c-abec598e1cae)

### base-2 (after the automated update):

![newimage](https://github.com/user-attachments/assets/02c480c5-d31e-4584-8e0d-b7e761313f56)

### changes:

![change log](https://github.com/user-attachments/assets/e14f5b03-3548-4981-99a4-66e016cd26ba)











