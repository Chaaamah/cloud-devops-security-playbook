# Chapter 8 — Securing the software supply chain

| File | Purpose |
| --- | --- |
| `prioritize_findings.py` | Ranks scanner findings by KEV, EPSS and severity into FIX NOW, PLAN, WATCH (with tests) |
| `scripts/sbom-and-scan.sh` | SBOM, scan with VEX, prioritization, CI gate |
| `scripts/verify-image.sh` | Verify signature and SBOM attestation of an image |
| `kyverno/require-signed-images.yaml` | Admission policy: only images signed by the release workflow |
| `vex/openvex.json` | Example VEX statement for a finding analysed as not exploitable |
| `../ch05-cicd/release.yml` | The pipeline that builds, scans, signs and attests |

## Lab 1 — SBOM, gate and prioritization

```bash
bash ch08-supply-chain/scripts/sbom-and-scan.sh ghcr.io/<you>/<app>@sha256:<digest>
```

A typical result on a real image: dozens of findings, of which only a handful land in **FIX NOW** (in the KEV catalog, or with a high EPSS score and a fix available). Fix those today, schedule PLAN within your service-level target, and let WATCH ride with the next base-image update. When you analyse a finding and prove it is not exploitable in your context, record it in `vex/openvex.json` so nobody triages it again.

## Lab 2 — Keyless signing and verification

Use `ch05-cicd/release.yml` in a test repository: it signs with Sigstore through the job's OIDC identity, with no key to manage. Then, from your laptop:

```bash
bash ch08-supply-chain/scripts/verify-image.sh ghcr.io/<you>/<app>@sha256:<digest> <you>/<app>
```

Try verifying with a wrong `--certificate-identity`, for example another branch: verification fails. That identity check is what makes a signature meaningful.

## Lab 3 — Enforce signatures at admission

```bash
helm repo add kyverno https://kyverno.github.io/kyverno/
helm install kyverno kyverno/kyverno -n kyverno --create-namespace --wait
# edit imageReferences and subject to your registry and repository, set failureAction: Audit
kubectl apply -f ch08-supply-chain/kyverno/require-signed-images.yaml
kubectl get policyreports -A                         # review violations for a few days
# switch to failureAction: Enforce, then prove it:
kubectl run unsigned --image=ghcr.io/<you>/<app>:unsigned   # rejected by the admission webhook
```

Run Kyverno with at least 3 replicas in production, and monitor it: with a fail-closed webhook, an outage of the policy engine blocks every deployment, including the fix.

## Tests

```bash
pytest ch08-supply-chain
```
