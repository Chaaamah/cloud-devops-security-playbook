# Chapter 4 — Kubernetes in production

## Lab cluster

```bash
kind create cluster --name lab --config ch04-kubernetes/kind-config.yaml
helm repo add cilium https://helm.cilium.io
helm install cilium cilium/cilium -n kube-system --wait     # enforces NetworkPolicies
kubectl apply -f ch04-kubernetes/priority-classes.yaml
kubectl apply -f ch04-kubernetes/checkout.yaml
kubectl -n payments get pods -o wide                         # 2 pods per zone
```

## Lab 1 — Drain a node and keep 4 replicas

```bash
NODE=$(kubectl get nodes -l topology.kubernetes.io/zone=zone-a -o name | head -1)
kubectl drain "$NODE" --ignore-daemonsets --delete-emptydir-data
kubectl -n payments get pods -o wide
kubectl -n payments get pdb checkout
kubectl uncordon "$NODE"
```

What you will see: the drain evicts the 2 pods of zone-a, and the PodDisruptionBudget lets it because 4 remain available. The 2 replacements stay **Pending**: with `whenUnsatisfiable: DoNotSchedule`, placing them in zone-b or zone-c would break the `maxSkew: 1` rule. After `uncordon` they start in zone-a again.

That is a deliberate trade-off. `DoNotSchedule` guarantees zone spread but can leave capacity unused during an incident; `ScheduleAnyway` keeps all replicas running but may stack them in fewer zones.

## Lab 2 — Default deny and prove it

```bash
kubectl apply -f ch04-kubernetes/network-policies.yaml
kubectl create namespace frontend
kubectl create namespace other

# Allowed: frontend -> checkout
kubectl -n frontend run probe --rm -it --restart=Never --image=curlimages/curl -- \
  curl -s -m 3 -o /dev/null -w "%{http_code}\n" http://checkout.payments

# Blocked: any other namespace -> checkout (times out)
kubectl -n other run probe --rm -it --restart=Never --image=curlimages/curl -- \
  curl -s -m 3 -o /dev/null -w "%{http_code}\n" http://checkout.payments || echo "blocked, as expected"
```

## Lab 3 — Watch autoscaling

```bash
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm install metrics-server metrics-server/metrics-server -n kube-system --set args={--kubelet-insecure-tls}
kubectl apply -f ch04-kubernetes/hpa.yaml

kubectl -n frontend run load --restart=Never --image=busybox -- \
  /bin/sh -c "while true; do wget -q -O- http://checkout.payments >/dev/null; done"
kubectl -n payments get hpa checkout -w
```

kind has no node autoscaler, so new pods that do not fit stay `Pending`. On EKS with Karpenter, measure the time from the first `Pending` pod to its `Running` state: that delay is why the capacity buffer in `priority-classes.yaml` exists.

## Tenant namespaces

`tenant-baseline.yaml` is the complete baseline from section 4.5: Pod Security labels, RBAC for the team's group, quota, default limits and default deny.
