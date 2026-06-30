# Release 1.0.17

`1.0.17` adds shared runtime workflow surfaces for operations, persona state,
continuity, bridges, and agent sessions.

## Changes

- Added public-safe dataclasses for operations rows/cards/settings/logs,
  persona panels, continuity rows, bridge status cards, and agent-session rows.
- Added `render_operations_surface(...)`,
  `render_persona_runtime_surface(...)`, `render_agent_ops_surface(...)`, and
  `render_workflow_sections(...)` under both `personaconsole` and
  `personaconsole`.
- Added feature constants and enabled checks:
  `OPERATIONS_FEATURE`, `PERSONA_RUNTIME_FEATURE`, and `AGENT_OPS_FEATURE`.
- Added `personaconsole.operations` as a public re-export module.
- Updated the public fixture to use typed workflow surfaces instead of static
  task/log/settings placeholder panels.
- Updated the consumer integration doctor to verify the new exports and safe
  redaction behavior.

## Consumer Boundary

PersonaConsole renders escaped, read-only operational posture. Consumers still own
task execution, worker controls, settings mutation, secret lookup, provider
calls, agent-session lifecycle, route authorization, and persistence.

Secret settings render only configured/not-configured posture. Rows with a
privacy scope use safe alternates for non-owner contexts and strip raw links in
the shared HTML.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.17
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.17.html
PYTHONPATH=src python3 -m compileall src
```
