# PersonaConsole 1.0.37

`1.0.37` adds optional public-safe consumer cutover audit tooling for runtimes
that are finishing migration from local shared Admin UI into PersonaConsole.

## Changes

- Added `personaconsole.cutover_audit` with:
  - `run_consumer_shared_ui_cutover_audit(...)`
  - `cutover_audit_report_to_text(...)`
  - `load_cutover_audit_ignore_patterns(...)`
  - `CutoverAuditFinding`
  - `CutoverAuditReport`
- Added `scripts/consumer_shared_ui_cutover_audit.py`.
- Detects deprecated compatibility names, local shared fallback markers,
  duplicated generic UI helpers, copied PersonaConsole static assets, and
  missing surface-registry declarations.
- Supports `--ignore`, JSON/TOML/line-based `--ignore-file`, `--json`, and
  `--fail-on`.
- Added legacy submodule shims for compatibility imports.
- Documented the consumer evidence expected for a final shared-UI cutover audit.

## Boundaries

The audit never edits consumer code, reads ignored private/runtime directories,
connects to deployments, inspects databases, or decides consumer ownership.
Runtime-specific forms, auth, route handlers, data access, mutations, provider
calls, and deployment controls remain consumer-owned.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests/test_cutover_audit.py tests/test_imports.py tests/test_doctor.py -q
PYTHONPATH=src python3 -m pytest tests -q
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.37
PYTHONPATH=src python3 scripts/consumer_shared_ui_cutover_audit.py /tmp/example-consumer --json
./scripts/export_public_baseline.sh /tmp/personaconsole-public-1.0.37
node --check src/personaconsole/static/persona-console.js
PYTHONPATH=src python3 scripts/visual_smoke.py --output-dir build/visual-smoke
```
