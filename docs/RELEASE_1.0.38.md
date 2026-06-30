# PersonaConsole 1.0.38

`1.0.38` adds generic diagnostic fallback and table primitives for consumer
Admin cleanup passes.

## Changes

- Added `DiagnosticActionCard`, `DiagnosticMetaPair`, and
  `DiagnosticTableColumn`.
- Added `render_surface_unavailable(...)` for public-safe renderer-unavailable
  diagnostics without consumer-specific wording.
- Added `render_diagnostic_action_card(...)` and
  `render_diagnostic_action_cards(...)` with legacy `action-card` CSS hooks.
- Added `render_diagnostic_table(...)` and
  `render_sortable_diagnostic_table(...)` for compact diagnostic tables with
  safe default escaping, optional row links, sortable headers, and legacy table
  CSS hooks.
- Updated the consumer integration doctor to audit the new exports and render
  paths.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.38
```
