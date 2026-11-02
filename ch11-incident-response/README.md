# Chapter 11 — Cloud incident response and forensics

| File | Purpose |
| --- | --- |
| `contain_instance.py` | Snapshot, protect, isolate and tag a compromised instance |
| `revoke_role_sessions.py` | Deny every session of a role issued before now |
| `test_containment.py` | Unit tests with fake AWS clients |
| `playbooks/leaked-access-key.md` | Lab 3 solution: the leaked-key runbook with exact commands |
| `playbooks/compromised-instance.md` | Instance containment runbook |
| `kubernetes/` | Pod quarantine guide and NetworkPolicy |
| `terraform/` | Quarantine security group and the pre-approved incident response role (lab 1) |

## Lab 1 — Prepare before the incident

Apply `terraform/quarantine.tf` in every VPC and `terraform/incident-response-role.tf` in every account, ideally through your account vending pipeline so new accounts get them automatically.

## Lab 2 — Run the containment script

Launch a throwaway instance in a sandbox account with one security group and one volume, then:

```bash
pytest ch11-incident-response                         # logic first, no AWS calls
python ch11-incident-response/contain_instance.py <instance-id> <quarantine-sg-id> IR-TEST-001
aws ec2 describe-instances --instance-ids <instance-id> \
  --query 'Reservations[0].Instances[0].[SecurityGroups,Tags]'
aws ec2 describe-snapshots --filters Name=tag:case,Values=IR-TEST-001
```

Check that the snapshots exist, the only security group is the quarantine group, termination protection is on, and the tags list the original groups.

## Lab 3 — Tabletop for a leaked key

Run the scenario as a team with `playbooks/leaked-access-key.md`. Time each step. The gaps you find (missing access, logs not retained long enough, nobody knows who approves customer communication) are the real output.

## Lab 4 — Revoke role sessions

```bash
aws sts assume-role --role-arn arn:aws:iam::<acct>:role/<test-role> --role-session-name before > creds.json
python ch11-incident-response/revoke_role_sessions.py <test-role>
# use the credentials from creds.json: every call now fails with an explicit deny
# assume the role again: the fresh session works
```

Remove the `AWSRevokeOlderSessions` inline policy when the incident is closed, or leave it: it only affects sessions older than its timestamp.
