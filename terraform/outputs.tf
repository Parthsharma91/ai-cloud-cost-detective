output "vpc_id" {
  description = "ID of the AI Cloud Cost Detective VPC."
  value       = aws_vpc.main.id
}

output "public_subnet_id" {
  description = "ID of the public subnet."
  value       = aws_subnet.public.id
}
output "security_group_id" {
  description = "ID of the application security group."
  value       = aws_security_group.app.id
}