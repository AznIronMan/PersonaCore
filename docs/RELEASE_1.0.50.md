# PersonaConsole 1.0.50

## Summary

Adds Control Center access-context rendering and explicit secret clear actions
for consumer runtimes that need owner/operator/moderator control posture.

## Changes

- Added `ControlAccessContext` and per-control `view_roles`/`edit_roles`
  metadata.
- Control Center rendering can now show hidden, editable, view-only, disabled,
  and read-only controls according to a runtime-supplied access context.
- Pending counts, section navigation, and diffs now follow the same visibility
  filtering as the rendered controls.
- Secret controls can be marked `clearable`, rendering a separate
  `.__clear=true` checkbox while keeping blank password input as “keep current
  value.”
- Secret inputs now default to “Stored; type here to overwrite” when a value is
  configured and still never render current or pending secret values.

## Verification

- `PYTHONPATH=src python3 -m pytest tests`
