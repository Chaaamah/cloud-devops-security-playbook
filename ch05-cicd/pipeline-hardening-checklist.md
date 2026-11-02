# Pipeline hardening checklist (lab 3)

Audit one real pipeline. Tick an item only when you have seen the evidence.

## Credentials
- [ ] No long-lived cloud access keys stored as CI secrets; cloud access uses OIDC federation
- [ ] Each OIDC trust policy checks both `aud` and `sub` (repository **and** branch or environment)
- [ ] The default token is read-only (`permissions: contents: read` at workflow level)
- [ ] Write scopes are granted per job, only where needed

## Third-party code
- [ ] Every third-party action or plugin is pinned to a full commit SHA, not a tag
- [ ] A bot (Dependabot or Renovate) proposes SHA updates, reviewed like any other change
- [ ] The list of allowed actions is restricted at organization level

## Untrusted input
- [ ] Workflows triggered by forks get no secrets and no write permissions
- [ ] `pull_request_target` is not used, or never checks out and runs fork code
- [ ] Pull request titles, branch names and issue text are never interpolated into `run:` scripts; they are passed through environment variables instead

## Deployment
- [ ] Production deploys require a protected environment with reviewers
- [ ] Only the main branch can deploy to production
- [ ] The artifact deployed is the exact digest that was tested and signed

## Runners
- [ ] Runners are ephemeral: a fresh VM or container for every job
- [ ] Self-hosted runners never serve public repositories
- [ ] Runner egress is restricted to what builds need

## Monitoring
- [ ] Changes to workflow files require review from the platform team (CODEOWNERS)
- [ ] Pipeline audit logs are shipped to the security account
