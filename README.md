# PersonaConsole

PersonaConsole is the public, reusable admin console distribution for persona
runtimes. It provides shared layout, navigation, theme tokens, live-refresh
helpers, feature-ready CSS/JS, and rendering primitives so multiple persona
admins can run from one configurable core instead of maintaining forked console
copies.

The public repository and Python distribution are named PersonaConsole. The
canonical import path is `personaconsole`; deprecated `personacore` and
`persona_console` import shims remain during the v1.x rollout so old deployed
consumers do not need a lockstep package rename. A runtime may
present as a focused, branded console, but the common implementation should stay
here when the behavior is reusable.

Public repository:

```text
https://github.com/AznIronMan/PersonaConsole.git
```

## Core Model

PersonaConsole should grow toward a shared feature catalog:

- Admin shell, layout, navigation, status/user pills, and theme tokens.
- Dashboard sections, health/status summaries, review queues, journal readers,
  activity feeds, message/conversation views, media/workflow panels, public
  splash/login/chat surfaces, and live-refresh helpers.
- Feature flags and capability settings that enable, disable, label, reorder,
  and theme modules per runtime.
- Lazy integrations for optional frameworks and template engines.
- Public-safe defaults and examples with no private persona, host, or account
  details.

Each consuming runtime should own its private routes, auth, database access,
secrets, provider credentials, deployment files, and runtime-specific behavior.

## Integration Surfaces

- `personaconsole` is the preferred public import path. `personacore` and
  `persona_console` remain as deprecated compatibility shims during the v1.x
  rollout.
- `personaconsole.render_shell_html(...)` renders a complete page shell for
  admins that build page bodies as trusted HTML strings.
- `personaconsole.render_dashboard_sections(...)` renders generic dashboard
  primitives such as attention cards, filters, metrics, route cards, health
  strips, token health, adapter cards, flow charts, queue summaries, and
  activity rows.
- `personaconsole.dashboard_metrics_from_counts(...)` and
  `personaconsole.render_dashboard_summary_grid(...)` turn consumer-owned count
  or status mappings into reusable dashboard summary cards without moving route,
  database, or runtime ownership into PersonaConsole.
- `personaconsole.TokenHealthConfig` and
  `personaconsole.build_token_health_report(...)` provide an opt-in, redacted
  credential health primitive for provider tokens and webhook secrets. Consumers
  supply their own settings/env lookup and PersonaConsole only reports configured,
  missing, required, and optional states. `personaconsole.TOKEN_HEALTH_FEATURE`
  and `personaconsole.token_health_config_for_providers(...)` give runtimes a
  common feature flag and public provider presets for integrations such as
  Meta, Instagram, X, Discord, and webhooks.
- `personaconsole.AdapterHealthConfig` and
  `personaconsole.render_adapter_health_panel(...)` provide an opt-in adapter and
  runtime health panel for provider routes, recent in/out activity, queue
  counts, policy notes, action hints, and compact sparkline buckets. Consumers
  own the underlying health probes and pass only public-safe display data.
- `personaconsole.MessageSurfaceConfig`,
  `personaconsole.ActivitySurfaceConfig`, `personaconsole.MediaSurfaceConfig`, and
  `personaconsole.render_surface_sections(...)` provide opt-in conversation,
  activity, and media/artifact admin surfaces. The message surface supports
  platform/filter chips, selected-thread metrics, action links, a conversation
  rail, transcript bubbles, attachments, badges, and owner-private redaction.
  Owner-private render helpers can show raw text to the linked owner context
  while rendering safe alternates or withheld placeholders for non-owner
  admins; consumers must still enforce the same policy in their HTML, JSON,
  query, snapshot, and file routes.
- `personaconsole.MediaLibrarySurfaceConfig` and
  `personaconsole.render_media_library_surface(...)` provide a richer
  media/artifact library for grid/list views, preview dialogs, metadata chips,
  safety/sendability flags, review state, non-image fallbacks, and
  runtime-owned upload/import action slots.
- `personaconsole.PeopleSurfaceConfig` and
  `personaconsole.render_people_surface(...)` provide the shared dense people
  table, filter bar, tag chips, relationship summary, notes preview, and
  owner-private note redaction hooks used by consumer-owned people pages.
- `personaconsole.AdminListSurfaceConfig` and
  `personaconsole.render_admin_list_surface(...)` provide reusable dense
  list/table pages with status tabs, filter fields, metric cards, sortable
  headers, row actions, pagination, mobile cards, and owner-private cell
  fallbacks.
- `personaconsole.DetailDossierSurfaceConfig` and
  `personaconsole.render_detail_dossier_surface(...)` provide reusable
  entity-detail pages with headers, metadata fields, metrics, sections, source
  tables, related links, timeline events, audit rows, and runtime-owned action
  slots.
