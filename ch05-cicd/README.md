# Chapter 5 — CI/CD and release engineering

| File | Purpose |
| --- | --- |
| `release.yml` | Build once, SBOM, vulnerability gate, keyless signing, promotion by digest |
| `rollout.yaml` | Argo Rollouts canary for the Chapter 4 checkout Deployment, plus stable and canary Services |
| `analysis-template.yaml` | Automated success-rate analysis (app metrics, or ingress-nginx metrics) |
| `pipeline-hardening-checklist.md` | Lab 3 audit checklist |

## Lab 1 — Convert the Deployment into a canary Rollout

```bash
kubectl create namespace argo-rollouts
kubectl apply -n argo-rollouts -f https://github.com/argoproj/argo-rollouts/releases/latest/download/install.yaml
kubectl apply -f ch05-cicd/analysis-template.yaml
kubectl apply -f ch05-cicd/rollout.yaml
kubectl argo rollouts get rollout checkout -n payments --watch
```

`workloadRef` lets the Rollout take over the existing Deployment's pod template: you migrate without rewriting manifests, and `scaleDown: progressively` hands traffic over gradually.

## Lab 2 — A broken release that rolls itself back

You need traffic, a router and metrics:

1. Install ingress-nginx with metrics enabled, and kube-prometheus-stack in the `monitoring` namespace.
2. Expose `checkout-stable` through an Ingress and add the `trafficRouting.nginx.stableIngress` field to the Rollout's canary strategy, so weights become exact.
3. Switch the analysis step to the `success-rate-ingress` template.
4. Send steady traffic, then release a broken version. The Argo Rollouts demo images are convenient: `argoproj/rollouts-demo:blue` is healthy and `argoproj/rollouts-demo:bad-red` returns errors.

The demo images run as root, which the `restricted` Pod Security level of the `payments` namespace rejects. For this lab, add `runAsUser: 1000` to the Deployment's pod `securityContext` (the demo binary runs fine as any user). Then release by changing the Deployment, because the Rollout reads its pod template from there:

```bash
kubectl -n payments set image deployment/checkout app=argoproj/rollouts-demo:blue      # healthy baseline
kubectl -n payments set image deployment/checkout app=argoproj/rollouts-demo:bad-red   # broken release
kubectl argo rollouts get rollout checkout -n payments --watch
```

The analysis measures the canary's success rate, fails, and the rollout status becomes **Degraded**: traffic returns to the stable version with no human action. Run `kubectl argo rollouts abort` or fix the image to continue.

## Lab 3 — Audit a pipeline

Work through `pipeline-hardening-checklist.md` on a real repository. Untrusted input is the gap most often found: for example `run: echo "${{ github.event.pull_request.title }}"` lets a malicious title run shell commands. The fix is to pass it through `env:` and quote the variable.
