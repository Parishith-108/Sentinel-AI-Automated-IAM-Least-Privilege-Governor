# Sentinel-AI: Intelligent IAM Least-Privilege Governor 🛡️🤖

## Project Overview
**Sentinel-AI** is a cloud-native security solution designed to automate the process of IAM policy hardening. In modern AWS environments, "over-privileged" identities are a primary attack vector. This project leverages **Generative AI (Amazon Bedrock)** to analyze broad IAM policies and automatically suggest or implement scoped-down, least-privileged versions.

This project demonstrates a shift from "Passive Detection" to **"Active AI Remediation"** in Cloud Security.

---

## 🚀 Key Features
* **Event-Driven Detection:** Monitors for high-risk IAM findings via **AWS Access Analyzer**.
* **AI-Powered Analysis:** Uses **Anthropic Claude 3.5 (via Amazon Bedrock)** to interpret policy intent and historical usage.
* **Infrastructure as Code (IaC):** Fully deployable via **Terraform** for consistent, repeatable security environments.
* **DevSecOps Integration:** Automates the creation of GitHub Pull Requests with remediated JSON policies, keeping "Human-in-the-loop" oversight.

---

## 🏗️ Architecture
1. **Trigger:** `AWS Access Analyzer` identifies an over-privileged or unused permission.
2. **Orchestration:** `Amazon EventBridge` captures the finding and triggers an `AWS Lambda` function.
3. **Intelligence:** The Lambda function sends the "dirty" policy to `Amazon Bedrock`.
4. **Remediation:** The AI returns a "Clean" policy, and the script pushes a PR to the security repository for review.

---

## 🛠️ Tech Stack
| Category | Technology |
| :--- | :--- |
| **Cloud Provider** | AWS (IAM, Bedrock, Lambda, EventBridge, CloudWatch) |
| **Languages** | Python 3.11 (Boto3) |
| **IaC** | Terraform |
| **AI Model** | Anthropic Claude 3.5 Sonnet |
| **Version Control** | GitHub API / Git |

---

## 📂 Repository Structure
* `main.tf`: Defines the AWS security infrastructure.
* `iam_logic.py`: The core Python logic for AI policy rewriting.
* `requirements.txt`: Python library dependencies.
* `prompts/`: (Optional) Documentation of the system prompts used for the LLM.

---

## ⚡ Quick Start
### Prerequisites
- AWS Account with **Amazon Bedrock** model access enabled.
- Terraform installed.
- AWS CLI configured with appropriate permissions.

### Deployment
1. **Initialize Terraform:**
   ```bash
   terraform init
