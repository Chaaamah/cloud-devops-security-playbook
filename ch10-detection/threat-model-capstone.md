# Threat model — capstone platform (lab 1)

**System:** the Chapter 12 capstone: a multi-account AWS organization, EKS clusters per environment, GitHub Actions with OIDC, Argo CD, signed images, centralized logs.

**Trust boundaries:**
1. Internet → public load balancer → checkout service
2. GitHub (CI) → AWS through OIDC role assumption
3. Git (GitOps repository) → Argo CD inside the cluster
4. Workload accounts → log archive account (write-only)
5. Pods → cloud APIs through pod identity

## Top five threats

| # | Threat | STRIDE | Where | Mitigations already in the platform | Residual risk and next step |
| --- | --- | --- | --- | --- | --- |
| 1 | A malicious pull request makes CI deploy attacker code | Spoofing, Tampering | Boundary 2 | OIDC `sub` bound to the production environment; protected environment with reviewers; untrusted input never interpolated into scripts (Ch. 5, 7) | Compromised maintainer account. Add required reviews from CODEOWNERS on workflow files |
| 2 | An unsigned or swapped image reaches production | Tampering | Boundary 3 | Keyless signing in CI, Kyverno verification at admission, deploy by digest (Ch. 8) | Kyverno outage blocks deploys. Run it highly available and alert on webhook failures |
| 3 | A compromised pod steals node or cloud credentials | Elevation of privilege, Information disclosure | Boundary 5 | Restricted Pod Security, IMDSv2 hop limit 1, per-pod identities, Falco metadata rule (Ch. 9) | Over-broad pod role. Generate its policy from activity (Ch. 7, lab 1) |
| 4 | An attacker with valid credentials disables logging to hide | Repudiation | Boundary 4 | SCP denies CloudTrail changes; log archive write-once with Object Lock; Sigma rule on attempts (Ch. 7, 10) | Detection depends on the SIEM pipeline. Alert when log ingestion volume drops |
| 5 | Data exfiltration by sharing snapshots or copying buckets | Information disclosure | Boundary 4 and egress | Resource policies with `aws:PrincipalOrgID`, centralized egress allow-lists, Sigma rule for snapshot sharing (Ch. 2, 7, 10) | Exfiltration through allowed SaaS domains. Add data-loss prevention on egress |

**Review date:** whenever a trust boundary changes, and at least once a year.
