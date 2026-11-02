# Cloud, DevOps & Cybersecurity: The Advanced Playbook — Companion Code

Policies, manifests, infrastructure code, scripts and lab solutions for the book **Cloud, DevOps & Cybersecurity: The Advanced Playbook — Engineering, Automating and Defending Cloud-Native Systems at Scale** by Chaima Agoumi.

Each chapter of the book has a folder. Every folder contains the chapter's examples as complete files and a `README.md` with worked solutions to the chapter's labs.

## Responsible use

Everything here is **defensive**. Run it only in accounts and clusters you own or are explicitly authorized to manage, ideally a dedicated sandbox AWS organization and a local Kubernetes cluster. Never point attack emulation or containment scripts at production.

## Before you start

| Tool | Used in | Notes |
| --- | --- | --- |
| A sandbox AWS account with a **budget alert** | 2, 3, 7, 10, 11, 12 | Create the budget alarm first: some labs create billable resources |
| Terraform 1.10+ or OpenTofu | 3, 7, 11, 12 | |
| `kind` or `minikube`, `kubectl`, Helm | 4, 5, 8, 9 | Use Cilium or Calico as CNI so network policies are enforced |
| Argo CD and Argo Rollouts | 3, 5 | Installed with Helm in the local cluster |
| conftest, OPA | 3 | |
| syft, grype, cosign | 8 | |
| Falco | 9 | |
| Python 3.11+ | 6, 8, 11 | `pip install -r requirements.txt` |

## Chapters

| Chapter | Folder |
| --- | --- |
| 1. The fundamentals refresher | [`ch01-refresher`](ch01-refresher) |
| 2. Cloud architecture at scale | [`ch02-architecture`](ch02-architecture) |
| 3. Infrastructure as code at scale | [`ch03-iac`](ch03-iac) |
| 4. Kubernetes in production | [`ch04-kubernetes`](ch04-kubernetes) |
| 5. CI/CD and release engineering | [`ch05-cicd`](ch05-cicd) |
| 6. Observability and SRE | [`ch06-sre`](ch06-sre) |
| 7. Identity is the new perimeter | [`ch07-iam`](ch07-iam) |
| 8. Securing the software supply chain | [`ch08-supply-chain`](ch08-supply-chain) |
| 9. Container and Kubernetes security | [`ch09-container-security`](ch09-container-security) |
| 10. Threat modeling and detection engineering | [`ch10-detection`](ch10-detection) |
| 11. Cloud incident response and forensics | [`ch11-incident-response`](ch11-incident-response) |
| 12. Governance, compliance and the capstone | [`ch12-governance`](ch12-governance) |

## Placeholders to replace

Account IDs (`111122223333`), organization IDs (`o-exampleorgid`), VPC endpoint IDs, repository names (`acme/checkout`) and image digests are examples. Replace them with your own values before applying anything.

## Testing

```bash
pip install -r requirements.txt
pytest
```

The Python tools have unit tests that run without cloud credentials. Infrastructure code, policies and manifests are written for current tool versions; run them in your sandbox and open an issue if anything has changed upstream.

## License

The code in this repository is released under the [MIT License](LICENSE). The book's text and figures are © 2026 Chaima Agoumi and are not covered by this license.

## Author

**Chaima Agoumi** — Casablanca, Morocco

- LinkedIn: [Chaima Agoumi](https://www.linkedin.com/in/chaima-a-218657295)
- GitHub: [@Chaaamah](https://github.com/Chaaamah)
- Email: agoumi.chaima@gmail.com
