output "function_endpoint" {
  value       = scaleway_function.main.domain_name
  description = "The endpoint URL of the deployed function"
}

output "function_token" {
  value       = scaleway_function_token.main.token
  description = "Authentication token for the private function (X-Auth-Token)"
  sensitive   = true
}
