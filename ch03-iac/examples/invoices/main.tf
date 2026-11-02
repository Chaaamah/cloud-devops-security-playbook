# Lab 1: consume the module from a separate root module, pinned to a release tag.

provider "aws" {
  region = "eu-west-1"
}

resource "aws_kms_key" "data" {
  description             = "Data key for the invoices bucket"
  enable_key_rotation     = true
  deletion_window_in_days = 30
}

module "invoices_bucket" {
  # After tagging a release of this repository:
  #   source = "git::https://github.com/Chaaamah/cloud-devops-security-playbook.git//ch03-iac/modules/secure-bucket?ref=v1.0.0"
  source = "../../modules/secure-bucket"

  name           = "acme-prod-invoices-111122223333"
  kms_key_arn    = aws_kms_key.data.arn
  retention_days = 2555        # 7 years for financial records

  tags = {
    owner       = "billing-team"
    environment = "prod"
    data_class  = "confidential"
  }
}

output "invoices_bucket_arn" {
  value = module.invoices_bucket.bucket_arn
}
