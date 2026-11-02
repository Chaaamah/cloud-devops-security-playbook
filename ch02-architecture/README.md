# Chapter 2 — Cloud architecture at scale

Files: `adr-template.md`, `adr-012-centralized-egress.md` (the chapter's example) and the lab solutions below.

## Lab 1 — OU and account structure for a fintech

Context: three products (payments, lending, savings), a data platform and a security team.

```text
Root
├── Security OU
│   ├── log-archive            # organization CloudTrail, Config, flow logs; write-once
│   └── security-tooling       # GuardDuty/Security Hub delegated admin, SIEM, forensics
├── Infrastructure OU
│   ├── network-hub            # Transit Gateway, inspection, NAT, Route 53 resolver
│   └── shared-services        # CI runners, artifact registry, internal DNS
├── Workloads OU
│   ├── Production OU
│   │   ├── payments-prod
│   │   ├── lending-prod
│   │   ├── savings-prod
│   │   └── data-platform-prod
│   └── Non-production OU
│       ├── payments-staging, lending-staging, savings-staging
│       └── data-platform-staging
├── Sandbox OU                 # one per engineer, budget-capped, no production data
└── Suspended OU               # deny-all SCP, kept for audit before closure
```

Why these boundaries:

- **One account per product and environment** limits the blast radius of a leaked credential and makes costs attributable without tagging gymnastics.
- **Payments sits alone** because card data brings PCI DSS scope. Keeping it in its own accounts keeps lending and savings out of that audit scope.
- **The data platform has its own accounts** because it reads from every product. It gets read-only, cross-account access to specific exports, never the reverse.
- **Log archive is separate from security tooling**: analysts can query logs but nobody, including the security team, can delete them.

## Lab 2 — Hub-and-spoke IP plan with room for four more regions

Allocate from `10.0.0.0/8`: one /12 per region, one /14 per environment inside it, one /20 per account VPC.

| Region | Region block | Environment | Environment block | Example VPCs (/20 each) |
| --- | --- | --- | --- | --- |
| eu-west-1 (primary) | 10.16.0.0/12 | Production | 10.16.0.0/14 | payments 10.16.0.0/20, data 10.16.16.0/20, lending 10.16.32.0/20, savings 10.16.48.0/20 |
| | | Non-production | 10.20.0.0/14 | payments-stg 10.20.0.0/20, lending-stg 10.20.16.0/20, ... |
| | | Shared | 10.24.0.0/14 | hub 10.24.0.0/20, shared-services 10.24.16.0/20 |
| | | Reserved | 10.28.0.0/14 | growth |
| eu-west-3 (DR) | 10.32.0.0/12 | same pattern | | |
| Future regions 3 to 6 | 10.48.0.0/12, 10.64.0.0/12, 10.80.0.0/12, 10.96.0.0/12 | reserved | | |

Each /14 holds 64 VPCs of /20 (4,096 addresses each). Record every allocation in an IPAM tool, such as Amazon VPC IPAM, and never hand out addresses from a spreadsheet.

## Lab 3 — Payments: RTO 15 minutes, RPO 1 minute

- **Strategy: warm standby** in a second region. Backup-and-restore cannot meet a 15-minute RTO, and pilot light usually cannot either once DNS changes, scaling and validation are counted. Active-active would meet it but costs roughly double and adds write-conflict complexity that payments rarely needs.
- **Data:** a database with cross-region replication measured in seconds (for example Aurora Global Database), which meets a 1-minute RPO with margin.
- **Compute:** a scaled-down copy of the services always running in the DR region, scaled up by automation during failover.
- **Traffic:** DNS failover with health checks and a low TTL.

**Estimating the monthly cost:** list the DR region's always-on resources (replica database instances, minimum task or node count, NAT, load balancers), add cross-region replication transfer per GB, and price them in the AWS Pricing Calculator. Express the result as a share of the primary region's cost, then compare it with what one hour of payment downtime costs the business. That comparison, not the raw number, is what justifies the decision.

Write the decision with `adr-template.md`. A strong ADR states the measured RTO from the last failover drill, not the hoped-for one.
