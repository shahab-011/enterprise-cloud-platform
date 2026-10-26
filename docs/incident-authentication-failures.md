# Authentication incident report template (ECP-1)

This is a template for a simulated local demonstration. It does not describe a confirmed
production incident or establish a root cause.

## Incident summary

- Incident ID:
- Start/end time (with timezone):
- Affected demo component:
- Severity and customer impact:

## Observed symptoms

Record the exact HTTP status, response error code, request ID, and timestamp. Never paste bearer
tokens, authorization headers, or other credentials into the report.

## Reproduction steps

1. Start the local service using the README instructions.
2. Exercise a documented valid, invalid, expired, or malformed demo credential.
3. Record the status code, error code, and `X-Request-ID`.

## Evidence collected

- Local command and environment:
- Request ID(s):
- Relevant sanitized log entries:
- Test(s) run and actual result:

## Suspected causes

List hypotheses separately from confirmed facts. Do not mark a hypothesis as root cause without
reproducible evidence.

## Confirmed root cause

Not established by the demo. Complete only after evidence identifies and verifies a cause.

## Mitigation

Document the change, operator action, and how it can be rolled back.

## Regression tests

Record the test name and actual result; relevant local coverage is in `tests/test_auth.py`.

## Remaining risks

The local token fixture does not implement a production identity provider, token signing,
revocation, rotation, or distributed session management.
