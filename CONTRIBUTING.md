# Contributing

Keep changes small and link implementation evidence to the corresponding Jira issue. Suggested
branch names include `fix/ECP-1-auth-reliability`,
`feat/ECP-3-api-rate-limiting`, and `fix/ECP-5-database-resource-handling`.

Use descriptive conventional commits, for example `fix(auth): handle malformed demo credentials`.
Actual Jira assignments and statuses are authoritative in Jira; actual code review and merge
states are authoritative in GitHub. Do not infer either from repository fixtures.

Before opening a pull request:

1. Run `python -m pytest -q` and `ruff check .`.
2. Update documentation for changed behavior.
3. Verify no secrets, real customer data, or generated database files are included.
4. Never run Terraform apply, cloud deployment, or image publishing as part of this demo workflow.
5. Complete the pull request checklist in `.github/PULL_REQUEST_TEMPLATE.md`.
