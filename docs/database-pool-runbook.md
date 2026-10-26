# Database resource runbook (ECP-5)

The demo uses Python's standard-library SQLite driver with one short-lived connection per
operation, a configurable busy timeout, WAL journaling, transaction rollback, and explicit
connection closure. SQLite is file-backed local storage; it does not reproduce PostgreSQL
connection-pool exhaustion or production database behavior.

## Symptoms

- `/health` reports a degraded database status or returns a database error.
- Operations fail with `sqlite3.OperationalError`, including `database is locked`.
- Requests are slower while concurrent local writes contend for the SQLite file.

## Investigation

From the repository root, inspect configuration and rerun the resource lifecycle tests:

```powershell
Get-Content .env
python -m pytest -q tests/test_database.py
python -m pytest -q tests/test_monitoring.py
```

Do not share `.env` contents or database files containing data. This fixture should contain
only synthetic test data. Check that `DATABASE_PATH` points to a writable local directory and
that a process is not holding the SQLite file open. Preserve sanitized error text, timestamps,
and request IDs when reporting an issue.

## Recovery options

1. Stop the local demo process before moving or replacing its SQLite file.
2. Back up the file if any local test evidence needs to be retained.
3. For disposable demo state only, remove the database file and restart; initialization
   recreates the schema. Do not delete files until their contents and purpose are confirmed.
4. Tune `DATABASE_TIMEOUT_SECONDS` for local lock contention and rerun concurrent-operation
   tests. A larger timeout is not a substitute for a production pooling design.

For PostgreSQL, separately assess bounded pool size, acquisition timeout, transaction scope,
connection leaks, retry policy for transient errors, and load-test evidence. Do not infer a
production fix from the SQLite demonstration.
