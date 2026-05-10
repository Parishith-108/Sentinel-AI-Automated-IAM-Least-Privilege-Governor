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
