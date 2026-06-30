# Release 1.0.9

`1.0.9` adds reusable message, activity, and media/artifact surfaces as
opt-in shared PersonaConsole modules.

## Added

- Added `MESSAGES_FEATURE`, `ACTIVITY_FEATURE`, and `MEDIA_FEATURE`.
- Added generic surface models:
  `MessageSurfaceConfig`, `MessageConversation`, `MessageTranscriptItem`,
  `MessageAttachment`, `ActivitySurfaceConfig`, `ActivityEvent`,
  `MediaSurfaceConfig`, `MediaArtifactCard`, and `SurfaceBadge`.
- Added `render_message_surface(...)`, `render_activity_surface(...)`,
  `render_media_surface(...)`, and `render_surface_sections(...)`.
- Added `personaconsole.surfaces` as the public submodule import path.
- Updated the public fixture console so generic visual QA includes message,
  activity, and media surfaces with a redacted owner-private example.
- Updated the consumer integration doctor to verify the new exports and a
  redacted message/media render smoke.

## Safety

- PersonaConsole does not query consumer databases, inspect private routes, read
  runtime files, or serve media bytes.
- When a row or card declares a privacy scope, the shared renderer shows raw
  text only when the provided owner-private policy and context allow it.
- Non-owner contexts receive safe alternates when provided, otherwise withheld
  placeholders.
- Private href and preview URLs are stripped for non-owner contexts. Consumers
  must still enforce the same policy in HTML, JSON, query/snapshot, and file
  routes before returning raw owner-private data.

## Verification

```bash
PYTHONPATH=src python -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.9
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.9 --json
```
