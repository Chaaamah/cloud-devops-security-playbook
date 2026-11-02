# Playbook — Compromised EC2 instance

**Trigger:** GuardDuty finding (for example crypto mining or command-and-control traffic), Falco alert on a node, or an unexpected outbound connection.

## 1. Preserve, then isolate (target: 30 minutes)

```bash
python ch11-incident-response/contain_instance.py i-0abc... sg-quarantine... IR-2026-014
```

The script snapshots every volume, enables termination protection, swaps the security groups for the quarantine group and tags the instance with what it changed.

Then:

1. **Cut established connections** if needed: associate the subnet with a deny-all network ACL, or move the instance's network interface into an isolated subnet. Changing security groups alone does not always end tracked connections.
2. **Remove its cloud permissions:** detach the instance profile, then revoke sessions of its role with `revoke_role_sessions.py`, since stolen temporary credentials stay valid otherwise.
3. **Memory:** if the case justifies it, capture memory before any shutdown, through the instance management agent and a memory acquisition tool. Memory is lost on stop.

## 2. Analyse in the forensic account

- Share the snapshots with the forensic account, create volumes from them and attach them **read-only** to an analysis instance.
- Hash every artifact at collection (SHA-256) and record who collected what, when and how.
- Build one UTC timeline from CloudTrail, VPC Flow Logs, DNS logs and the disk.

## 3. Eradicate and recover

Do not clean the instance: rebuild it from known-good infrastructure code and a patched image. Rotate secrets it could reach, watch for the attacker's indicators, and restore traffic gradually.
