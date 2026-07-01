# PersonaConsole 1.0.51

## Summary

Preserves Engine catalog access and input metadata when rendering Control
Center controls.

## Changes

- Engine catalog controls now carry through `view_roles` and `edit_roles` so
  consumer runtimes can make selected Engine-projected controls editable for
  operators without opening the whole catalog.
- Engine catalog conversion now preserves useful control metadata such as
  numeric bounds, step, placeholders, clearable flags, and disabled/read-only
  state.
- Control Center numeric inputs now render zero-valued attributes such as
  `min="0"`.

## Verification

- `PYTHONPATH=src python3 -m pytest tests`
