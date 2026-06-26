# PersonaCore

PersonaCore is the public, reusable admin console distribution for persona
runtimes. It provides shared layout, navigation, theme tokens, live-refresh
helpers, feature-ready CSS/JS, and rendering primitives so multiple persona
admins can run from one configurable core instead of maintaining forked console
copies.

The current Python package is named `persona_console`. The broader project
direction is PersonaCore: a complete admin distro where each runtime turns
features on or off through settings and capability flags. A runtime may present
as a focused, branded console, but the common implementation should stay here
when the behavior is reusable.

Public repository:

```text
https://github.com/AznIronMan/PersonaCore.git
```

## Core Model

PersonaCore should grow toward a shared feature catalog:

- Admin shell, layout, navigation, status/user pills, and theme tokens.
- Dashboard sections, health/status summaries, review queues, activity feeds,
  message/conversation views, media/workflow panels, and live-refresh helpers.
- Feature flags and capability settings that enable, disable, label, reorder,
  and theme modules per runtime.
- Lazy integrations for optional frameworks and template engines.
- Public-safe defaults and examples with no private persona, host, or account
  details.

Each consuming runtime should own its private routes, auth, database access,
secrets, provider credentials, deployment files, and runtime-specific behavior.

## Integration Surfaces

- `personacore` is the preferred public import path. `persona_console` remains
  available as the current compatibility import path.
- `persona_console.render_shell_html(...)` renders a complete page shell for
  admins that build page bodies as trusted HTML strings.
- `personacore.render_dashboard_sections(...)` renders generic dashboard
  primitives such as attention cards, filters, metrics, route cards, health
  strips, token health, adapter cards, flow charts, queue summaries, and
  activity rows.
- `personacore.dashboard_metrics_from_counts(...)` and
  `personacore.render_dashboard_summary_grid(...)` turn consumer-owned count
  or status mappings into reusable dashboard summary cards without moving route,
  database, or runtime ownership into PersonaCore.
- `personacore.TokenHealthConfig` and
  `personacore.build_token_health_report(...)` provide an opt-in, redacted
  credential health primitive for provider tokens and webhook secrets. Consumers
  supply their own settings/env lookup and PersonaCore only reports configured,
  missing, required, and optional states. `personacore.TOKEN_HEALTH_FEATURE`
  and `personacore.token_health_config_for_providers(...)` give runtimes a
  common feature flag and public provider presets for integrations such as
  Meta, Instagram, X, Discord, and webhooks.
- `personacore.AdapterHealthConfig` and
  `personacore.render_adapter_health_panel(...)` provide an opt-in adapter and
  runtime health panel for provider routes, recent in/out activity, queue
  counts, policy notes, action hints, and compact sparkline buckets. Consumers
  own the underlying health probes and pass only public-safe display data.
- `personacore.MessageSurfaceConfig`,
  `personacore.ActivitySurfaceConfig`, `personacore.MediaSurfaceConfig`, and
  `personacore.render_surface_sections(...)` provide opt-in conversation,
  activity, and media/artifact admin surfaces. Owner-private render helpers can
  show raw text to the linked owner context while rendering safe alternates or
  withheld placeholders for non-owner admins; consumers must still enforce the
  same policy in their HTML, JSON, query, snapshot, and file routes.
- `personacore.run_consumer_integration_doctor(...)` verifies consumer installs
  or source mounts by checking version alignment, required shared exports,
  owner-private helpers, token-health helpers, adapter-health helpers,
  message/media/activity helpers, and a generic render smoke.
- `persona_console.register_static_assets(app, ...)` mounts shared CSS and JS
  assets in FastAPI apps.
- `persona_console.configure_jinja_loader(templates)` adds PersonaCore
  templates/macros to a `Jinja2Templates` instance.

## Package Identity

