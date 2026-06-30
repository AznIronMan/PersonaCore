# Release 1.0.28

`1.0.28` adds a reusable availability/live monitor surface for consumer admin
consoles that need to show schedule windows, live checks, policy posture,
scenario QA, and recent monitor events.

## Added

- `AvailabilityMonitorSurfaceConfig` plus rows for schedule windows, live
  monitor checks, policy posture, scenario QA, and monitor events.
- `render_availability_monitor_surface(...)` and
  `availability_monitor_feature_enabled(...)`.
- Public exports and compatibility shim submodules for
  `personaconsole.availability_monitor`, `persona_console.availability_monitor`,
  and `personacore.availability_monitor`.
- Fixture, doctor, import, and focused tests for rendering, feature gates,
  disabled action slots, and owner-private redaction.

## Boundaries

PersonaConsole only renders display-safe state supplied by a consumer. Consumers
still own schedule evaluation, queue workers, provider probes, alerts,
notifications, database reads, route authorization, worker control, service
restarts, and runtime policy.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.28
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.28.html
```
