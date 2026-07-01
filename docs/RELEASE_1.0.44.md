# PersonaConsole 1.0.44

`1.0.44` adds a generic runtime task board surface for consumer runtimes that
need shared admin visibility into adapter-fed tasks without moving the task
database or workflow rules into PersonaConsole.

## Highlights

- Added `RuntimeTaskBoardSurfaceConfig` plus task row, linked record, history,
  and runtime action slot models.
- Added `render_runtime_task_board_surface(...)` behind the
  `runtime_task_board` feature flag with owner-private redaction, pagination,
  filters, status tabs, selected task detail, and optional live-refresh
  controls.
- Added compatibility shims for both `persona_console.runtime_task_board` and
  `personacore.runtime_task_board`.
- Added fixture, doctor, import, renderer, CSS, and configuration docs for the
  shared runtime task board workflow.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/test_runtime_task_board.py tests/test_imports.py tests/test_doctor.py tests/test_fixture_app.py -q
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.44
```
