# Release 1.0.15

`1.0.15` adds a shared status-tab control for consumer admin list and queue
pages.

## Changes

- Added `StatusTab` and `render_status_tabs(...)`.
- Added `personacore.controls` as the public submodule import path.
- The renderer emits both PersonaCore classes and legacy-compatible
  `status-tabs`, `status-tab`, and `status-tab-count` hooks so consumers can
  adopt it incrementally.
- Added shared CSS for dense, pill-shaped status tabs.
- Updated the consumer integration doctor to verify shared control exports and
  render output.

## Consumer Boundary

PersonaCore does not build status URLs, query runtime databases, decide which
statuses exist, or enforce route access. Consumers pass sanitized labels, hrefs,
counts, active state, and tone values into the shared renderer.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.15
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personacore-fixture-1.0.15.html
PYTHONPATH=src python3 -m compileall src
```
