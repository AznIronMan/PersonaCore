# Release 1.0.36

`1.0.36` adds a public-safe surface composition registry for consumer Admin
consoles.

## Added

- `SurfaceRegistryConfig`, `SurfaceRegistration`,
  `SurfaceAssetRequirement`, `SurfaceAdapterBinding`,
  `SurfaceRegistryIssue`, and `SurfaceRegistryReport`.
- `build_surface_registry_report(...)` for duplicate route-key, unsafe href,
  unknown feature, missing renderer, missing asset, and disabled-surface checks.
- `render_surface_registry_report(...)` for a compact operator-facing coverage
  audit.
- `surface_registry_to_nav_groups(...)` and
  `surface_registry_feature_flags(...)` helpers for building configured
  PersonaConsole instances from one registry.
- Doctor, fixture, docs, and compatibility submodule coverage.

## Safety

The registry describes consumer-owned bindings. PersonaConsole does not own
routes, auth, data loading, databases, provider calls, secrets, private config,
or adapter execution. Registry hrefs and asset paths are validated as
same-origin root-relative URLs or anchors.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.36
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.36.html
python3 scripts/visual_smoke.py
```
