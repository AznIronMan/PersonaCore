# Release 1.0.24

`1.0.24` adds a reusable system health surface for consumer admin consoles that
need a dense runtime/database/audit posture page without moving probes or
private inspection logic into PersonaConsole.

## Changes

- Added `SystemHealthSurfaceConfig`, `SystemHealthGroup`,
  `SystemHealthCheck`, `SystemDatabaseCard`, `SystemTableSummary`,
  `SystemAuditRow`, `SystemSecretCoverageRow`, and `SystemReadinessProbe`.
- Added `SYSTEM_HEALTH_FEATURE`, `render_system_health_surface(...)`, and
  `system_health_surface_feature_enabled(...)`.
- Renders metric strips, status tabs, health check groups, database cards,
  schema/table summaries, secret coverage cards, readiness probes, and audit
  tables.
- Supports owner-private audit summary redaction using the existing
  `OwnerPrivateScopePolicy` and `AdminPrivacyContext` helpers.
- Added fixture, static CSS, doctor, import, compatibility shim, and focused
  renderer test coverage.

## Boundaries

PersonaConsole does not connect to databases, inspect schemas, read secrets, run
service probes, retain audit events, or execute remediation actions. Consumers
own data collection, authorization, redaction policy, persistence, routes, and
actions.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.24
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.24.html
```
