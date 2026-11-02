# Chapter 3 — Infrastructure as code at scale

```text
ch03-iac/
├── modules/secure-bucket/     # private, versioned, KMS-encrypted, TLS-only bucket + tests
├── examples/invoices/         # a root module consuming the module (lab 1)
├── policy/                    # Rego policies and their unit tests (lab 2)
├── ci/terraform-pr.yml        # pull-request pipeline: fmt, validate, test, plan, conftest
├── scripts/drift-check.sh     # nightly drift detection (lab 3)
└── argocd/                    # GitOps applications (lab 4)
```

## Lab 1 — Module, release tag, consumer

```bash
cd ch03-iac/modules/secure-bucket
terraform init && terraform test              # 4 runs, no AWS credentials needed

cd ../../examples/invoices
terraform init && terraform plan              # needs credentials for your sandbox account
```

To consume the module by version, tag this repository (`git tag v1.0.0 && git push --tags`) and switch the `source` in `examples/invoices/main.tf` to the commented `git::` line. Consumers then upgrade deliberately by changing `?ref=`.

The module goes further than the book's snippet: it disables ACLs with `BucketOwnerEnforced`, denies any request without TLS, expires old versions only when asked, and **refuses to plan** if the `owner`, `environment` or `data_class` tag is missing.

## Lab 2 — Policy checks that block a merge

```bash
opa test ch03-iac/policy -v                    # unit tests of the policies themselves
cd ch03-iac/examples/invoices
terraform plan -out=plan.out && terraform show -json plan.out > plan.json
conftest test plan.json --policy ../../policy
```

To prove the gate works, set `block_public_policy = false` in the module and plan again: conftest prints the deny message and exits 1, which fails the pull request in `ci/terraform-pr.yml`. Restore the value afterwards.

## Lab 3 — Detect drift

1. Apply the example, then change the bucket by hand in the console: for example, suspend versioning.
2. Run `bash ch03-iac/scripts/drift-check.sh ch03-iac/examples/invoices`.
3. The script exits 1 and `drift.txt` shows the difference. Decide: update the code if the change was right, or apply to revert it if it was not.

Schedule the script nightly in CI and open a ticket on exit code 1.

## Lab 4 — Watch GitOps self-heal

```bash
kind create cluster --name gitops
helm repo add argo https://argoproj.github.io/argo-helm
helm install argocd argo/argo-cd -n argocd --create-namespace --wait
kubectl apply -f ch03-iac/argocd/lab-guestbook-application.yaml

kubectl -n guestbook get deploy -w            # wait for guestbook-ui to appear
kubectl -n guestbook delete deploy guestbook-ui
kubectl -n guestbook get deploy -w            # Argo CD recreates it within moments
```

Try `kubectl -n guestbook scale deploy guestbook-ui --replicas=5` too: self-heal sets it back to the value in Git.
