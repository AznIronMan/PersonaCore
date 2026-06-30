# Release 1.0.11

`1.0.11` extracts the reference-style people page into a shared typed
PersonaConsole surface.

## Changes

- Added generic people models:
  - `PeopleSurfaceConfig`
  - `PersonListRow`
  - `PersonRelationshipSummary`
  - `PersonTag`
- Added `PEOPLE_FEATURE`, `people_surface_feature_enabled(...)`, and
  `render_people_surface(...)` under both `personaconsole` and `personaconsole`
  import paths.
- Added `personaconsole.people` as the public submodule import path.
- Added shared CSS for the dense people filter bar, new-person slot, table,
  tags, relationship score, and notes summary.
- Updated the public fixture to render the typed people surface with generic
  data and owner-private safe alternates.
- Updated the consumer integration doctor to verify people exports and a
  privacy-redacted people render.

## Consumer Notes

Consumers still own person queries, create/edit routes, auth, private tier
mapping, and server-side owner-private enforcement. PersonaConsole only renders
escaped display data and applies the same safe-alternate/withheld behavior used
by the other shared UI surfaces when a row declares a private notes scope.

## Verification

```bash
PYTHONPATH=src python -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.11
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.11.html
```
