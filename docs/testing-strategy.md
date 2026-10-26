# Testing strategy

`pytest` and FastAPI's `TestClient` exercise the public API without a network listener. Tests use
temporary SQLite files and deterministic synthetic tokens. The coverage includes authentication
success and failure shapes, authorization, HTTP 429 behavior, fixture labeling, responsive
dashboard markup, concurrent SQLite operations, transaction rollback, health, and measured
request counters.

Run all tests with `python -m pytest -q`, or focus on a Jira area:

```powershell
python -m pytest -q tests/test_auth.py
python -m pytest -q tests/test_gateway.py
python -m pytest -q tests/test_database.py
```

`ruff check .` is the CI code-quality gate. Tests and local lint do not imply that GitHub Actions
has run. No PostgreSQL, cloud, multi-worker, browser-automation, or production load test is
included.
