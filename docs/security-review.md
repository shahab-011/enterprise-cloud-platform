# Security review notes (ECP-6)

## Scope and evidence

This is a practical review checklist for the local demo, not a penetration test, formal audit,
or production security approval. Record each command, date, dependency lock/revision, and result
when checks are run. GitHub Actions results are authoritative only after a real workflow run;
local results are not GitHub evidence.

## Implemented safeguards

- Demo tokens are explicitly local-only, fixed synthetic fixtures; the service is not an
  identity provider. Tokens are never included in application logs or error responses.
- Request schemas reject malformed and oversized token fields. Errors use a consistent
  envelope with a request correlation ID.
- Admin example routes perform an explicit role-permission check.
- API requests are rate limited per client address in one process. This is not a distributed
  gateway policy.
- SQLite queries use parameter binding; operation connections are closed and transactions
  commit or roll back deterministically.
- `.env` and SQLite runtime files are ignored. `.env.example` contains configuration names and
  non-secret defaults only.
- The container uses a non-root user and has no cloud credentials or deployment step.

## Review checklist

- [ ] Run `python -m pip install -e ".[test]"`, `ruff check .`, and `pytest -q`.
- [ ] Inspect dependency advisories using an approved, current scanner and capture its output;
      no vulnerability count is asserted by this repository.
- [ ] Check the Git diff and history for tokens, private keys, `.env`, database files, and
      production data before publishing.
- [ ] Confirm authentication and authorization tests cover invalid, expired, malformed,
      missing, allowed, and denied requests.
- [ ] Confirm logs and error responses do not disclose credentials or sensitive headers.
- [ ] Review rate-limit key trust behind any reverse proxy before deployment.
- [ ] Review container image, base image updates, filesystem permissions, and runtime policy.

## Production-readiness gaps

The fixture has no real identity provider, signed/rotatable credentials, revocation, persistent
role source, TLS termination, distributed rate limiting, PostgreSQL connection pool, secrets
manager, cloud monitoring, deployment automation, threat model, or independent security audit.
The dashboard metrics are local process counters and reset when the process restarts. Do not
describe this demo as production-ready or secure based on these checks alone.
