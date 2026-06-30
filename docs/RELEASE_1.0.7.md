# Release 1.0.7

`1.0.7` adds a public-safe consumer integration doctor for runtime upgrade and
restart smokes.

## Changes

- Added `run_consumer_integration_doctor(...)` and `doctor_report_to_text(...)`
  through both `personaconsole` and `personaconsole` import paths.
- Added `scripts/consumer_integration_doctor.py` for source-checkout and mounted
  source deployments.
- The doctor checks importability, version alignment, installed package metadata
  when available, token-health exports, owner-private exports, shell rendering,
  token-health panel rendering, and owner-private safe alternate rendering.
- Doctor output omits imported module filesystem paths by default. Operators can
  pass `--show-paths` for local diagnostics.

## Consumer Notes

Run this after updating PersonaConsole, changing a mounted source directory, or
rebuilding/restarting consumer services:

```bash
PYTHONPATH=/path/to/personaconsole/src python3 /path/to/personaconsole/scripts/consumer_integration_doctor.py --expected-version 1.0.7
```

Use `--json` when wiring this into a consumer-specific smoke script. The doctor
does not replace runtime-owned login, auth, database, media, privacy-route, or
token validation tests.
