# Sentinel-AI: Automated IAM Least-Privilege Governor

Elevator pitch
--------------

Sentinel-AI helps teams eliminate over-privileged AWS IAM policies by automating detection, analysis, and suggested remediation. It listens for IAM Access Analyzer findings, uses an LLM (Amazon Bedrock / Claude 3.5 Sonnet) to interpret CloudTrail evidence and the policy's intent, and proposes a least-privilege replacement via a GitHub Pull Request for human review.

Why this matters
-----------------

- Reduces blast radius caused by wildcard or overly-broad IAM policies.
- Speeds up audits by automatically surfacing targeted, reviewable PRs.
- Keeps humans in the loop — auto-suggestions are always presented for review before any changes are applied.

This repository provides a deployable prototype (IaC + Lambda) and local development tooling so you can test, iterate, and harden the solution for production.

---

Overview
--------

Sentinel-AI is a prototype pipeline that detects over-privileged AWS IAM policies, analyzes them with an LLM (Amazon Bedrock / Claude 3.5 Sonnet), rewrites them to least-privilege, and opens a GitHub Pull Request with the corrected policy for human review.

This repository contains a deployable example: a Terraform `main.tf` that outlines the AWS resources, and a Python Lambda handler `iam_logic.py` that demonstrates how to process an Access Analyzer finding, call Bedrock, and create a GitHub PR.

Contents
--------

- `main.tf` — Terraform skeleton to deploy EventBridge rule + Lambda + IAM roles (notes included).
- `iam_logic.py` — Python Lambda handler: retrieves an Access Analyzer finding from EventBridge payload, queries CloudTrail for related events (pseudo), calls Amazon Bedrock (pseudo), generates a least-privilege policy, and creates a GitHub PR.
- `requirements.txt` — Python dependencies for local testing and Lambda packaging.
- `prompts/system_prompt.txt` — The system prompt used for Bedrock calls.

Important
---------

This project provides a local prototype and IaC skeleton. It does NOT perform real AWS actions out of the box from this repo; you must supply AWS credentials, configure Bedrock access, and provide GitHub credentials or a token. The Terraform is minimal and meant as a starting point — review and adapt before deploying.

Quick start (local test)
------------------------

1. Create a Python virtualenv and install dependencies:

