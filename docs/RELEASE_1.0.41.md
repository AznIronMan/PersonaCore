# PersonaConsole 1.0.41

`1.0.41` lets admin-login consumers preserve pre-validated absolute return
URLs when an external login service hands back to a separate admin console
origin.

## Highlights

- Added `allowed_next_origins` to `AdminLoginPageConfig`.
- Kept absolute `next` URLs blocked by default unless the consumer opts into
  specific `http` or `https` origins.
- Preserved existing blocked-login path protection for root-relative and
  allowed absolute URLs.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.41
```
