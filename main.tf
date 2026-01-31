terraform {
  required_providers {
    scaleway = {
      source = "scaleway/scaleway"
    }
    archive = {
      source = "hashicorp/archive"
    }
  }
  required_version = ">= 0.13"
}

provider "scaleway" {
  access_key = var.scw_access_key
  secret_key = var.scw_secret_key
  project_id = var.scw_project_id
  region     = "fr-par"
  zone       = "fr-par-1"
}

# Zip the backend code
data "archive_file" "function_zip" {
  type        = "zip"
  source_dir  = "${path.module}/backend"
  output_path = "${path.module}/function.zip"
  excludes    = [".env", "__pycache__", "*.pyc", "venv", ".venv"]
}

# Create Function Namespace
resource "scaleway_function_namespace" "main" {
  name        = "voice-assistant-ns"
  description = "Namespace for Voice Assistant functions"
  region      = "fr-par"
}

# Deploy Function
resource "scaleway_function" "main" {
  namespace_id       = scaleway_function_namespace.main.id
  name               = "voice-assistant"
  runtime            = "python311"
  handler            = "handler.handler"
  privacy            = "private"
  zip_file           = data.archive_file.function_zip.output_path
  zip_hash           = data.archive_file.function_zip.output_base64sha256
  deploy             = true
  private_network_id = var.mongo_private_network_id

  # Deploy the function after the zip is ready
  depends_on = [data.archive_file.function_zip]

  environment_variables = {
    MONGO_USERNAME           = var.mongo_username
    MONGO_DB_NAME            = var.mongo_db_name
    MONGO_INSTANCE_ID        = var.mongo_instance_id
    MONGO_PRIVATE_NETWORK_ID = var.mongo_private_network_id
    MONGO_REGION             = var.mongo_region
    MONGO_TLS_CERT_FILE      = var.mongo_tls_cert_file # "cert.pem" inside the zip
    SENDER_EMAIL             = var.sender_email
  }

  secret_environment_variables = {
    SCW_ACCESS_KEY = var.scw_access_key
    SCW_SECRET_KEY = var.scw_secret_key
    MONGO_PASSWORD = var.mongo_password
  }
}

# Create a token for the function
resource "scaleway_function_token" "main" {
  function_id = scaleway_function.main.id
  description = "Token for Android App"
}
