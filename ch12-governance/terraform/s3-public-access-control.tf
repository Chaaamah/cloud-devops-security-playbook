# Lab 2: one control end to end — "no S3 bucket is publicly readable".
# Prevent, detect, auto-remediate, and keep the evidence.
# Requires AWS Config to be recording in the account (configuration recorder + delivery channel).

variable "account_id" {
  type = string
}

# 1. PREVENT: block public access for the whole account, whatever a bucket says.
resource "aws_s3_account_public_access_block" "this" {
  account_id              = var.account_id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# 2. DETECT: an AWS managed Config rule evaluates every bucket continuously.
resource "aws_config_config_rule" "s3_public_read" {
  name = "s3-bucket-public-read-prohibited"
  source {
    owner             = "AWS"
    source_identifier = "S3_BUCKET_PUBLIC_READ_PROHIBITED"
  }
}

# 3. REMEDIATE: a non-compliant bucket gets its public access blocked automatically.
data "aws_iam_policy_document" "remediation_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "Service"
      identifiers = ["ssm.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "remediation" {
  name               = "config-remediation-s3-public"
  assume_role_policy = data.aws_iam_policy_document.remediation_trust.json
}

data "aws_iam_policy_document" "remediation" {
  statement {
    actions   = ["s3:PutBucketPublicAccessBlock", "s3:GetBucketPublicAccessBlock",
                 "s3:PutBucketAcl", "s3:GetBucketAcl"]
    resources = ["arn:aws:s3:::*"]
  }
}

resource "aws_iam_role_policy" "remediation" {
  name   = "block-public-access"
  role   = aws_iam_role.remediation.id
  policy = data.aws_iam_policy_document.remediation.json
}

resource "aws_config_remediation_configuration" "s3_public_read" {
  config_rule_name = aws_config_config_rule.s3_public_read.name
  target_type      = "SSM_DOCUMENT"
  target_id        = "AWS-DisableS3BucketPublicReadWrite"

  parameter {
    name         = "AutomationAssumeRole"
    static_value = aws_iam_role.remediation.arn
  }
  parameter {
    name           = "S3BucketName"
    resource_value = "RESOURCE_ID"
  }

  automatic                  = true
  maximum_automatic_attempts = 3
  retry_attempt_seconds      = 60
}

# 4. EVIDENCE: AWS Config keeps the compliance history of every evaluation.
#    Export it for auditors with:
#    aws configservice get-compliance-details-by-config-rule \
#      --config-rule-name s3-bucket-public-read-prohibited --compliance-types NON_COMPLIANT COMPLIANT
