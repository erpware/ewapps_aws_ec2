output "api_endpoint" {
  value = aws_api_gateway_stage.ew_app_ec2_stage.invoke_url
}