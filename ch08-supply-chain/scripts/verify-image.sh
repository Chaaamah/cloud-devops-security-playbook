#!/usr/bin/env bash
# Lab 2: verify who built an image and from which workflow, from your laptop.
# usage: verify-image.sh ghcr.io/<owner>/<repo>@sha256:<digest> <owner>/<repo>
set -euo pipefail
IMAGE="$1"
REPO="$2"

cosign verify "$IMAGE" \
  --certificate-identity "https://github.com/${REPO}/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  | jq '.[0].optional | {Issuer, Subject, githubWorkflowRepository, githubWorkflowSha}'

cosign verify-attestation "$IMAGE" --type cyclonedx \
  --certificate-identity "https://github.com/${REPO}/.github/workflows/release.yml@refs/heads/main" \
  --certificate-oidc-issuer "https://token.actions.githubusercontent.com" \
  > /dev/null && echo "SBOM attestation verified"
