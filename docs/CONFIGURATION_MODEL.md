# Configuration Model

PersonaCore should use configuration to make one distro fit many runtimes.
Configuration should be explicit, typed where practical, and safe to expose in
public examples.

## Layers

- `PersonaCoreConfig` or the current compatibility `PersonaConsoleConfig`:
  shell-level configuration for brand label, page title, nav, badges, status
  pills, user pill, theme, static paths, live refresh, and layout width.
- Feature settings: runtime-level switches that decide which shared modules are
  mounted or rendered.
- Capability flags: facts about what the runtime can do, such as whether it has
  conversations, media, review queues, workers, scheduling, or external adapter
  health.
- Feature-specific settings: opt-in module configuration such as token health
  checks, labels, required/optional state, and runtime-owned data lookups.
- Data providers: runtime-owned callables or routes that supply rows, counts,
  summaries, and partial refresh fragments to shared render primitives.

## Public Example Shape

```python
from persona_console import NavGroup, NavItem, PersonaConsoleConfig

config = PersonaConsoleConfig(
    brand_name="Example Persona",
    page_title="Dashboard",
    page_subtitle="Runtime overview",
    active="dashboard",
    nav_groups=[
        NavGroup(
            "Core",
            [
                NavItem("Dashboard", "/", active="dashboard"),
                NavItem("Messages", "/messages", active="messages"),
            ],
        ),
        NavGroup(
            "Review",
            [
                NavItem("Queue", "/review", active="review", badge="review"),
            ],
        ),
    ],
    nav_badges={"review": 3},
)
```

Public examples must remain generic. Private consumers can inject private
labels, paths, and data at runtime from their own repositories.

As the public API moves to PersonaCore naming, examples should prefer:

```python
from personacore import NavGroup, NavItem, PersonaCoreConfig
```

The older `persona_console` path should remain available as a compatibility
alias during the v1.x transition.

## Format Recommendation

Use typed Python dataclasses and plain dictionaries as the primary runtime
configuration model. They are fast, dependency-light, easy to construct from
consumer code, and compatible with all current Python runtime styles.

Support optional JSON loading through the standard library for deployments that
want declarative files. Avoid mandatory YAML, Pydantic, or other heavy
configuration dependencies in the core import path. If richer validation is
needed later, keep it optional.

## Feature Flag Direction

Future shared configuration should make common feature modules selectable:

```python
features = {
    "adapter_health": False,
    "dashboard": True,
    "messages": True,
    "media": False,
    "owner_private_admin": False,
    "review": True,
    "token_health": False,
    "workers": False,
    "scheduling": False,
}
```

Feature flags should hide navigation and UI modules by default when disabled.
They should not import optional dependencies or private adapters unless the
feature is enabled and the consumer provides the integration.

Navigation items may declare a `feature` key. PersonaCore hides feature-gated
navigation when that feature is disabled or absent. This is only a UI/module
switch; consumers must still enforce permissions in their own server routes.

## Reference Admin Parity Fixture

`examples/fixture_app.py` is the public-safe reference fixture for consumer
alignment. It shows how one `PersonaCoreConfig` can present a fuller admin
workspace with grouped overview, conversations, operations, and system
navigation while still keeping all real routes and data consumer-owned.

Use the fixture as a configuration target when making consumer admins feel
consistent:

- Enable only the modules the runtime actually supports.
- Keep local labels, hrefs, status pills, badges, and theme tokens in the
  consumer repo.
- Feed shared render primitives with safe counts, summaries, and status data.
- Keep route auth, mutation policy, database queries, secrets, restart
  controls, and owner-private scope aliases outside PersonaCore.

See [Reference Admin Parity Spec](REFERENCE_ADMIN_PARITY_SPEC.md) for the
shared composition contract.

## Owner-Private Visibility

Owner-private visibility is a shared, opt-in policy helper for content that only
the linked owner account should see raw. PersonaCore provides generic policy and
rendering primitives; consuming runtimes provide their own scope names, aliases,
person mappings, database filters, and file-route checks.

