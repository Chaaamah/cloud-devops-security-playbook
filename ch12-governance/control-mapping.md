# Control mapping (lab 1)

One control, implemented once, satisfies several frameworks. This table maps ten controls built in the book to ISO/IEC 27001:2022 Annex A, the SOC 2 Trust Services Criteria (common criteria) and NIST CSF 2.0.

> The mapping is indicative. Auditors interpret scope and wording; confirm against the current framework text and with your auditor before relying on it.

| # | Control in this book | Chapter | ISO/IEC 27001:2022 | SOC 2 | NIST CSF 2.0 |
| --- | --- | --- | --- | --- | --- |
| 1 | SSO for humans, OIDC for CI, no long-lived keys | 7 | A.5.16, A.5.17, A.8.5 | CC6.1, CC6.2 | PR.AA-01, PR.AA-03 |
| 2 | Least privilege from observed activity, permission boundaries | 7 | A.5.15, A.5.18, A.8.2 | CC6.3 | PR.AA-05 |
| 3 | Encryption at rest with KMS, TLS-only buckets | 3 | A.8.24 | CC6.1, CC6.7 | PR.DS-01, PR.DS-02 |
| 4 | Network segmentation, default-deny policies, inspected egress | 2, 4 | A.8.20, A.8.22 | CC6.6 | PR.IR-01 |
| 5 | Infrastructure as code, policy checks, drift detection | 3 | A.8.9, A.8.32 | CC8.1, CC7.1 | PR.PS-01 |
| 6 | Signed builds, SBOMs, vulnerability gate | 5, 8 | A.8.8, A.8.25, A.8.28 | CC7.1, CC8.1 | ID.RA-01, PR.PS-06 |
| 7 | Centralized, immutable audit logs | 10 | A.8.15 | CC7.2 | PR.PS-04, DE.CM-01 |
| 8 | Detections as code, runtime security | 9, 10 | A.8.16 | CC7.2, CC7.3 | DE.CM-09, DE.AE-02 |
| 9 | Incident playbooks, evidence collection, postmortems | 6, 11 | A.5.24, A.5.26, A.5.28 | CC7.4, CC7.5 | RS.MA-01, RC.RP-01 |
| 10 | Backups and tested regional failover | 2 | A.8.13, A.5.30 | A1.2, A1.3 | PR.DS-11, RC.RP-01 |

**How to use it:** for each row, store the evidence once (a configuration rule result, a pipeline log, a test report, a postmortem) and tag it with every framework reference in the table. During an audit, one query per framework returns the evidence.