- `personaconsole.ReviewSurfaceConfig` and
  `personaconsole.render_review_surface(...)` provide a shared review-board
  surface for operator-gated decision rows, agenda cards, publishing queue
  summaries, and owner-private safe-alternate summaries.
- `personaconsole.JournalSurfaceConfig` and
  `personaconsole.render_journal_surface(...)` provide a shared journal reader
  with a calendar rail, paper-style default page layout, selectable theme
  catalog, provenance details, page-turn links, and owner-private redaction.
- `personaconsole.BrandAssets`, `personaconsole.PublicMediaConfig`,
  `personaconsole.ConnectorOption`, `personaconsole.ConnectorGroup`, and the public
  renderers `render_public_splash_page(...)`, `render_login_page(...)`,
  `render_chat_page(...)`, and `render_public_settings_surface(...)` provide
  reusable public-facing homepage, login, chat, connector-choice, media hero,
  logo, social-link, legal-modal, and admin settings surfaces. PersonaConsole
  renders escaped generic choices only; consumers and PersonaEngine own
  connector capability truth, auth, OAuth callbacks, provider secrets, chat
  processing, persistence, uploads, and deployment wiring. These surfaces are
  deployment-agnostic: a consumer can export the splash page to a static host
  or CDN while rendering login and chat from separate runtime-owned app
  servers.
- `personaconsole.OperationsSurfaceConfig`,
  `personaconsole.PersonaRuntimeSurfaceConfig`,
  `personaconsole.AgentOpsSurfaceConfig`, and
  `personaconsole.render_workflow_sections(...)` provide shared operations,
  persona-state, continuity, bridge, and agent-session panels. Consumers still
  own task execution, settings mutations, provider calls, and private route
  authorization.
- `personaconsole.BridgeOpsSurfaceConfig` and
  `personaconsole.render_bridge_ops_surface(...)` provide provider-neutral
  bridge operation panels for webhook posture, queues, heartbeats, provider
  capabilities, and delivery claims. Consumers own webhook verification,
  delivery queues, adapter execution, provider API calls, credentials, browser
  profiles, OAuth, and deployment wiring.
- `personaconsole.PersonaEditorConfig` and
  `personaconsole.render_persona_editor(...)` provide a generic editor surface
  for profile sections, traits, rules, mutable state, proposals, and change
  history. PersonaConsole renders supplied state and action slots only;
  consumers own source-of-truth storage, validation, prompt assembly, approval
  policy, persistence, and audit trails.
- `personaconsole.TerminalStreamConfig`,
  `personaconsole.TerminalStreamEvent`, and
  `personaconsole.render_terminal_stream(...)` provide a read-only terminal-style
  current event window with bounded initial history, chunked earlier-history
  hooks, live polling hooks, and owner-private redaction. Consumers own terminal
  capture, retention, stream/history endpoints, auth, and any real command
  execution.
- `personaconsole.SystemHealthSurfaceConfig` and
  `personaconsole.render_system_health_surface(...)` provide a dense shared
  system posture surface for runtime checks, database cards, table summaries,
  audit rows, secret coverage, and readiness probes. PersonaConsole renders
  escaped status data only; consumers own database inspection, probes, audit
  retention, remediation actions, authorization, and redaction policy.
- `personaconsole.StatusTab` and `personaconsole.render_status_tabs(...)` provide a
  shared dense tab control for queue/list status filters while leaving URL
  construction, counts, and filtering semantics in the consuming runtime.
- `personaconsole.FlashBanner`, `personaconsole.render_flash_banners(...)`, and
  `personaconsole.flash_url(...)` provide shared flash/action banner markup and
  redirect query helpers while leaving action routes in the consuming runtime.
- `personaconsole.run_consumer_integration_doctor(...)` verifies consumer installs
  or source mounts by checking version alignment, required shared exports,
  owner-private helpers, token-health helpers, adapter-health helpers,
  availability-monitor helpers, message/media/activity helpers, people helpers,
  review helpers, journal helpers, operations/bridge/persona-editor/
  command-intake helpers, settings/system-health helpers, admin-list and
  detail-dossier helpers, shared controls, and generic render smokes.
- `personaconsole.register_static_assets(app, ...)` mounts shared CSS and JS
  assets in FastAPI apps.
- `personaconsole.configure_jinja_loader(templates)` adds PersonaConsole
  templates/macros to a `Jinja2Templates` instance.

## Package Identity

