#!/usr/bin/env bash
# Lab 1: SBOM for an image, vulnerability scan, prioritization.
# usage: sbom-and-scan.sh ghcr.io/acme/checkout@sha256:<digest>
set -euo pipefail
IMAGE="$1"
HERE="$(cd "$(dirname "$0")/.." && pwd)"

syft "$IMAGE" -o cyclonedx-json > sbom.cdx.json
echo "SBOM: $(grep -o '"bom-ref"' sbom.cdx.json | wc -l) components"

# Use a VEX document to suppress findings you have analysed as not exploitable.
VEX_ARGS=()
[[ -f "$HERE/vex/openvex.json" ]] && VEX_ARGS=(--vex "$HERE/vex/openvex.json")
grype "sbom:sbom.cdx.json" "${VEX_ARGS[@]}" -o json > findings.json

curl -sSLo kev.json https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json
curl -sSL https://epss.cyentia.com/epss_scores-current.csv.gz | gunzip > epss.csv
python3 "$HERE/prioritize_findings.py" findings.json kev.json epss.csv

# The CI gate: fail on high or critical findings (keep this in the pipeline)
grype "sbom:sbom.cdx.json" "${VEX_ARGS[@]}" --fail-on high
