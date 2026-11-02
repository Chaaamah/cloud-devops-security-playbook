# Chapter 7 — Identity is the new perimeter

| File | Purpose |
| --- | --- |
| `policies/read-invoices-vpce.json` | Conditions turn a broad permission into a narrow one |
| `policies/scp-protect-security-tooling.json` | Nobody but the security platform role can blind you |
| `policies/scp-deny-unapproved-regions.json` | Only approved regions; global services and the org access role exempt |
| `policies/workload-permissions-boundary.json` | The maximum any application role can ever have |
| `policies/developer-role-creation.json` | Developers create roles only with that boundary attached |
| `policies/github-oidc-trust.json` | Trust policy for keyless CI |
| `terraform/github-oidc.tf` | The OIDC provider and a narrowly scoped deploy role |

## Lab 1 — Generate a policy from real activity

```bash
aws accessanalyzer start-policy-generation \
  --policy-generation-details principalArn=arn:aws:iam::111122223333:role/my-app-role \
  --cloud-trail-details '{
      "trails": [{"cloudTrailArn": "arn:aws:cloudtrail:eu-west-1:111122223333:trail/org-trail", "allRegions": true}],
      "accessRole": "arn:aws:iam::111122223333:role/AccessAnalyzerPolicyGeneration",
      "startTime": "2026-10-01T00:00:00Z"}'

aws accessanalyzer get-generated-policy --job-id <job-id-from-above>
```

Compare the generated actions with the role's current policy. Typical findings: wildcards (`s3:*`) where three actions are used, and whole services granted but never called. Replace the policy, keep the old version for a quick rollback, and watch for `AccessDenied` errors for a week.

## Lab 2 — Prove the guardrails

Attach both SCPs to a **test OU** containing a sandbox account. Then, as an administrator of that account:

```bash
aws cloudtrail stop-logging --name org-trail
aws ec2 describe-instances --region us-east-1
```

Both fail with `AccessDenied ... with an explicit deny in a service control policy`. The administrator has `AdministratorAccess`, which proves the point: an SCP caps what any identity policy grants.

The region SCP exempts global services and `OrganizationAccountAccessRole`. Review the `NotAction` list against the services your organization actually uses before attaching it to production.

## Lab 3 — Remove long-lived keys from CI

1. Find stored keys: repository and organization secrets named like `AWS_ACCESS_KEY_ID`, and leaked ones in history with a scanner such as gitleaks.
2. Apply `terraform/github-oidc.tf` with your repository and environment.
3. In the workflow, grant `permissions: id-token: write` and replace the secrets with `aws-actions/configure-aws-credentials` and `role-to-assume`.
4. Run the workflow; confirm in CloudTrail that the session is `AssumeRoleWithWebIdentity`.
5. Delete the old access keys: `aws iam delete-access-key --user-name ci-user --access-key-id AKIA...`, then delete the user.

The `sub` condition is the step that matters most. Test it: run the same workflow from another branch or environment, and the role assumption must fail.
