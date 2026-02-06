variable "scw_access_key" {
  type      = string
  sensitive = true
}

variable "scw_secret_key" {
  type      = string
  sensitive = true
}

variable "scw_project_id" {
  type = string
}

variable "mongo_username" {
  type = string
}

variable "mongo_password" {
  type      = string
  sensitive = true
}

variable "mongo_instance_id" {
  type = string
}

variable "mongo_private_network_id" {
  type = string
}

variable "mongo_region" {
  type = string
}

variable "mongo_tls_cert_file" {
  type    = string
  default = "cert.pem"
}

variable "mongo_db_name" {
  type    = string
  default = "voice_assistant"
}

variable "sender_email" {
  type = string
}

variable "llm_api_url" {
  type    = string
  default = "https://api.scaleway.ai/v1/chat/completions"
}

variable "llm_model" {
  type    = string
  default = "mistral-small-3.2-24b-instruct-2506"
}

variable "stt_model" {
  type    = string
  default = "whisper-large-v3"
}
