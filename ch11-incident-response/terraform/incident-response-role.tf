# Pre-approved role in every account, assumable only from the security account with MFA.
variable "security_account_id" {
  type = string
}

data "aws_iam_policy_document" "ir_trust" {
  statement {
    actions = ["sts:AssumeRole"]
    principals {
      type        = "AWS"
      identifiers = ["arn:aws:iam::${var.security_account_id}:role/IncidentResponder"]
    }
    condition {
      test     = "Bool"
      variable = "aws:MultiFactorAuthPresent"
      values   = ["true"]
    }
  }
}

resource "aws_iam_role" "incident_response" {
  name                 = "IncidentResponse"
  assume_role_policy   = data.aws_iam_policy_document.ir_trust.json
  max_session_duration = 14400
}

resource "aws_iam_role_policy_attachment" "read_everything" {
  role       = aws_iam_role.incident_response.name
  policy_arn = "arn:aws:iam::aws:policy/SecurityAudit"
}

data "aws_iam_policy_document" "containment" {
  statement {
    sid = "Contain"
    actions = [
      "ec2:CreateSnapshot", "ec2:CreateTags", "ec2:ModifyInstanceAttribute",
      "ec2:ModifySnapshotAttribute", "ec2:DisassociateIamInstanceProfile",
      "ec2:ReplaceNetworkAclAssociation", "ec2:CreateNetworkAcl", "ec2:CreateNetworkAclEntry",
      "iam:UpdateAccessKey", "iam:PutRolePolicy", "iam:AttachUserPolicy",
    ]
    resources = ["*"]
  }
}

resource "aws_iam_role_policy" "containment" {
  name   = "containment"
  role   = aws_iam_role.incident_response.id
  policy = data.aws_iam_policy_document.containment.json
}
