# Release 1.0.18

`1.0.18` adds a shared themed journal reader for continuity pages.

## Changes

- Added public-safe journal dataclasses for calendar days, entries, markers,
  details, theme options, and surface configuration.
- Added `JOURNAL_FEATURE`, `JOURNAL_THEME_KEYS`,
  `build_journal_calendar(...)`, `journal_theme_options(...)`, and
  `render_journal_surface(...)` under both `personaconsole` and
  `personaconsole`.
- Added `personaconsole.journal` as a public re-export module.
- Added shared CSS for the default paper reader plus white paper, typewriter,
  script, sepia, ledger, night ink, violet archive, matrix, amber terminal,
  blueprint, and glass themes.
- Updated the public fixture and visual smoke to include the journal surface.
- Updated the consumer integration doctor to verify journal exports and
  owner-private redaction for entry text, details, page links, calendar links,
  and raw actions.

## Consumer Boundary

PersonaConsole renders escaped, read-only journal pages. Consumers still own entry
lookup, calendar routing, settings persistence, mutations, authorization,
storage, private scope mapping, and any byte or JSON routes.

The default theme is `paper`. Consumers can store a preferred journal theme in
their own console settings and pass the selected key into
`JournalSurfaceConfig(theme=...)`.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.18
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.18.html
PYTHONPATH=src python3 -m compileall src
```
