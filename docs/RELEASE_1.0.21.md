# Release 1.0.21

`1.0.21` renames the Python distribution and canonical import path to
`personaconsole`.

## Changes

- Changed package metadata from `personacore` to `personaconsole`.
- Moved the canonical implementation package from `persona_console` to
  `personaconsole`.
- Kept deprecated `personacore` and `persona_console` re-export shims for v1.x
  rollout compatibility.
- Updated the consumer integration doctor, examples, tests, and public docs to
  treat `personaconsole` as canonical.

## Consumer Boundary

Consumers should import `personaconsole` and pin the `personaconsole`
distribution from the PersonaConsole repository. The old import shims are only
for deployed-code compatibility and should not be used by new consumer source.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.21
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.21.html
PYTHONPATH=src python3 -m compileall src
```