```powershell
python -m venv .venv
. \.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the handler locally with a sample event:

```powershell
python iam_logic.py --local-test samples/sample_event.json
```

3. To deploy: review `main.tf`, configure AWS credentials, then run `terraform init` and `terraform apply`.

Architecture
------------

Trigger: EventBridge rule that matches IAM Access Analyzer findings (unused-access).

Processor: Python Lambda consumes the finding, gathers CloudTrail evidence, calls Bedrock to rewrite the policy, and opens a GitHub PR.

AI Engine: Amazon Bedrock (Claude 3.5 Sonnet). The prompt is included in `prompts/system_prompt.txt` and is designed for an AWS security expert persona.

Security & Governance
---------------------

- Keep Bedrock and GitHub credentials out of source control (use Secrets Manager or AWS SSM Parameter Store).
- Review generated policies before applying them.
- Add logging, alerting, and human-in-the-loop gating in production.

Files
-----

See the repository files for implementation details and comments. This is a starting point—adapt it to your security posture and operational requirements.

License
-------

MIT

---

Deploy & run (detailed)
----------------------

These steps describe how to package the Lambda, run Terraform, and test locally. They assume you're on Windows PowerShell (pwsh) and using the repository root `D:/Personal Files/VS Coding/Project-1`.

1) Package the Lambda for Terraform (creates `deploy/package.zip`):

```powershell
cd .\sentinel-ai
.\scripts\package_lambda.ps1
```

2) Review and apply Terraform (example):

```powershell
cd ..\sentinel-ai
# initialize and review plan
terraform init
terraform plan -out plan.tfplan
# when ready
terraform apply plan.tfplan
```

Notes:
- Ensure `deploy/package.zip` S3 upload or local path in `main.tf` matches your Terraform variables.
- Provide AWS credentials via environment variables, named profiles, or CI secrets (do not store them in source control).

3) Local testing (dry-run)

Set environment variables for local runs (example):

```powershell
# Only for local testing - never store long-lived tokens in source control
$env:GITHUB_TOKEN = 'ghp_...'
$env:BEDROCK_MODEL_ID = 'claude-3.5-sonnet'
python iam_logic.py --local-test samples/sample_event.json
```

4) Tests

Run the unit tests with pytest (inside virtualenv):

```powershell
# from repository root
cd .\sentinel-ai
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
```

Create a pull request (history-preserving)
----------------------------------------

If you want to preserve the branch history from `sentinel-ai-clean`, create a PR that merges that branch into `main`. I can't create the PR programmatically here without a token that has Pull Requests and Repository Contents write access. You can open the PR from the web UI or with the GitHub CLI. Examples:

Web UI (one-click):

https://github.com/Parishith-108/Sentinel-AI-Automated-IAM-Least-Privilege-Governor/compare/main...sentinel-ai-clean?expand=1

gh CLI (if you prefer the terminal):

```powershell
# authenticate first: gh auth login
gh pr create --base main --head sentinel-ai-clean --title "chore: add Sentinel-AI prototype (EventBridge + Lambda + Bedrock + GitHub PR flow)" --body "This PR adds the Sentinel-AI prototype. CI runs tests and packages the Lambda artifact.\n\nSee README for quick start and architecture. Please review the Terraform skeleton, IAM role assumptions, and the LLM integration approach before merging."
```

Security reminder
-----------------
- Revoke any tokens you pasted into this environment and create short-lived fine-grained tokens for automation. For programmatic PR creation the token must include repository Contents: Read & write and Pull requests: Read & write permissions (or classic `repo` scope).
# Sentinel-AI: Automated IAM Least-Privilege Governor

Overview
--------

Sentinel-AI is a prototype pipeline that detects over-privileged AWS IAM policies, analyzes them with an LLM (Amazon Bedrock / Claude 3.5 Sonnet), rewrites them to least-privilege, and opens a GitHub Pull Request with the corrected policy for human review.

This repository contains a deployable example: a Terraform `main.tf` that outlines the AWS resources, and a Python Lambda handler `iam_logic.py` that demonstrates how to process an Access Analyzer finding, call Bedrock, and create a GitHub PR.

Contents
--------

- `main.tf` — Terraform skeleton to deploy EventBridge rule + Lambda + IAM roles (notes included).
- `iam_logic.py` — Python Lambda handler: retrieves an Access Analyzer finding from EventBridge payload, queries CloudTrail for related events (pseudo), calls Amazon Bedrock (pseudo), generates a least-privilege policy, and creates a GitHub PR.
- `requirements.txt` — Python dependencies for local testing and Lambda packaging.
- `prompts/system_prompt.txt` — The system prompt used for Bedrock calls.

Important
---------

This project provides a local prototype and IaC skeleton. It does NOT perform real AWS actions out of the box from this repo; you must supply AWS credentials, configure Bedrock access, and provide GitHub credentials or a token. The Terraform is minimal and meant as a starting point — review and adapt before deploying.

Quick start (local test)
------------------------

1. Create a Python virtualenv and install dependencies:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

2. Run the handler locally with a sample event:

```powershell
python iam_logic.py --local-test samples/sample_event.json
```

3. To deploy: review `main.tf`, configure AWS credentials, then run `terraform init` and `terraform apply`.

Architecture
------------

Trigger: EventBridge rule that matches IAM Access Analyzer findings (unused-access).

Processor: Python Lambda consumes the finding, gathers CloudTrail evidence, calls Bedrock to rewrite the policy, and opens a GitHub PR.

AI Engine: Amazon Bedrock (Claude 3.5 Sonnet). The prompt is included in `prompts/system_prompt.txt` and is designed for an AWS security expert persona.

Security & Governance
---------------------

- Keep Bedrock and GitHub credentials out of source control (use Secrets Manager or AWS SSM Parameter Store).
- Review generated policies before applying them.
- Add logging, alerting, and human-in-the-loop gating in production.

Files
-----

See the repository files for implementation details and comments. This is a starting point—adapt it to your security posture and operational requirements.

License
-------

MIT
