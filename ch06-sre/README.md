# Chapter 6 — Observability and SRE

| File | Purpose |
| --- | --- |
| `error_budget.py` | Error budget, burn rate and alert thresholds for any SLO (with tests) |
| `slo-rules.yaml` | Recording rules and three-tier burn-rate alerts for Prometheus |
| `otel-collector.yaml` | Collector with personal-data scrubbing and tail-based sampling |
| `postmortem-template.md` | Blameless postmortem template |

## Lab 1 — SLIs, SLO and error budget

Example for checkout:

- **Availability SLI:** share of checkout requests that return a non-5xx status.
- **Latency SLI:** share of checkout requests served in under 300 ms.
- **SLO:** 99.9% for availability and 99% for latency, over a rolling 30 days.

```bash
python ch06-sre/error_budget.py --slo 99.9 --requests 12000000 --error-rate 0.5
```

```text
SLO 99.9% over 30 days
  error budget: 43.2 minutes of full downtime (0.72 hours)
  error budget: 12,000 failed requests out of 12,000,000
  ...
  at 0.5% errors: burn rate 5.0, budget gone in 144.0 hours
```

## Lab 2 — Test the fast-burn alert

Load `slo-rules.yaml` into Prometheus (for kube-prometheus-stack, wrap it in a `PrometheusRule` resource). Then inject errors with a fault-injection tool, or with Chaos Mesh's `HTTPChaos` replacing a share of responses with 500s. The page should fire within about 5 minutes of the error rate passing 1.44%. Check `promtool check rules ch06-sre/slo-rules.yaml` before loading.

## Lab 3 — Tail-based sampling

Run `otel/opentelemetry-collector-contrib` with `otel-collector.yaml`. Send traces with a load generator; in your backend, every trace with an error or slower than one second is present, and about 5% of the healthy ones.

## Lab 4 — Game day

Plan it before you run it:

1. **Steady state:** the SLO dashboard is green.
2. **Hypothesis:** "losing one node at peak load keeps checkout within its SLO".
3. **Blast radius and abort:** one node, staging first; abort if the error ratio passes 1%.
4. **Run:** terminate the node, observe alerts, dashboards and autoscaling.
5. **Write it up** with `postmortem-template.md`, even if everything went well.
