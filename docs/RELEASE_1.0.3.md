# PersonaConsole 1.0.3

Released: 2026-06-24

`1.0.3` is a public-safe patch release over `1.0.2`. It keeps the token health
feature behavior stable while carrying the latest sanitized export workflow and
documentation cleanup.

## Changes

- Kept token health reports focused on `label` and `key` fields without the
  extra legacy `name` alias in generated report rows.
- Updated public export guidance so the printed tag follows the package
  version instead of embedding an older release tag.
- Updated public release documentation to point consumers at the current
  versioned tag.
- Kept the public package metadata and runtime `__version__` aligned.

## Verification

- `PYTHONPATH=src python3 -m pytest tests`
- Sanitized export plus package tests from the exported tree.