```python
from personacore import AdminPrivacyContext, OwnerPrivateScopePolicy, render_private_text

policy = OwnerPrivateScopePolicy(
    owner_private_scopes={"owner_private": ["owner"]},
    aliases={"master_private": "owner_private"},
)
context = AdminPrivacyContext(
    access_tier="operator",
    viewer_person_key="operator",
    allowed_scopes=["public", "operator"],
)

text = render_private_text(
    "raw note text",
    safe_alternate="operator-safe summary",
    policy=policy,
    context=context,
    scope="owner_private",
)
```

The `owner_private_admin` feature flag controls whether a runtime exposes
owner-private admin panels. It does not disable server-side protection. JSON
endpoints, HTML snapshots, and artifact/media byte routes should all call the
same runtime policy before returning raw owner-private data.

## Token Health

Token health is a shared, opt-in feature. PersonaCore should not read private
`.env` files or runtime databases on its own. A consuming runtime enables the
feature, names the checks it wants to expose, and passes a settings/env mapping
or lookup callable into the redacted report builder.

```python
from personacore import TokenHealthCheck, TokenHealthConfig, build_token_health_report

token_health = TokenHealthConfig(
    enabled=True,
    checks=[
        TokenHealthCheck(
            "social_api",
            "Social API token",
            "Social",
            ["SOCIAL_API_TOKEN"],
            required=True,
        ),
        TokenHealthCheck(
            "webhook_verify",
            "Webhook verify token",
            "Webhooks",
            ["WEBHOOK_VERIFY_TOKEN"],
            required=False,
        ),
    ],
)

report = build_token_health_report(token_health, values=runtime_settings)
```

The returned report is safe to render or expose through an admin health route:
raw values are never copied into the report. Consumers may hide secret key names
with `TokenHealthConfig(show_secret_names=False)` when even source names should
stay runtime-local.

Runtimes that use the shared feature map can gate the module with
`features["token_health"]`. An explicit `False` hides the shared panel even when
the config is otherwise enabled; route handlers and background checks remain
owned by the consumer runtime.

For common public providers, consumers can start from sanitized presets and
override source names locally:

```python
from personacore import (
    TOKEN_HEALTH_FEATURE,
    build_token_health_report,
    token_health_config_for_providers,
)

features = {TOKEN_HEALTH_FEATURE: True}
token_health = token_health_config_for_providers(
    ["meta", "instagram", "x", "discord"],
    show_secret_names=False,
    overrides={
        "x": {"secret_names": ["RUNTIME_X_TOKEN"], "required": False},
    },
)

report = build_token_health_report(
    token_health,
    values=runtime_settings,
    features=features,
)
```

Built-in provider presets are public labels only. Runtime-specific aliases,
credential names, validation calls, token refresh state, and health routes
should stay in the consumer repository.

## Adapter Health

Adapter health is a shared, opt-in feature for runtime-owned provider, route,
queue, worker, and policy status. PersonaCore renders the cards and summary
shell; consuming runtimes own the actual checks and pass only display-safe data.

```python
from personacore import AdapterHealthCard, AdapterHealthConfig, AdapterHealthSparkBucket

adapter_health = AdapterHealthConfig(
    enabled=True,
    cards=[
        AdapterHealthCard(
            "Messages",
            "healthy",
            href="/messages",
            tone="good",
            route="inbound/outbound",
            policy="reply route enabled",
            last_in="2m ago",
            last_out="1m ago",
            counts=[{"label": "0 failed", "tone": "good"}],
            sparkline=[AdapterHealthSparkBucket("now", 76, tone="good")],
        )
    ],
)
```

`features["adapter_health"] = False` hides the shared panel when a runtime wants
to keep the module off. The flag does not grant health-probe permissions,
restart rights, or provider access; those remain runtime-owned.

## Message, Activity, And Media Surfaces

Message, activity, and media/artifact surfaces are shared, opt-in UI modules
for consumer-owned data. PersonaCore renders the shell, lists, transcript
bubbles, attachment chips, activity rows, media cards, badges, and empty states;
the consuming runtime still owns the queries, route authorization, file byte
serving, and mutation endpoints.

