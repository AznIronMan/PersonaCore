# Release 1.0.12

`1.0.12` expands the shared message surface into a denser browser default for
consumer admin consoles.

## Changes

- Added optional `MessageSurfaceConfig` controls for:
  - filter chips
  - selected-thread metrics
  - action links
  - conversation and transcript section headings
  - transcript metadata
- Kept the existing minimal message-surface contract backwards compatible for
  consumers that only pass conversations and transcript rows.
- Added shared CSS for the richer message browser controls, metric strip, and
  mobile collapse behavior.
- Updated the public fixture to exercise the new generic message browser shape
  with public-safe example data.
- Extended surface tests to verify the richer controls render while
  owner-private text, media labels, and raw URLs remain redacted for non-owner
  admins.

## Consumer Notes

Consumers still own message queries, thread selection, platform normalization,
auth, private scope mapping, pagination, and raw/file route enforcement.
PersonaConsole only renders escaped display rows and applies the configured
owner-private safe-alternate behavior to provided values.

## Verification

```bash
PYTHONPATH=src python -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.12
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.12.html
```
