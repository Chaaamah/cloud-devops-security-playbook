# Chapter 12 — Governance, compliance and the capstone

| File | Purpose |
| --- | --- |
| `control-mapping.md` | Lab 1: ten controls mapped to ISO/IEC 27001:2022, SOC 2 and NIST CSF 2.0 |
| `terraform/s3-public-access-control.tf` | Lab 2: one control end to end, prevent, detect, remediate, evidence |
| `exception-template.yaml` | Policy exceptions as code, always with an expiry date |

## Lab 2 — One control, end to end

```bash
cd ch12-governance/terraform
terraform init && terraform apply -var account_id=<sandbox-account-id>
```

To test the remediation, temporarily remove the account-level block in the sandbox, create a bucket with a public-read ACL, and watch AWS Config mark it non-compliant and the SSM automation fix it within minutes. Restore the account-level block afterwards. The account block alone would have prevented the violation, which is exactly the point of layering prevention before detection.

## Lab 3 — The capstone

Build the platform described in section 12.3 of the book, using the folders of this repository as building blocks.

| Step | Build | Start from |
| --- | --- | --- |
| 1 | Organization, OUs, SCPs, log archive | `ch02-architecture`, `ch07-iam/policies` |
| 2 | Hub-and-spoke network, VPC endpoints | `ch02-architecture/README.md` IP plan |
| 3 | EKS from versioned modules, policy checks, drift detection | `ch03-iac` |
| 4 | CI with OIDC, SBOM, scanning, keyless signing | `ch05-cicd/release.yml`, `ch07-iam/terraform` |
| 5 | GitOps, canary releases | `ch03-iac/argocd`, `ch05-cicd` |
| 6 | Workload hardening and admission policies | `ch04-kubernetes`, `ch08-supply-chain/kyverno`, `ch09-container-security` |
| 7 | Observability and SLOs | `ch06-sre` |
| 8 | Logging, detections, runtime security | `ch10-detection`, `ch09-container-security/falco` |
| 9 | Playbooks and a game day against your own platform | `ch11-incident-response` |
| 10 | README with architecture, threat model, ADRs, game day postmortem | `ch10-detection/threat-model-capstone.md`, `ch02-architecture/adr-template.md` |

**Definition of done**

- [ ] Everything is created from code; nothing was clicked in the console
- [ ] No long-lived credential exists anywhere in the platform
- [ ] An unsigned image cannot run; a public bucket cannot exist
- [ ] Each detection in `ch10-detection` has been tested by emulation
- [ ] The game day postmortem lists at least one improvement you then made

Keep costs low: small instance types, one NAT gateway in the sandbox, and destroy the environment between sessions.
