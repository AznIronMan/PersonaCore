# PersonaConsole 1.0.48

`1.0.48` fixes Control Center layout resilience when a consumer runtime has
global form/grid styles.

## Highlights

- Forced `.pc-control-center` to use a single-column grid so whole sections do
  not inherit runtime-level form grid columns.
- Updated Control Center overview and card grids to use responsive `auto-fit`
  tracks with readable minimum widths.
- Allowed source-path labels inside Control Center cards to wrap instead of
  creating hidden horizontal overflow on narrow screens.
- Added a CSS regression test for the Control Center form-grid guard.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.48
```
