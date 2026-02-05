---
name: Deployment Manager
description: Automates the packaging and deployment of the backend to Scaleway using Terraform.
---

# Deployment Manager Skill

This skill automates the deployment of the serverless backend.

## 1. Clean & Build
*   **Clean**: Remove old `function.zip`.
*   **Package**: Zip the `backend/` directory into `function.zip`.
    *   **Exclude**: `__pycache__`, `tests/`, `*.pyc`, `.env`, and local virtual environments.
    *   **Command**: `zip -r function.zip backend/ -x "*/__pycache__/*" "*/.*" "*tests*"` (Run from project root).

## 2. Infrastructure Deployment (Terraform)
*   **Initialize**: Ensure terraform is initialized. `terraform init` (only needed once or if modules change).
*   **Apply**: Run `terraform apply -auto-approve`.
    *   **Note**: Ensure `terraform.tfvars` or environment variables are set for secrets (API Keys, etc.).

## 3. Verification
*   **Check Output**: Capture the `function_url` from Terraform outputs.
*   **Health Check**: Send a simple GET/POST to the URL to ensure it doesn't return 500.

## Usage
Run this skill whenever `backend/` code changes and needs to be pushed to production.
