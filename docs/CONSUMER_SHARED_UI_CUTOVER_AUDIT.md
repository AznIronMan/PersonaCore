# Consumer Shared UI Cutover Audit

PersonaConsole includes an optional audit for consumer repositories that are
moving copied or hardcoded Admin UI into shared PersonaConsole surfaces.

Run it from the PersonaConsole checkout:

```bash
PYTHONPATH=src python3 scripts/consumer_shared_ui_cutover_audit.py /path/to/consumer
```

The audit is public-safe by design. It skips `.private/`, `.env*`, virtualenvs,
build outputs, caches, and common runtime data folders. It reports relative
paths only.

## What It Detects

- Deprecated compatibility imports or dependency pins such as `personacore` and
  `persona_console`.
- Local shared fallback markers such as copied “PersonaConsole unavailable”
  fallbacks that should now be archived or intentionally runtime-owned.
- Generic UI helper definitions that often indicate reusable table, filter,
  pagination, nav, badge, or status-pair code still living in the consumer.
- Copied PersonaConsole static assets instead of serving package assets.
- Missing surface-composition registry markers.

Findings are intentionally advisory except hard legacy import/pin usage and a
missing surface registry, which are errors by default.

## Ignore Lists

Consumers may keep runtime-owned forms, details, route handlers, auth, database
queries, mutations, provider calls, and deployment controls local. Use ignores
for those intentional cases.

Line-based ignore file:

```text
# key:path
duplicated-generic-helper:app/admin.py
fallback:app/admin.py
```

JSON ignore file:

```json
{
  "ignore_patterns": [
    "duplicated-generic-helper:app/admin.py",
    "fallback:app/admin.py"
  ]
}
```

TOML ignore file:

```toml
[cutover_audit]
ignore_patterns = [
  "duplicated-generic-helper:app/admin.py",
  "fallback:app/admin.py",
]
```

Patterns are glob-style and can match `key:path`, `category:path`, `level:path`,
`key`, `category`, or `path`.

## Expected Evidence

Consumer repos should record their own final evidence:

- local tests and focused Admin render tests;
- PersonaConsole consumer integration doctor;
- cutover audit output with any runtime-owned ignores explained;
- fixture or protected Admin render smoke;
- static asset route smoke;
- private/raw leakage scan where applicable;
- live route smoke and launch/deploy check in the owning runtime repo.

PersonaConsole does not decide whether a consumer-specific UI block is allowed
to remain local. The consumer task should document that ownership decision.
