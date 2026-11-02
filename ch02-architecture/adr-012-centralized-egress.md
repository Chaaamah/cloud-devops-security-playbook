# ADR-012: Centralize internet egress through the network hub

Status: Accepted (2026-03-04)

## Context
Workload accounts each run their own NAT gateways. We cannot inspect outbound traffic,
and NAT costs are duplicated across 40 accounts.

## Decision
Remove internet gateways from spokes. Route 0.0.0.0/0 to the Transit Gateway;
egress through inspected NAT in the hub account.

## Consequences
+ One place to enforce domain allow-lists and detect exfiltration.
+ Lower total NAT cost.
- The hub becomes critical: deploy it in every AZ and monitor it closely.
- Added latency of about one network hop.
