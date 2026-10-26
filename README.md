# Enterprise Cloud Platform Modernization

A runnable, local-only backend demo for a fictional enterprise platform modernization program.
It gives an engineering team reproducible examples for authentication reliability, role
authorization, gateway rate limiting, SQLite resource handling, CI, containerization,
infrastructure examples, monitoring, and responsive dashboard behavior.

The project does not connect to production infrastructure, a cloud account, an identity provider,
Jira, GitHub MCP, or Orquestra. It contains no real customer data and requires no cloud credentials.

## Business scenario

The fictional platform team is investigating intermittent authentication failures, fragmented
identity controls, inconsistent API routing, manual CI/CD, database resource pressure, security
review gaps, inconsistent infrastructure, limited monitoring, and a dashboard overflow issue.
The repository supplies local code and test evidence for those themes; it does not assert that a
real production incident occurred or that a suspected root cause was confirmed.

The fictional team scenario describes Rahul Kumar (`RK`) as focused on backend reliability,
database performance, infrastructure, and monitoring, and Shivani Kumari (`SK`) as focused on
authentication, identity, security, and API gateway engineering. These are scenario roles, not
verified GitHub account identities or current Jira assignments. Actual owners and work statuses
must be checked in Jira and GitHub, not inferred from these descriptions or local test results.

## Architecture and stack

- Python 3.12+, FastAPI, Pydantic Settings, Uvicorn
- SQLite through Python's standard library
- pytest, HTTPX, and Ruff
- Docker/Compose, GitHub Actions, Kubernetes YAML, provider-free Terraform scaffold
- Single-process API with no separate frontend framework

See [ARCHITECTURE.md](ARCHITECTURE.md) for diagrams and component details.

## Repository layout

```text
services/       API, auth fixture, gateway simulation, and local metrics
shared/         environment configuration, JSON logs, and SQLite lifecycle
tests/          API, authorization, rate-limit, metrics, and DB regression tests
web/            responsive HTML/CSS/JS dashboard
docs/           incident template, runbooks, security notes, decisions, test strategy
infra/          Kubernetes manifests and provider-free Terraform scaffold
.github/        CI workflow, issue templates, and PR checklist
```

## Prerequisites and installation

- Python 3.12 or newer
- Optional: Docker Desktop with Compose for the container example
- Optional: Terraform 1.5+ for validating the provider-free metadata scaffold

From the repository root in PowerShell:

```powershell
python --version
python -m pip install -e ".[test]"
Copy-Item .env.example .env
```

The `.env` copy is optional; the application runs with the defaults in `shared/config.py`.
Configure the Python environment you intend to use before installing packages. This repository
does not require or create a virtual environment.

## Run locally

```powershell
python -m uvicorn services.platform_api:app --reload
```

Open `http://127.0.0.1:8000/health`, API docs at `http://127.0.0.1:8000/docs`, or the responsive
dashboard at `http://127.0.0.1:8000/dashboard`. The default SQLite file is created at
`data/platform.sqlite3` and is ignored by Git.

### Example requests

```powershell
Invoke-RestMethod http://127.0.0.1:8000/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/auth/health
Invoke-RestMethod http://127.0.0.1:8000/api/v1/metrics
Invoke-RestMethod http://127.0.0.1:8000/api/v1/routes
Invoke-RestMethod http://127.0.0.1:8000/api/v1/demo/issues
```

Validate a synthetic credential:

```powershell
Invoke-RestMethod -Method Post `
  -Uri http://127.0.0.1:8000/api/v1/auth/validate `
  -ContentType "application/json" `
  -Body '{"token":"demo-viewer-token"}'
```

Authenticated user and admin example:

```powershell
Invoke-RestMethod http://127.0.0.1:8000/api/v1/users/me `
  -Headers @{ Authorization = "Bearer demo-viewer-token" }
```

`demo-admin-token`, `demo-operator-token`, and `demo-viewer-token` are public, synthetic test
fixtures. `demo-expired-token` deterministically returns an expired-credential error. These
values are not secrets and must never be treated as production authentication.

## Tests and quality

```powershell
python -m pytest -q
ruff check .
```

The tests cover valid, invalid, expired, malformed, missing, and role-restricted authentication;
HTTP 429 behavior; route and fixture labeling; dashboard responsive markup; concurrent SQLite
operations and rollback; health; and locally measured metrics. See [docs/testing-strategy.md](docs/testing-strategy.md).

## Docker

With Docker available:

```powershell
docker compose up --build
```

The service is available at `http://127.0.0.1:8000`. The image runs as a non-root user, persists
SQLite data in a named volume, and includes a health check. No secret is baked into the image and
no deployment or image publishing is configured.

## Jira issue mapping and local coverage

| Key | Scenario | Local evidence |
|---|---|---|
| ECP-1 | Authentication reliability | `services/auth_service/`, `tests/test_auth.py`, incident template |
| ECP-2 | Centralized IAM | Role and permission fixture, authorization tests |
| ECP-3 | Gateway routing/rate limiting | `services/api_gateway/`, `tests/test_gateway.py` |
| ECP-4 | CI/CD | `.github/workflows/ci.yml`; only configured, not run on GitHub here |
| ECP-5 | Database resource handling | `shared/database.py`, concurrent and rollback tests |
| ECP-6 | Security/dependency review | `docs/security-review.md`; checklist is not an audit result |
| ECP-7 | Infrastructure as code | Kubernetes examples and provider-free Terraform metadata |
| ECP-8 | Monitoring | Local health and process metrics endpoints |
| ECP-9 | Responsive layout | `/dashboard`, `web/dashboard.html`, markup test |

`GET /api/v1/demo/issues` is static fixture data, not a Jira integration. Jira status/assignment
and GitHub pull request/review/merge/Actions state must be checked in their respective systems.
The presence of the CI workflow is not evidence it has run, and local tests are not GitHub results.

## Known limitations and security caveats

- Authentication tokens and roles are fixed local fixtures, not a secure identity system.
- The operator/admin permissions are illustrative static policy examples, not a managed IAM
  service or role database.
- The rate limiter and metrics are in-process and reset on restart; rate limits do not coordinate
  across workers or trust-proxy boundaries.
- SQLite is not PostgreSQL and does not reproduce PostgreSQL pooling or production contention.
- Kubernetes and Terraform examples are illustrative and are not deployed or validated against a
  live cluster. Terraform intentionally declares no provider/resources, so it cannot provision
  anything.
- No dependency vulnerability scan, external security audit, production load test, live cloud
  metric collection, browser automation, or GitHub Actions run is claimed.
- This demo is not production-ready. See [SECURITY.md](SECURITY.md) and
  [docs/security-review.md](docs/security-review.md).

## Engineering workflow

Suggested branches: `fix/ECP-1-auth-reliability`,
`feat/ECP-2-centralized-iam`, `feat/ECP-3-api-rate-limiting`,
`feat/ECP-4-container-ci`, `fix/ECP-5-database-resource-handling`,
`chore/ECP-6-security-review`, `feat/ECP-7-infrastructure-as-code`,
`feat/ECP-8-service-metrics`, `fix/ECP-9-responsive-dashboard`.

Use the [contribution checklist](CONTRIBUTING.md) and GitHub pull request template. The initial
repository publication does not create Jira records, GitHub issues, feature branches, pull
requests, or workflow-run evidence. Actual records and statuses must be read from Jira and GitHub.

## Future improvements

Introduce an approved identity provider, durable metrics backend, distributed gateway policies,
PostgreSQL pool/load testing, dependency scanning, browser-level responsive tests, and an
explicitly reviewed cloud deployment design only when there is a concrete requirement and
authorization.
