# Chapter 9 — Container and Kubernetes security

```text
ch09-container-security/
├── app/                  # tiny Go service, a hardened Dockerfile and a naive one
├── k8s/                  # restricted namespace, hardened Deployment, External Secrets
├── falco/                # custom runtime detection rule
└── scripts/rbac-audit.sh # who is cluster-admin, wildcard roles, who can read Secrets
```

## Lab 1 — Distroless vs naive image

```bash
cd ch09-container-security/app
docker build -t checkout:naive -f Dockerfile.naive .
docker build -t checkout:hardened .
docker images checkout
grype checkout:naive    | tail -n +2 | wc -l
grype checkout:hardened | tail -n +2 | wc -l
docker run --rm --entrypoint sh checkout:hardened   # fails: there is no shell to abuse
```

The naive image carries a full Go toolchain and Debian userland, so it is several hundred megabytes with many findings. The hardened image is a few megabytes and runs as a non-root user.

## Lab 2 — Make a namespace `restricted`

Preview first. A server-side dry run lists every pod that would violate the new level, without changing anything:

```bash
kubectl label --dry-run=server --overwrite ns payments pod-security.kubernetes.io/enforce=restricted
```

Fix each workload (usually: `runAsNonRoot`, `seccompProfile`, `allowPrivilegeEscalation: false`, `capabilities.drop: [ALL]`; see `k8s/deployment-hardened.yaml`), then apply `k8s/namespace-restricted.yaml`.

## Lab 3 — Runtime detection with Falco

```bash
helm repo add falcosecurity https://falcosecurity.github.io/charts
helm install falco falcosecurity/falco -n falco --create-namespace \
  --set driver.kind=modern_ebpf \
  --set-file customRules."acme-rules\.yaml"=ch09-container-security/falco/custom-rules.yaml \
  --set falcosidekick.enabled=true \
  --set falcosidekick.config.slack.webhookurl="https://hooks.slack.com/services/XXX"   # your webhook

kubectl run probe --rm -it --restart=Never --image=curlimages/curl -- \
  curl -s -m 2 http://169.254.169.254/latest/meta-data/ || true
kubectl -n falco logs -l app.kubernetes.io/name=falco | grep "Metadata service"
```

On AWS, also block the path itself: require IMDSv2 with a hop limit of 1 on nodes, so pods cannot reach node credentials at all. Detection tells you someone tried; the hop limit makes the attempt fail.

## Lab 4 — CIS benchmark

```bash
kubectl apply -f https://raw.githubusercontent.com/aquasecurity/kube-bench/main/job.yaml
kubectl logs job/kube-bench | grep -E "^\[FAIL\]" | head -20
bash ch09-container-security/scripts/rbac-audit.sh
```

Track each `[FAIL]` like a vulnerability: owner, fix or accepted exception with an expiry date. On managed clusters some checks cover the control plane you cannot touch; use the provider-specific benchmark profile where kube-bench has one (the EKS and GKE profiles are listed in the kube-bench documentation).
