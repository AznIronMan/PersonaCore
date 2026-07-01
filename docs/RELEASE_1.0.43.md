# PersonaConsole 1.0.43

`1.0.43` adds a generic presence monitor surface for consumer runtimes that need
shared admin visibility into runtime presence state, channel posture, schedule
windows, source freshness, policy notes, and recent transitions.

## Highlights

- Added `PresenceMonitorSurfaceConfig` plus state, channel, schedule,
  freshness, policy, and transition row models.
- Added `render_presence_monitor_surface(...)` behind the `presence_monitor`
  feature flag with owner-private redaction and optional live-refresh controls.
- Added compatibility shims for both `persona_console.presence_monitor` and
  `personacore.presence_monitor`.
- Added fixture, doctor, import, renderer, CSS, and configuration docs for the
  shared presence admin workflow.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/test_presence_monitor.py tests/test_imports.py tests/test_doctor.py tests/test_fixture_app.py -q
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.43
```
