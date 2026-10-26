# Architecture decisions

## ADR-001: One local FastAPI process

The demo keeps health, auth fixtures, route simulation, metrics, and the dashboard in one
process. This makes the default setup deterministic and avoids pretending that separate
services or cloud integrations exist.

## ADR-002: SQLite and short-lived connections

SQLite is used to demonstrate transaction and connection cleanup without requiring a database
service. It is not a PostgreSQL pool-exhaustion reproduction. Connections use a bounded busy
timeout and close after each operation.

## ADR-003: In-memory local rate limit and metrics

Rate-limit state and request metrics are process-local. They are intentionally small and
observable, but do not coordinate across workers or persist across restarts.

## ADR-004: Provider-free Terraform scaffold

Terraform describes naming and application metadata only. It has no provider or resource
definitions, so it cannot create cloud infrastructure or incur cloud costs.
