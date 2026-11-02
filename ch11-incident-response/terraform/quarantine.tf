# One quarantine security group per VPC, created ahead of time (section 11.2).
# Terraform removes the default allow-all egress rule AWS adds to new security groups,
# so this group allows nothing in and nothing out.
variable "vpc_id" {
  type = string
}

resource "aws_security_group" "quarantine" {
  name        = "quarantine"
  description = "Incident response isolation: no inbound, no outbound"
  vpc_id      = var.vpc_id
  tags        = { purpose = "incident-response" }
}

output "quarantine_security_group_id" {
  value = aws_security_group.quarantine.id
}
