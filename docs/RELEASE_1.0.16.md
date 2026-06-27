# Release 1.0.16

`1.0.16` adds shared flash/action banner controls and live-refresh class hooks
for consumer admin pages.

## Changes

- Added `FlashBanner`, `render_flash_banners(...)`, `flash_query_params(...)`,
  and `flash_url(...)`.
- Added `personacore.controls` exports for the flash helpers under the public
  import path.
- The flash renderer emits both PersonaCore classes (`pc-flash-*`) and
  legacy-compatible hooks (`flash-*`) so consumers can adopt it incrementally.
- The shell flash container now includes `pc-flash-stack`.
- The live-refresh controls and page refresh button now include `pc-*` class
  hooks while preserving the existing ids and legacy classes.
- Updated shared CSS/JS so server-rendered and query-param flash banners share
  dismiss behavior and tone classes.
- Updated the consumer integration doctor to verify shared flash exports and
  render output.

## Consumer Boundary

PersonaCore does not perform redirects, mutate runtime state, authorize actions,
or decide which operations deserve a flash message. Consumers still own POST
handlers, permissions, target routes, and any action links passed into the
shared renderer.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.16
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personacore-fixture-1.0.16.html
PYTHONPATH=src python3 -m compileall src
```
