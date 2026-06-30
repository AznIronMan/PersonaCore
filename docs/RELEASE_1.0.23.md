# Release 1.0.23

`1.0.23` adds a reusable settings editor surface for consumer admin consoles
that need grouped runtime settings without copying hardcoded form markup.

## Changes

- Added `SettingsEditorConfig`, `SettingsGroup`, `SettingsField`,
  `SettingsOption`, `SettingsValidationMessage`, and `SettingsChange`.
- Added `SETTINGS_EDITOR_FEATURE`, `render_settings_editor(...)`, and
  `settings_editor_feature_enabled(...)`.
- Supports text, textarea, select, boolean, number, secret/redacted, readonly,
  JSON, and code-style display fields.
- Renders validation messages, save/restart banners, pending-change summaries,
  restart-required markers, redacted safe value previews, and consumer-supplied
  action slots.
- Added fixture, static CSS/JS, doctor, import, and compatibility shim coverage.

## Boundaries

PersonaConsole does not read environment variables, reveal secrets, persist
settings, restart services, decide authorization, or write audit logs. Consumers
own storage, validation, reveal permission, mutation handlers, queueing,
restart execution, and audit logging.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.23
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.23.html
```
