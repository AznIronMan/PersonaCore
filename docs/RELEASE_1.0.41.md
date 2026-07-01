# PersonaConsole 1.0.41

`1.0.41` lets admin-login consumers preserve pre-validated absolute return
URLs when an external login service hands back to a separate admin console
origin, and lets command-intake consumers mount runtime-owned controls through
shared action slots.

## Highlights

- Added `allowed_next_origins` to `AdminLoginPageConfig`.
- Kept absolute `next` URLs blocked by default unless the consumer opts into
  specific `http` or `https` origins.
- Preserved existing blocked-login path protection for root-relative and
  allowed absolute URLs.
- Added `CommandIntakeActionSlot`, `CommandIntakeSurfaceConfig.action_slots`,
  and `show_form=False` support so consumers can render their own validated
  forms or panels inside the shared command-intake surface without rewriting
  PersonaConsole-generated HTML.
- Added `MediaLibraryItem.detail_html` so consumers can keep local review
  controls beside shared media cards while PersonaConsole owns the reusable
  gallery/list shell.
- Added a sanitized consumer release propagation guide plus a local-only roster
  checklist helper that refuses to write private rollout plans outside
  `.private/`.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.41
```
