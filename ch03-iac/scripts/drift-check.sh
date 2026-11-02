#!/usr/bin/env bash
# Nightly drift detection: plan every stack and report the ones that drifted.
# usage: drift-check.sh stacks/payments/network stacks/payments/database ...
# Exit code 0 = no drift, 1 = drift found, 2 = a plan failed.
set -uo pipefail

drifted=()
failed=()

for stack in "$@"; do
  echo "::group::${stack}"
  terraform -chdir="${stack}" init -input=false -lock=false >/dev/null
  terraform -chdir="${stack}" plan -input=false -lock=false -detailed-exitcode -no-color > "${stack}/drift.txt"
  code=$?
  echo "::endgroup::"
  case $code in
    0) echo "OK      ${stack}" ;;
    2) echo "DRIFT   ${stack}"; drifted+=("${stack}") ;;
    *) echo "FAILED  ${stack}"; failed+=("${stack}") ;;
  esac
done

if ((${#failed[@]})); then
  echo "Plans failed: ${failed[*]}"; exit 2
fi
if ((${#drifted[@]})); then
  echo "Drift found in: ${drifted[*]} (see drift.txt in each stack)"; exit 1
fi
echo "No drift."
