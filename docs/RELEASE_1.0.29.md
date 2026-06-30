# Release 1.0.29

`1.0.29` adds a reusable generic admin-list surface for consumer consoles that
need to move bespoke list/table UI into PersonaConsole while keeping runtime
data, routes, permissions, and mutations local.

## Added

- `AdminListSurfaceConfig` plus column, cell, row, filter field, and pagination
  models.
- `render_admin_list_surface(...)` and
  `admin_list_surface_feature_enabled(...)`.
- Desktop table, status tabs, metric cards, filter form, sortable header links,
  row action slots, pagination controls, and mobile card fallback markup.
- Owner-private safe-alternate rendering for cells and row card summaries, with
  raw cell hrefs suppressed unless the viewer can see the matching scope.
- Public exports, doctor checks, docs, and focused tests for escaping, feature
  gates, empty state, pagination, mobile cards, row actions, and privacy.

## Boundaries

PersonaConsole only renders normalized rows and controls supplied by a consumer.
Consumers still own database queries, search/filter semantics, auth, route
authorization, mutations, audit logging, deployment, and runtime-specific
business logic.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.29
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.29.html
```
