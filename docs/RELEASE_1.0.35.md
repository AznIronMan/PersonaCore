# Release 1.0.35

`1.0.35` extends the shared system health surface with reusable audit and
secret review presentation primitives.

## Added

- `SystemAuditFilterState`, `SystemSecretFilterState`, and
  `SystemPaginationState` for consumer-applied filter summaries and pagination
  labels.
- `SystemSecretInventoryRow` for key-name-only secret row summaries.
- Optional `entity` and `source` fields on `SystemAuditRow`.
- Optional section/source grouping, configured counts, import status, last
  checked labels, and no-reveal copy on `SystemSecretCoverageRow`.
- Compact mobile card rendering for audit and secret rows while preserving the
  dense table view on desktop.
- Fixture and doctor coverage for configured, missing, filtered, paginated, and
  redacted states.

## Safety

PersonaConsole only renders display-safe audit and secret metadata supplied by
the consumer. It does not read secret values, import credentials, fetch audit
rows, parse request filters, decide reveal permissions, or write audit logs.
Owner-private audit summaries still use the existing redaction policy hooks.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.35
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.35.html
python3 scripts/visual_smoke.py
```
