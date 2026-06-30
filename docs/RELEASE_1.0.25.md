# Release 1.0.25

`1.0.25` adds reusable persona editor primitives for consumer admin consoles
that need profile, trait, rule, mutable-state, proposal, and change-history
views without moving persona-specific state or mutation logic into
PersonaConsole.

## Changes

- Added `PersonaEditorConfig`, `PersonaProfileSection`,
  `PersonaProfileField`, `PersonaTraitRow`, `PersonaRuleRow`,
  `PersonaStateField`, `PersonaProposalCard`, and `PersonaChangeRow`.
- Added `PERSONA_EDITOR_FEATURE`, `render_persona_editor(...)`, and
  `persona_editor_feature_enabled(...)`.
- Renders profile sections, trait rows, rule rows, mutable state fields,
  proposal cards, change diffs, status tabs, disabled actions, and action slots.
- Supports owner-private safe alternates for private profile, trait, rule,
  proposal, and change text.
- Keeps secret mutable-state values redacted while allowing safe display and
  pending-display labels.
- Added fixture, static CSS, doctor, import, compatibility shim, and focused
  renderer test coverage.

## Boundaries

PersonaConsole does not contain persona-specific lore, prompts, private
relationship state, validation rules, approval policy, persistence, prompt
assembly, or audit trail writes. Consumers own source-of-truth storage,
validation, approval, persistence, route authorization, and audit logging.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.25
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.25.html
```
