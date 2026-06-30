# Release 1.0.10

`1.0.10` adds a public-safe reference admin parity spec and expands the generic
fixture admin into a fuller operator workspace target.

## Changes

- Added `docs/REFERENCE_ADMIN_PARITY_SPEC.md` to define the shared admin
  composition target for consumer runtimes without naming private projects,
  hosts, paths, accounts, screenshots, or deployment details.
- Expanded the public fixture shell with grouped overview, conversations,
  operations, and system navigation.
- Added generic people, task, log, and settings posture fixture panels so
  consumer runtimes have a clearer reference for making their admins feel
  aligned without copying private runtime code.
- Updated fixture theme tokens and dashboard data to show a fuller first
  viewport with attention, route filters, metrics, service health, adapters,
  flow, queue, activity, messages, media, and owner-private redaction examples.
- Added small shared CSS polish for compact headings, preformatted log blocks,
  and reference workspace spacing.

## Compatibility

- The Python package remains `personaconsole`, with `personaconsole` kept as the
  compatibility import path.
- No private runtime data, routes, auth policy, secrets, or deployment state
  were added to PersonaConsole.
- The new fixture panels are static example HTML composed with existing shared
  primitives. Consumers still own real people, task, log, settings, mutation,
  and authorization behavior.

## Verification

```bash
PYTHONPATH=src python -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.10
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture.html
PYTHONPATH=src python3 scripts/visual_smoke.py
```