The public package distribution is `personaconsole`. The sanitized `v1.0.1`
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
operator workspace target. `v1.0.11` extracts the reference-style people page
into a shared typed surface. `v1.0.12` expands the shared message surface into
a denser browser default with filter chips, action links, selected-thread
metrics, and named conversation/transcript columns. `v1.0.13` fixes
adapter-health card markup so linked adapter titles and linked sparkline
buckets remain valid card content instead of breaking browser layout.
`v1.0.14` adds a shared review-board surface for operator-gated decision rows,
agenda cards, publishing queue summaries, and owner-private safe-alternate
rendering. `v1.0.15` adds a shared status-tab control for review queues and
filtered list pages. `v1.0.16` adds shared flash/action banners, redirect
query helpers, and PersonaConsole class hooks for live-refresh controls.
`v1.0.17` adds operations, persona runtime, continuity, bridge, and agent-ops
surfaces. `v1.0.18` adds a shared themed journal reader with calendar
navigation, paper-style default rendering, and owner-private safe alternates.
`v1.0.19` adds reusable public presence surfaces for branded splash, login,
chat, connector choices, configurable media heroes, and the admin settings
form. `v1.0.20` polishes public presence visual defaults for connector
buttons, fallback logos, and split static/app-server deployments. `v1.0.21`
renames the distribution and canonical import to `personaconsole` while keeping
deprecated `personacore` and `persona_console` shims for rollout safety.
  `v1.0.22` adds a read-only terminal stream renderer for bounded current agent
activity windows with chunked history/live-update hooks. `v1.0.23` adds a
shared settings editor surface for grouped runtime-owned fields, redacted
values, validation summaries, pending-change previews, restart markers, and
consumer-supplied action slots, plus reusable admin branding fields for an
optional header icon/wordmark. `v1.0.24` adds a system health surface for
runtime checks, database posture, table summaries, audit events, secret
coverage, and readiness probes. `v1.0.25` adds generic persona editor
primitives for profile sections, traits, rules, mutable state, proposals, and
change history. `v1.0.26` adds bridge operation panels for provider-neutral
webhooks, queues, heartbeats, capabilities, and delivery claims. `v1.0.27`
adds a command intake preview surface for parsed commands, target candidates,
risk checks, confirmation gates, queue posture, and sanitized history.
`v1.0.28` adds an availability monitor surface for schedule windows, live
checks, policy posture, scenario QA, and sanitized monitor events. `v1.0.29`
adds a generic admin-list/table surface for dense filtered list pages.
`v1.0.30` adds a detail/dossier surface for reusable entity detail pages.
`v1.0.31` adds a media/artifact library surface for reusable asset galleries,
review queues, metadata chips, preview dialogs, and runtime-owned import
actions.

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
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.31
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
scripts/export_public_baseline.sh /tmp/personaconsole-public-baseline
```

Review the exported tree before creating fresh public git history. The export
script prints the tag matching the exported package version.

## Docs

- [PersonaConsole Direction](docs/PERSONACONSOLE_DIRECTION.md)
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
- [Release 1.0.11](docs/RELEASE_1.0.11.md)
- [Release 1.0.12](docs/RELEASE_1.0.12.md)
- [Release 1.0.13](docs/RELEASE_1.0.13.md)
- [Release 1.0.14](docs/RELEASE_1.0.14.md)
- [Release 1.0.15](docs/RELEASE_1.0.15.md)
- [Release 1.0.16](docs/RELEASE_1.0.16.md)
- [Release 1.0.17](docs/RELEASE_1.0.17.md)
- [Release 1.0.18](docs/RELEASE_1.0.18.md)
- [Release 1.0.19](docs/RELEASE_1.0.19.md)
- [Release 1.0.20](docs/RELEASE_1.0.20.md)
- [Release 1.0.21](docs/RELEASE_1.0.21.md)
- [Release 1.0.22](docs/RELEASE_1.0.22.md)
- [Release 1.0.23](docs/RELEASE_1.0.23.md)
- [Release 1.0.24](docs/RELEASE_1.0.24.md)
- [Release 1.0.25](docs/RELEASE_1.0.25.md)
- [Release 1.0.26](docs/RELEASE_1.0.26.md)
- [Release 1.0.27](docs/RELEASE_1.0.27.md)
- [Release 1.0.28](docs/RELEASE_1.0.28.md)
- [Release 1.0.29](docs/RELEASE_1.0.29.md)
- [Release 1.0.30](docs/RELEASE_1.0.30.md)
- [Release 1.0.31](docs/RELEASE_1.0.31.md)
- [Visual QA](docs/VISUAL_QA.md)
- [Public Release And Sanitization](docs/PUBLIC_RELEASE.md)
- [Settled Direction And Open Questions](docs/OPEN_QUESTIONS.md)

## Fixture App

The `examples/` directory includes a generic fixture admin console for public
examples and future screenshot QA.

```bash
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture.html
```

When FastAPI and Uvicorn are installed:

```bash
PYTHONPATH=src python3 -m uvicorn examples.fixture_app:create_app --factory --reload
```
