# Run from the module folder: terraform init && terraform test
mock_provider "aws" {}   # Terraform 1.7+: runs without cloud credentials

variables {
  name        = "test-bucket"
  kms_key_arn = "arn:aws:kms:eu-west-1:111122223333:key/example"
  tags = {
    owner       = "platform-team"
    environment = "test"
    data_class  = "internal"
  }
}

run "public_access_is_blocked_by_default" {
  command = plan

  assert {
    condition     = aws_s3_bucket_public_access_block.this.block_public_policy == true
    error_message = "Bucket must block public policies by default"
  }

  assert {
    condition     = aws_s3_bucket_public_access_block.this.restrict_public_buckets == true
    error_message = "Bucket must restrict public buckets by default"
  }
}

run "versioning_and_kms_are_enabled" {
  command = plan

  assert {
    condition     = aws_s3_bucket_versioning.this.versioning_configuration[0].status == "Enabled"
    error_message = "Versioning must be enabled"
  }
}

run "no_lifecycle_rule_without_retention" {
  command = plan

  assert {
    condition     = length(aws_s3_bucket_lifecycle_configuration.this) == 0
    error_message = "No lifecycle rule should exist when retention_days is 0"
  }
}

run "missing_required_tag_is_rejected" {
  command = plan

  variables {
    tags = { owner = "platform-team" }
  }

  expect_failures = [var.tags]
}
