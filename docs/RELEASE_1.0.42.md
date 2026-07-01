# PersonaConsole 1.0.42

`1.0.42` adds a generic public profile admin surface for consumer runtimes that
need shared editing, readiness, preview, media-reference, and history controls
without moving the public website, login, chat, upload, or publish pipeline into
PersonaConsole.

## Highlights

- Added `PublicProfileSurfaceConfig` plus public profile field, section,
  preview, readiness, media, and history models.
- Added `render_public_profile_surface(...)` behind the `public_profile`
  feature flag with owner-private redaction support.
- Added compatibility shims for both `persona_console.public_profile` and
  `personacore.public_profile`.
- Added fixture, doctor, import, and renderer tests for the shared profile
  admin workflow.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/test_public_profile.py tests/test_imports.py tests/test_doctor.py tests/test_fixture_app.py -q
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.42
```