The public package distribution is `personacore`. The sanitized `v1.0.1`
baseline starts the public history, `v1.0.2` adds configurable token health as
a shared feature primitive, `v1.0.3` carries public-safe export workflow
cleanup, `v1.0.4` adds reusable dashboard summary-card helpers for consumer
deduplication, `v1.0.5` adds generic owner-private admin visibility helpers
for runtime-enforced privacy, `v1.0.6` adds token-health feature gating and
public provider presets, `v1.0.7` adds the consumer integration doctor for
upgrade/restart smokes, and `v1.0.8` adds adapter/runtime health cards as an
opt-in shared module. `v1.0.9` adds reusable message, activity, and
media/artifact surfaces with owner-private redaction hooks. `v1.0.10` adds a
public-safe reference admin parity spec and expands the fixture into a fuller
operator workspace target. The existing `persona_console` Python package
remains in the source tree as a compatibility implementation path for v1.x
consumers.

## Public Safety

This repo targets a public GitHub upstream. Tracked files must remain sanitized:

- Do not commit private project names, character names, hostnames, local paths,
  account IDs, deployment state, credentials, `.env` files, browser profiles,
  generated media, runtime databases, or private task notes.
- Keep local deployment mappings in ignored `.private/` notes.
- Use generic examples such as `example-persona`, `operator`, `runtime`, and
  `consumer`.
- Do not push the existing local history directly to the public repo if it
  contains private handoff details. Publish from a fresh sanitized history or
  after an explicit history rewrite and audit.
- `AGENTS.md` is local operator guidance and is intentionally excluded from the
  public distribution.

## Local Verification

From this directory:

```bash
PYTHONPATH=src python -m pytest tests
```

Use Python 3.11+ with the package's test dependencies installed. For consuming
runtime changes, follow the owning runtime's `AGENTS.md`, task tracker,
verification, and deployment rules.

Consumer integration doctor:

```bash
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.10
```

Use `--json` for automation. Imported module filesystem paths are hidden unless
`--show-paths` is passed.

Optional fixture visual smoke:

```bash
python3 -m pip install -e ".[visual]"
python3 -m playwright install chromium
PYTHONPATH=src python3 scripts/visual_smoke.py
```

## Public Export

Create a fresh public-safe tree with:

```bash
scripts/export_public_baseline.sh /tmp/personacore-public-baseline
```

Review the exported tree before creating fresh public git history. The export
script prints the tag matching the exported package version.

## Docs

- [PersonaCore Direction](docs/PERSONACORE_DIRECTION.md)
- [Configuration Model](docs/CONFIGURATION_MODEL.md)
- [Feature Extraction Plan](docs/FEATURE_EXTRACTION_PLAN.md)
- [Reference Admin Parity Spec](docs/REFERENCE_ADMIN_PARITY_SPEC.md)
- [Reference Console Backlog](docs/REFERENCE_CONSOLE_BACKLOG.md)
- [Release 1.0.2](docs/RELEASE_1.0.2.md)
- [Release 1.0.3](docs/RELEASE_1.0.3.md)
- [Release 1.0.4](docs/RELEASE_1.0.4.md)
- [Release 1.0.5](docs/RELEASE_1.0.5.md)
- [Release 1.0.6](docs/RELEASE_1.0.6.md)
- [Release 1.0.7](docs/RELEASE_1.0.7.md)
- [Release 1.0.8](docs/RELEASE_1.0.8.md)
- [Release 1.0.9](docs/RELEASE_1.0.9.md)
- [Release 1.0.10](docs/RELEASE_1.0.10.md)
- [Visual QA](docs/VISUAL_QA.md)
- [Public Release And Sanitization](docs/PUBLIC_RELEASE.md)
- [Settled Direction And Open Questions](docs/OPEN_QUESTIONS.md)

## Fixture App

The `examples/` directory includes a generic fixture admin console for public
examples and future screenshot QA.

```bash
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personacore-fixture.html
```

When FastAPI and Uvicorn are installed:

```bash
PYTHONPATH=src python3 -m uvicorn examples.fixture_app:create_app --factory --reload
```
