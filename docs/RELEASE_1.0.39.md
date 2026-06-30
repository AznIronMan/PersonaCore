# PersonaConsole 1.0.39

`1.0.39` expands admin shell branding so consumers can configure header title
text, subtitle text, a title image, and a full lockup image.

## Highlights

- Added `BrandAssets.admin_title`, `BrandAssets.admin_subtitle`, and
  `BrandAssets.lockup_url`.
- Updated `render_shell_html(...)` so a title image replaces the bold title
  while preserving subtitle text, and a full lockup image replaces both text
  lines.
- Expanded the reusable admin branding settings editor with subtitle,
  title-image, and full-lockup fields.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.39
```
