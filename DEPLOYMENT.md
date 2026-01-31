# Deployment Guide: Scaleway Serverless

This guide details how to deploy the Voice Assistant backend to Scaleway Functions.

## Prerequisites

1.  **Scaleway Account**: Ensure you have an active account.
2.  **Scaleway CLI**: [Install the CLI](https://github.com/scaleway/scaleway-cli).
3.  **Python 3.10+**: Ensure Python is installed locally for testing.

## Configuration

1.  **Environment Variables**:
    Create a `.env` file in `backend/` (already done if you followed the assistant).
    Ensure the following variables are set:
    ```bash
    SCW_ACCESS_KEY=<your-access-key>
    SCW_SECRET_KEY=<your-secret-key>
    SCW_DEFAULT_PROJECT_ID=<your-project-id>
    MONGO_USERNAME=<mongo-user>
    MONGO_PASSWORD=<mongo-pass>
    MONGO_HOST=<mongo-host-url>
    MONGO_DB_NAME=voice_assistant
    SENDER_EMAIL=<verified-sender-email>
    ```

## Deployment

We use **OpenTofu** (or Terraform) to manage the infrastructure.

### 1. Prepare Credentials
The OpenTofu configuration is in the root directory. You can populate variables using a `terraform.tfvars` file or environment variables.

**Recommended:** Create `terraform.tfvars` in the root directory with the following content (DO NOT COMMIT THIS FILE):

```hcl
scw_access_key           = "SCW..."
scw_secret_key           = "..."
scw_project_id           = "..."
mongo_username           = "..."
mongo_password           = "..."
mongo_instance_id        = "..."
mongo_private_network_id = "..."
mongo_region             = "fr-par"
sender_email             = "..."
```

*Tip: You can copy values from `backend/.env`.*

### 2. Run OpenTofu

Ensure you are in the project root:

```bash
# Verify you see main.tf
ls main.tf
```

Initialize the project:
```bash
tofu init
```

Plan the deployment:
```bash
tofu plan
```

Apply the deployment:
```bash
tofu apply
```

### 3. Post-Deployment
Tofu will output the `function_endpoint`.
Update your Android App's `ApiService` with this URL.
