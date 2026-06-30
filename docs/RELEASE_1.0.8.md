# Release 1.0.8

`1.0.8` adds adapter/runtime health cards as an opt-in shared PersonaConsole
feature.

## Added

- Added `ADAPTER_HEALTH_FEATURE`, `AdapterHealthConfig`,
  `AdapterHealthCard`, `AdapterHealthSparkBucket`,
  `adapter_health_feature_enabled(...)`, and
  `render_adapter_health_panel(...)`.
- Added `personaconsole.adapter_health` as the public submodule import path.
- Updated dashboard adapter-card rendering to use the shared adapter-health
  panel while preserving existing `DashboardData.adapters` compatibility.
- Updated the consumer integration doctor to verify adapter-health exports and
  generic panel rendering.
- Updated the public fixture console so visual QA includes the stable
  `pc-adapter-health` feature hook.

## Safety

- PersonaConsole does not probe provider APIs, inspect private runtime routes,
  read credentials, restart services, or query consumer databases.
- Consuming runtimes provide public-safe labels, counts, timestamps, policy
  notes, and optional sparkline buckets from their own already-authorized
  runtime checks.
- The `adapter_health` feature flag hides the shared UI module only; it does not
  replace runtime-side authorization or health-route policy.

## Verification

```bash
PYTHONPATH=src python -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.8
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.8 --json
```