```python
from personacore import (
    MESSAGES_FEATURE,
    AdminPrivacyContext,
    DashboardAction,
    DashboardFilter,
    DashboardMetric,
    MessageConversation,
    MessageSurfaceConfig,
    MessageTranscriptItem,
    OwnerPrivateScopePolicy,
    render_message_surface,
)

policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
context = AdminPrivacyContext(
    access_tier="operator",
    viewer_person_key="operator",
    allowed_scopes=("public", "operator"),
)

html = render_message_surface(
    MessageSurfaceConfig(
        enabled=True,
        filters=[
            DashboardFilter("All", "/messages", key="12", active=True),
            DashboardFilter("Direct", "/messages?platform=direct", key="5"),
        ],
        metrics=[
            DashboardMetric("Threads", 2, "/messages", "current filter"),
            DashboardMetric("Unread", 2, "/messages?unread=1", "needs pass", tone="warn"),
        ],
        actions=[DashboardAction("Raw rows", "/messages?view=raw")],
        conversations=[
            MessageConversation(
                "thread-1",
                "Example thread",
                summary="raw owner-private text",
                safe_alternate="Operator-safe summary",
                privacy_scope="owner_private",
            )
        ],
        transcript=[
            MessageTranscriptItem(
                "Owner",
                "raw owner-private message",
                safe_alternate="Operator-safe message summary",
                privacy_scope="owner_private",
            )
        ],
        conversation_title="Threads",
        transcript_title="Selected conversation",
        transcript_meta="current page",
    ),
    features={MESSAGES_FEATURE: True},
    privacy_policy=policy,
    privacy_context=context,
)
```

If a row or card declares a privacy scope and no policy is supplied,
PersonaCore fails closed: it renders the safe alternate when present, otherwise
a withheld placeholder, and it strips raw href/preview URLs from the shared
HTML. This is a UI safeguard, not a substitute for server enforcement. Consumer
HTML snapshots, JSON endpoints, database queries, and media/artifact byte
routes must apply the same runtime policy before returning raw owner-private
data.

## People Surface

The people surface is a shared, opt-in module for canonical person lists,
reference-style filtering, tags, relationship summaries, and notes previews.
The consuming runtime owns person lookup, auth, create/edit routes, aliases,
database schema, and any private tier mapping.

```python
from personacore import (
    PEOPLE_FEATURE,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    PeopleSurfaceConfig,
    PersonListRow,
    PersonRelationshipSummary,
    PersonTag,
    render_people_surface,
)

policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
context = AdminPrivacyContext(access_tier="operator", viewer_person_key="operator")

html = render_people_surface(
    PeopleSurfaceConfig(
        enabled=True,
        search_action="/people",
        rows=[
            PersonListRow(
                "person-1",
                "Example Person",
                external_id="CN0001",
                trust_label="internal",
                tags=[PersonTag("supportive", tone="good")],
                relationship=PersonRelationshipSummary(
                    label="Persona",
                    score="+42",
                    tone="good",
                    score_percent=71,
                ),
                notes="Operator-visible summary",
            )
        ],
    ),
    features={PEOPLE_FEATURE: True},
    privacy_policy=policy,
    privacy_context=context,
)
```

Rows with `notes_privacy_scope` use the same owner-private rendering contract
as messages and media: owner contexts can see raw notes for their matching
scope, while operators and moderators receive safe alternates or withheld
placeholders. This protects the shared HTML render only; consumer JSON,
snapshot, query, and file routes must enforce the same policy before returning
raw private data.

## Review Surface

The review surface is a shared, opt-in module for operator-gated decision
boards. Consumers provide the normalized rows, agenda routes, queue summaries,
filters, actions, and authorization; PersonaCore renders the scan-friendly
surface and applies safe-alternate owner-private summaries where configured.

```python
from personacore import (
    REVIEW_FEATURE,
    AdminPrivacyContext,
    DashboardFilter,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    ReviewAgendaItem,
    ReviewBoardRow,
    ReviewQueueCard,
    ReviewQueueSection,
    ReviewSurfaceConfig,
    render_review_surface,
)

policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
context = AdminPrivacyContext(access_tier="operator", viewer_person_key="operator")

html = render_review_surface(
    ReviewSurfaceConfig(
        enabled=True,
        filters=[DashboardFilter("All", "/review", key="8", active=True)],
        metrics=[DashboardMetric("Pending", 8, "/review?status=pending", tone="warn")],
        rows=[
            ReviewBoardRow(
                "message",
                "held",
                "messages:owner-private",
                summary="raw owner-private review note",
                summary_safe_alternate="Operator-safe review summary",
                summary_privacy_scope="owner_private",
                href="/messages/private-row",
                risk="bad",
            )
        ],
        agenda=[
            ReviewAgendaItem("Messages", 2, "/review/messages", "queue", "Inspect safe summaries", "warn"),
        ],
        queue_sections=[
            ReviewQueueSection(
                "Publishing Queues",
                cards=[
                    ReviewQueueCard("Draft post", status="pending", href="/review/social", summary="Ready for review"),
                ],
            )
        ],
    ),
    features={REVIEW_FEATURE: True},
    privacy_policy=policy,
    privacy_context=context,
)
```

