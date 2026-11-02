# Chapter 10 — Threat modeling and detection engineering

| File | Purpose |
| --- | --- |
| `threat-model-capstone.md` | Lab 1: STRIDE threat model of the capstone, top five threats |
| `sigma/aws_cloudtrail_logging_tampering.yml` | T1562.008, from the chapter |
| `sigma/aws_iam_access_key_created.yml` | Lab 2: T1098.001, persistence through new access keys |
| `sigma/aws_snapshot_shared_externally.yml` | Lab 2: T1537, exfiltration by sharing EBS or RDS snapshots |

## Lab 2 — Detections as code

Validate and convert the rules with the Sigma CLI. Install the backend for your SIEM as a plugin:

```bash
pip install sigma-cli
sigma check ch10-detection/sigma/                      # run this in CI on every pull request
sigma plugin list                                      # find your SIEM's backend
sigma plugin install splunk                            # example
sigma convert -t splunk ch10-detection/sigma/
```

Real CloudTrail field names sometimes differ between log pipelines. If your SIEM renames fields, add a processing pipeline (`-p`) rather than editing the rules, so the rules stay portable.

## Lab 3 — Emulate, then measure time to detect

In a dedicated, authorized test account, use [Stratus Red Team](https://github.com/DataDog/stratus-red-team):

```bash
stratus detonate aws.defense-evasion.cloudtrail-stop        # T1562.008
stratus detonate aws.persistence.iam-backdoor-user          # T1098.001
stratus detonate aws.exfiltration.ec2-share-ebs-snapshot    # T1537
stratus cleanup --all
```

For each technique, record in a table: detonation time, alert time, whether the right rule fired, and whether an analyst could act on the alert as written. The CloudTrail stop should **fail** if the Chapter 7 SCP is attached; the detection should still fire on the attempt.

## Coverage tracking

| ATT&CK technique | Detection | Emulation test | Status |
| --- | --- | --- | --- |
| T1562.008 Disable or Modify Cloud Logs | `aws_cloudtrail_logging_tampering.yml` | `aws.defense-evasion.cloudtrail-stop` | |
| T1098.001 Additional Cloud Credentials | `aws_iam_access_key_created.yml` | `aws.persistence.iam-backdoor-user` | |
| T1537 Transfer Data to Cloud Account | `aws_snapshot_shared_externally.yml` | `aws.exfiltration.ec2-share-ebs-snapshot` | |
| T1552.005 Cloud Instance Metadata API | Falco rule in `ch09-container-security` | `curl 169.254.169.254` from a pod | |

Fill in the status column after each test run: *tested*, *fires late*, *missing*. The empty rows are your detection backlog.
