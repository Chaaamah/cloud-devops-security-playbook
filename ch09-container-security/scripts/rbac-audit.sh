#!/usr/bin/env bash
# Lab 4 companion: quick RBAC review of a cluster.
set -euo pipefail

echo "== Subjects bound to cluster-admin =="
kubectl get clusterrolebindings -o json | jq -r '
  .items[] | select(.roleRef.name == "cluster-admin")
  | .metadata.name as $b | (.subjects // [])[] | "\($b): \(.kind) \(.namespace // "-")/\(.name)"'

echo; echo "== Roles and ClusterRoles with wildcard verbs or resources =="
kubectl get clusterroles,roles -A -o json | jq -r '
  .items[] | select(.metadata.name | startswith("system:") | not)
  | select([.rules[]? | (.verbs // []) + (.resources // []) | .[]] | index("*"))
  | "\(.kind) \(.metadata.namespace // "-")/\(.metadata.name)"'

echo; echo "== Who can read Secrets in every namespace (list/watch reveals all values) =="
kubectl get clusterroles -o json | jq -r '
  .items[] | select(.metadata.name | startswith("system:") | not)
  | select([.rules[]? | select((.resources // []) | index("secrets") or index("*"))
            | (.verbs // [])[] | select(. == "list" or . == "watch" or . == "*")] | length > 0)
  | .metadata.name'