If a review row or queue card declares a privacy scope, the shared renderer
strips raw links for non-owner contexts and renders the configured safe
alternate or withheld placeholder. Consumer HTML snapshots, JSON endpoints,
database queries, and action routes must still enforce the same policy.

## Shared Controls

Shared controls are small UI primitives that keep list and queue pages visually
consistent without moving URL construction, database filters, or authorization
into PersonaCore.

```python
from personacore import StatusTab, render_status_tabs

html = render_status_tabs(
    [
        StatusTab("All", "/review", 12, active=True),
        StatusTab("Pending", "/review?status=pending", 3, tone="warn"),
        {"label": "Approved", "href": "/review?status=approved", "count": 8, "tone": "good"},
    ],
    aria_label="Review status",
)
```

`render_status_tabs(...)` emits both the generic PersonaCore classes
(`pc-status-tabs`, `pc-status-tab`, `pc-status-tab-count`) and the legacy class
hooks (`status-tabs`, `status-tab`, `status-tab-count`) so consumers can migrate
page by page without breaking existing admin tests or styles.

Flash and action banners share the same incremental migration approach:

```python
from personacore import FlashBanner, flash_url, render_flash_banners

html = render_flash_banners(
    [
        FlashBanner(
            "Settings saved.",
            tone="good",
            action_label="Review changes",
            action_href="/settings?tab=audit",
        )
    ]
)
redirect_to = flash_url("/settings#runtime", "Settings saved.", level="good")
```

`render_flash_banners(...)` emits `pc-flash-*` classes alongside the legacy
`flash-*` hooks. `flash_url(...)` only appends the shared `flash`,
`flash_level`, and `flash_ts` query parameters; consumers still own redirects,
mutations, permissions, and action targets.

## Consumer Integration Doctor

After changing a consumer's installed package, checked-out tag, source mount, or
service image, run the generic doctor before deeper runtime-specific smokes:

```bash
PYTHONPATH=/path/to/personacore/src python3 /path/to/personacore/scripts/consumer_integration_doctor.py --expected-version 1.0.16
```

The doctor verifies that `persona_console` and `personacore` import, report the
same version, expose adapter-health, token-health, owner-private, and
message/activity/media/people/review helpers plus shared controls, and can
render a generic shell plus redacted feature panels. It does not read runtime
secrets, databases, private routes, or consumer settings. Filesystem paths are
omitted from output unless `--show-paths` is explicitly passed for local
diagnostics.

## Dashboard Summary Cards

Repeated count/status cards should stay generic. Consumers own the underlying
database queries, routes, and labels, then pass a safe mapping plus display
specs into PersonaCore:

```python
from personacore import DashboardMetricSpec, render_dashboard_summary_grid

html = render_dashboard_summary_grid(
    {"messages": 42, "review_pending": 3, "provider": "example-provider"},
    [
        DashboardMetricSpec("Messages", "messages", "/messages", value_kind="count"),
        DashboardMetricSpec("Review", "review_pending", "/review", value_kind="count"),
        DashboardMetricSpec("Provider", "provider", "/runtime/provider", value_kind="text"),
    ],
)
```

This keeps route ownership and data access in the consumer while removing
duplicated summary-card markup.

## Extension Rules

- Prefer adding a generic capability or data provider over adding
  persona-specific branching.
- Keep render helpers tolerant of missing optional data.
- Keep runtime-owned mutation endpoints in the consumer app unless the mutation
  is truly generic.
- Keep secret-bearing and deployment-specific behavior out of PersonaCore.
