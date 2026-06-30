# Release 1.0.14

`1.0.14` adds a shared review-board surface for consumer admin consoles.

## Changes

- Added generic review models:
  - `ReviewSurfaceConfig`
  - `ReviewBoardRow`
  - `ReviewAgendaItem`
  - `ReviewQueueSection`
  - `ReviewQueueCard`
- Added `REVIEW_FEATURE`, `review_surface_feature_enabled(...)`, and
  `render_review_surface(...)`.
- Added shared CSS for dense review filters, metrics, decision-board tables,
  agenda cards, and publishing queue cards.
- Extended the public fixture and consumer doctor to exercise review rendering.
- Preserved fail-closed owner-private summary handling for review rows and
  queue cards.

## Consumer Notes

Consumers still own review queries, filters, mutations, auth, owner-private
scope mapping, route targets, and row-level action handlers. PersonaConsole only
renders escaped, consumer-provided review rows and safe summaries.

## Verification

```bash
PYTHONPATH=src python -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.14
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.14.html
python3 -m compileall -q src tests examples
```
