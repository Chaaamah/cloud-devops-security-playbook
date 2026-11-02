# Quarantining a compromised pod without destroying evidence

NetworkPolicies are **additive**: a deny-all policy does not cancel other policies that
already allow traffic to the pod. Isolation therefore works by taking the pod *out of*
its normal policies, then applying one that matches nothing but the quarantine label.

```bash
NS=payments; POD=checkout-7d9f8b6c5-x2k4q

# 1. Detach the pod from its Deployment, Service and allow policies by changing its app label.
#    The ReplicaSet starts a clean replacement; the suspect pod keeps running, untouched.
kubectl -n $NS label pod $POD app=quarantined quarantine=true --overwrite

# 2. Deny all traffic to and from pods carrying the quarantine label.
kubectl -n $NS apply -f quarantine-networkpolicy.yaml

# 3. Stop new pods landing on the same node, then collect evidence.
mkdir -p evidence
kubectl cordon "$(kubectl -n $NS get pod $POD -o jsonpath='{.spec.nodeName}')"
kubectl -n $NS get pod $POD -o yaml > evidence/$POD.yaml
kubectl -n $NS logs $POD --all-containers > evidence/$POD.log
sha256sum evidence/* > evidence/SHA256SUMS
```

Avoid `kubectl debug` on the suspect pod unless the case requires it: it adds an ephemeral container to the pod spec, which changes the evidence, and a root debug image is rejected by the `restricted` Pod Security level anyway. Prefer node-level collection from the snapshot.

Snapshot the node's disk from the cloud console or CLI before deleting anything.
