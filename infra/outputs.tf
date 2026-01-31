output "function_endpoint" {
  value       = scaleway_function.main.domain_name
  description = "The endpoint URL of the deployed function"
}
