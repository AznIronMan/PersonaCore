# PersonaConsole 1.0.46

`1.0.46` adds a generic admin access surface for consumer runtimes that need
shared visibility into admin principals, sessions, allow/block rules, lockouts,
and access audit posture while keeping enforcement local.

## Highlights

- Added `AdminAccessSurfaceConfig` plus principal, session, access rule, audit,
  warning, and action slot models.
- Added `render_admin_access_surface(...)` behind the `admin_access` feature
  flag with owner-private redaction and optional live-refresh controls.
- Added compatibility shims for both `persona_console.admin_access` and
  `personacore.admin_access`.
- Added fixture, doctor, import, renderer, CSS, and configuration docs for
  centralized-admin-login companion surfaces.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/test_admin_access.py tests/test_imports.py tests/test_doctor.py tests/test_fixture_app.py -q
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.46
```
