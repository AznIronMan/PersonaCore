# PersonaConsole 1.0.45

`1.0.45` adds a generic infrastructure posture surface for consumer runtimes
that need shared admin visibility into DNS, certificates, edge endpoints,
propagation checks, and infrastructure warnings.

## Highlights

- Added `InfrastructurePostureSurfaceConfig` plus DNS record, certificate,
  endpoint, propagation check, warning, and action slot models.
- Added `render_infrastructure_posture_surface(...)` behind the
  `infrastructure_posture` feature flag with owner-private redaction and
  optional live-refresh controls.
- Added compatibility shims for both `persona_console.infrastructure_posture`
  and `personacore.infrastructure_posture`.
- Added fixture, doctor, import, renderer, CSS, and configuration docs for
  DNS/certificate posture rendering.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/test_infrastructure_posture.py tests/test_imports.py tests/test_doctor.py tests/test_fixture_app.py -q
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.45
```
