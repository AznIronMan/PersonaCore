# Release 1.0.33

`1.0.33` adds a reusable live-refresh and partial-update contract for shared
admin surfaces.

## Added

- `LiveRefreshConfig` for endpoint URL, interval options, target/control/status
  ids, hold selectors, stale thresholds, pause defaults, labels, and no-JS
  fallback links.
- `live_refresh_attributes(...)`, `render_live_region(...)`, and
  `render_live_status(...)` helpers for attaching live metadata to any
  consumer-owned surface fragment.
- Expanded `render_live_controls(...)` output with `data-pc-live-*` attributes,
  pause state, interval options, target binding, status binding, and no-JS
  fallback support.
- Browser behavior for multiple partial targets, manual refresh, pause/resume,
  persisted interval state, hold selectors, stale/error states, and existing
  `window.__personaConsoleRefreshLiveTarget` compatibility.
- CSS for refreshing, stale, and error target states.
- Doctor, fixture, and visual-smoke coverage for the partial target contract.

## Boundaries

PersonaConsole only renders the shared controls and client behavior. Consumers
still own partial endpoints, authentication, permissions, rate limits, database
queries, cache policy, websocket/SSE alternatives, and returned HTML fragments.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.33
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.33.html
python3 scripts/visual_smoke.py
```
