# Release 1.0.27

`1.0.27` adds a reusable command intake preview surface for consumer admin
consoles that need to show parsed operator intent before runtime-owned
execution.

## Added

- `CommandIntakeSurfaceConfig` plus rows for parsed fields, candidate targets,
  risk checks, confirmation steps, queued commands, and command history.
- `render_command_intake_surface(...)` and
  `command_intake_feature_enabled(...)`.
- Public exports and compatibility shim submodules for
  `personaconsole.command_intake`, `persona_console.command_intake`, and
  `personacore.command_intake`.
- Fixture, doctor, import, and focused tests for rendering, feature gates,
  disabled action slots, and owner-private redaction.

## Boundaries

PersonaConsole only renders the preview and posture data supplied by a consumer.
Consumers still own command parsing, target lookup, policy evaluation,
confirmation semantics, auth, queue storage, execution, provider calls, local
filesystem access, audit logging, and side effects.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.27
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.27.html
```
