# Release 1.0.22

`1.0.22` adds a generic read-only terminal stream surface for consumer admin
consoles that need to show current agent/runtime activity without exposing a
real interactive shell.

## Changes

- Added `TerminalStreamConfig`, `TerminalStreamEvent`,
  `TERMINAL_STREAM_FEATURE`, `render_terminal_stream(...)`, and
  `terminal_stream_feature_enabled(...)`.
- Integrated the terminal stream into `AgentOpsSurfaceConfig` so shared agent
  operations pages can show a current bounded event window.
- Added static CSS/JS for bounded rendered rows, current-window autoscroll,
  chunked earlier-history loading, live polling, and no-JS fallback rendering.
- Kept the terminal surface read-only: consumers own capture, retention,
  stream/history endpoints, auth, and any real command execution.
- Updated the public fixture and consumer doctor to exercise owner-private
  redaction for terminal events.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.22
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.22.html
```

## Notes

Initial renderers should receive only a bounded current slice. Older history
should be fetched in chunks with cursors so very long logs do not lock the
consumer server or the operator's browser.
