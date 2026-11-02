# Playbook — Leaked or misused IAM access key

**Trigger:** GuardDuty finding, secret-scanning alert, or a key used from an unexpected country or ASN.
**Severity:** SEV2 by default; SEV1 if production data or IAM changes are involved.

## 1. Contain (target: 15 minutes)

```bash
KEY=AKIA...; USER=$(aws iam list-access-keys --query "AccessKeyMetadata[?AccessKeyId=='$KEY'].UserName" --output text)
# If USER is empty, the key belongs to another account: aws sts get-access-key-info --access-key-id $KEY

aws iam update-access-key --user-name "$USER" --access-key-id "$KEY" --status Inactive
```

Deactivate, do **not** delete: the key ID ties together all of its activity in the logs.

## 2. Scope (target: 1 hour)

```bash
aws cloudtrail lookup-events --lookup-attributes AttributeKey=AccessKeyId,AttributeValue=$KEY \
  --start-time "$(date -u -d '-30 days' +%FT%TZ)" --max-results 50 \
  --query 'Events[].[EventTime,EventName,EventSource]' --output table
```

`lookup-events` only covers 90 days of management events in one region. For the full picture, query the organization trail in the log archive (Athena or the SIEM), all regions.

Look for **persistence** first:

- `CreateUser`, `CreateAccessKey`, `CreateLoginProfile`, `UpdateLoginProfile`
- `AttachUserPolicy`, `PutUserPolicy`, `AttachRolePolicy`, `UpdateAssumeRoleTrustPolicy`
- `CreateFunction`, `UpdateFunctionCode`, `CreateEventSourceMapping`, scheduled rules
- `RunInstances` (cryptomining), `ModifySnapshotAttribute` (exfiltration)

## 3. Eradicate

- Remove every persistence mechanism found; revoke sessions of any role the key could assume (`revoke_role_sessions.py`).
- Rotate every secret the user could read.
- Find how the key leaked (repository, CI log, laptop) and close that path.

## 4. Recover and learn

- Replace the IAM user with role-based access (SSO for humans, OIDC for CI). The best fix for a leaked long-lived key is not having one.
- Write the postmortem (`ch06-sre/postmortem-template.md`), add a detection for whatever was missed.
