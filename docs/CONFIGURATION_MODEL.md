# Configuration Model

PersonaConsole should use configuration to make one distro fit many runtimes.
Configuration should be explicit, typed where practical, and safe to expose in
public examples.

## Layers

- `PersonaConsoleConfig` or the current compatibility `PersonaConsoleConfig`:
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
from personaconsole import NavGroup, NavItem, PersonaConsoleConfig

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

As the public API moves to PersonaConsole naming, examples should prefer:

```python
from personaconsole import NavGroup, NavItem, PersonaConsoleConfig
```

The older `personaconsole` path should remain available as a compatibility
alias during the v1.x transition.

## Live Refresh And Partials

`LiveRefreshConfig` defines the shared shell contract for polling a
consumer-owned partial endpoint. PersonaConsole renders controls, target data
attributes, stale/error classes, and the browser-side replacement behavior. The
consumer runtime still owns the route, auth, rate limits, data queries, and the
HTML fragment returned by that route.

```python
from personaconsole import LiveRefreshConfig, PersonaConsoleConfig

config = PersonaConsoleConfig(
    brand_name="Example Persona",
    page_title="Dashboard",
    live_refresh=LiveRefreshConfig(
        enabled=True,
        key="dashboard",
        url="/fragments/dashboard",
        interval_seconds=30,
        interval_options=(10, 30, 60),
        hold_selector="[data-live-hold]",
        stale_after_seconds=120,
        fallback_href="/dashboard",
    ),
)
```

For compatibility, older `live_url`, `live_interval`, and
`live_hold_selector` fields still render the same default `#live-target` shell.
New integrations should prefer `LiveRefreshConfig`, `render_live_controls(...)`,
`render_live_region(...)`, and `live_refresh_attributes(...)` when they need
per-surface partial targets.

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
    "public_presence": True,
    "journal": True,
    "review": True,
    "token_health": False,
    "workers": False,
    "scheduling": False,
}
```

Feature flags should hide navigation and UI modules by default when disabled.
They should not import optional dependencies or private adapters unless the
feature is enabled and the consumer provides the integration.

Navigation items may declare a `feature` key. PersonaConsole hides feature-gated
navigation when that feature is disabled or absent. This is only a UI/module
switch; consumers must still enforce permissions in their own server routes.

## Reference Admin Parity Fixture

`examples/fixture_app.py` is the public-safe reference fixture for consumer
alignment. It shows how one `PersonaConsoleConfig` can present a fuller admin
workspace with grouped overview, conversations, operations, and system
navigation while still keeping all real routes and data consumer-owned.

Use the fixture as a configuration target when making consumer admins feel
consistent:

- Enable only the modules the runtime actually supports.
- Keep local labels, hrefs, status pills, badges, and theme tokens in the
  consumer repo.
- Feed shared render primitives with safe counts, summaries, and status data.
- Keep route auth, mutation policy, database queries, secrets, restart
  controls, and owner-private scope aliases outside PersonaConsole.

See [Reference Admin Parity Spec](REFERENCE_ADMIN_PARITY_SPEC.md) for the
shared composition contract.

## Owner-Private Visibility

Owner-private visibility is a shared, opt-in policy helper for content that only
the linked owner account should see raw. PersonaConsole provides generic policy and
rendering primitives; consuming runtimes provide their own scope names, aliases,
person mappings, database filters, and file-route checks.

```python
from personaconsole import AdminPrivacyContext, OwnerPrivateScopePolicy, render_private_text

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

Token health is a shared, opt-in feature. PersonaConsole should not read private
`.env` files or runtime databases on its own. A consuming runtime enables the
feature, names the checks it wants to expose, and passes a settings/env mapping
or lookup callable into the redacted report builder.

```python
from personaconsole import TokenHealthCheck, TokenHealthConfig, build_token_health_report

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
from personaconsole import (
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
queue, worker, and policy status. PersonaConsole renders the cards and summary
shell; consuming runtimes own the actual checks and pass only display-safe data.

```python
from personaconsole import AdapterHealthCard, AdapterHealthConfig, AdapterHealthSparkBucket

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
for consumer-owned data. PersonaConsole renders the shell, lists, transcript
bubbles, attachment chips, activity rows, media cards, badges, and empty states;
the consuming runtime still owns the queries, route authorization, file byte
serving, and mutation endpoints.

```python
from personaconsole import (
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
PersonaConsole fails closed: it renders the safe alternate when present, otherwise
a withheld placeholder, and it strips raw href/preview URLs from the shared
HTML. This is a UI safeguard, not a substitute for server enforcement. Consumer
HTML snapshots, JSON endpoints, database queries, and media/artifact byte
routes must apply the same runtime policy before returning raw owner-private
data.

## Media Library Surface

The media-library surface is a richer shared renderer for asset galleries,
received media, generated artifacts, reference anchors, and review queues. It
adds grid/list view options, preview dialogs, metadata chips, safety and
sendability flags, non-image fallback states, source labels, and action slots
for runtime-owned upload/import/regenerate controls.

```python
from personaconsole import (
    MEDIA_LIBRARY_FEATURE,
    MediaLibraryActionSlot,
    MediaLibraryItem,
    MediaLibraryMetadata,
    MediaLibrarySurfaceConfig,
    SurfaceAction,
    render_media_library_surface,
)

html = render_media_library_surface(
    MediaLibrarySurfaceConfig(
        enabled=True,
        title="Media Library",
        action_slots=[
            MediaLibraryActionSlot(
                "Import",
                actions=[SurfaceAction("Upload", "/media/upload")],
            )
        ],
        items=[
            MediaLibraryItem(
                "asset-1",
                "Reference image",
                kind="image",
                preview_src="/media/reference-1/preview",
                detail_href="/media/reference-1",
                status="review",
                safety_label="review needed",
                sendability_label="blocked",
                metadata=[MediaLibraryMetadata("Source", "operator upload")],
            )
        ],
    ),
    features={MEDIA_LIBRARY_FEATURE: True},
)
```

PersonaConsole only renders supplied, escaped metadata and safe root-relative
URLs. Consumers own storage, upload validation, byte serving, provider
generation, moderation policy, mutations, auth, and retention. Owner-private
items use the same safe-alternate behavior as the other shared surfaces and raw
preview/detail URLs are stripped unless the viewer can see the matching scope.

## Generic Admin List Surface

The admin-list surface is a shared, opt-in renderer for dense runtime tables:
filters, status tabs, metrics, sortable column links, row action slots,
pagination, and mobile cards. The consuming runtime owns queries, auth, routes,
mutations, persistence, and any private data policy.

```python
from personaconsole import (
    ADMIN_LIST_FEATURE,
    AdminListCell,
    AdminListColumn,
    AdminListFilterField,
    AdminListPagination,
    AdminListRow,
    AdminListSurfaceConfig,
    AdminPrivacyContext,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    render_admin_list_surface,
)

policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
context = AdminPrivacyContext(access_tier="operator", viewer_person_key="operator")

html = render_admin_list_surface(
    AdminListSurfaceConfig(
        enabled=True,
        title="Runtime Rows",
        columns=[
            AdminListColumn("name", "Name", href="/items?sort=name", sortable=True),
            AdminListColumn("status", "Status", align="center"),
            AdminListColumn("summary", "Summary"),
        ],
        status_tabs=[StatusTab("All", "/items", 12, active=True)],
        filter_fields=[AdminListFilterField("q", "Search", "", "search")],
        metrics=[DashboardMetric("Visible", 12, "/items", "active filter")],
        rows=[
            AdminListRow(
                "item-1",
                cells=[
                    AdminListCell("name", "Example row", href="/items/item-1"),
                    AdminListCell("status", "ready", tone="good"),
                    AdminListCell("summary", "Operator-visible summary"),
                ],
                actions=[SurfaceAction("Open", "/items/item-1")],
            )
        ],
        pagination=AdminListPagination(count=12, page=1, page_count=2),
    ),
    features={ADMIN_LIST_FEATURE: True},
    privacy_policy=policy,
    privacy_context=context,
)
```

Cells with `privacy_scope` use the same owner-private rendering contract as
messages, media, people, and system audit rows. Operators receive safe
alternates or withheld placeholders, and raw cell hrefs are stripped unless the
viewer can see the private scope.

## Detail/Dossier Surface

The detail/dossier surface is a shared, opt-in renderer for entity profile and
record detail pages. It handles the common page shape: a header, metadata
fields, metric strip, narrative sections, source tables, related links,
timeline, audit rows, and runtime-owned action slots. The consuming runtime
owns record lookup, forms, mutations, auth, route policy, and persistence.

```python
from personaconsole import (
    DETAIL_DOSSIER_FEATURE,
    AdminPrivacyContext,
    DetailDossierAuditRow,
    DetailDossierField,
    DetailDossierHeader,
    DetailDossierMetric,
    DetailDossierSection,
    DetailDossierSourceTable,
    DetailDossierSurfaceConfig,
    DetailDossierTableCell,
    DetailDossierTableColumn,
    DetailDossierTableRow,
    DetailDossierTimelineEvent,
    OwnerPrivateScopePolicy,
    SurfaceAction,
    render_detail_dossier_surface,
)

policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
context = AdminPrivacyContext(access_tier="operator", viewer_person_key="operator")

html = render_detail_dossier_surface(
    DetailDossierSurfaceConfig(
        enabled=True,
        header=DetailDossierHeader(
            title="Example Record",
            subtitle="Runtime-owned source data rendered by PersonaConsole.",
            status="ready",
            tone="good",
        ),
        fields=[
            DetailDossierField("handle", "Handle", "@example", mono=True),
            DetailDossierField(
                "private_note",
                "Private Note",
                "raw note text",
                privacy_scope="owner_private",
                safe_alternate="Owner-private note summarized for operators.",
            ),
        ],
        metrics=[DetailDossierMetric("messages", "Messages", 12, "last 7 days")],
        sections=[
            DetailDossierSection(
                "summary",
                "Summary",
                body="Operator-visible summary supplied by the runtime.",
            )
        ],
        source_tables=[
            DetailDossierSourceTable(
                "sources",
                "Source Rows",
                columns=[
                    DetailDossierTableColumn("kind", "Kind"),
                    DetailDossierTableColumn("summary", "Summary"),
                ],
                rows=[
                    DetailDossierTableRow(
                        "source-1",
                        cells=[
                            DetailDossierTableCell("kind", "message"),
                            DetailDossierTableCell("summary", "Safe source summary."),
                        ],
                        actions=[SurfaceAction("Open", "/records/source-1")],
                    )
                ],
            )
        ],
        timeline=[DetailDossierTimelineEvent("created", "Created", "09:00")],
        audit_rows=[DetailDossierAuditRow("updated", "Updated", "1m ago")],
    ),
    features={DETAIL_DOSSIER_FEATURE: True},
    privacy_policy=policy,
    privacy_context=context,
)
```

Text content is escaped by default. `body_html` fields and action-slot HTML are
trusted extension points for consumer-owned forms or controls, so runtimes
should only pass HTML they generate themselves after their own authorization
checks. Owner-private fields, sections, rows, timeline entries, and audit values
render safe alternates for non-owner contexts and suppress raw private hrefs.

## People Surface

The people surface is a shared, opt-in module for canonical person lists,
reference-style filtering, tags, relationship summaries, and notes previews.
The consuming runtime owns person lookup, auth, create/edit routes, aliases,
database schema, and any private tier mapping.

```python
from personaconsole import (
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
filters, actions, and authorization; PersonaConsole renders the scan-friendly
surface and applies safe-alternate owner-private summaries where configured.

```python
from personaconsole import (
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

## Journal Surface

The journal surface is a shared, opt-in reader for continuity pages. Consumers
own entry lookup, calendar routing, persistence, auth, and private scope
mapping. PersonaConsole renders the dense calendar rail, the default paper page,
theme options, markers, provenance details, page-turn links, and safe
owner-private fallbacks.

```python
from personaconsole import (
    JOURNAL_FEATURE,
    AdminPrivacyContext,
    JournalEntry,
    JournalSurfaceConfig,
    OwnerPrivateScopePolicy,
    build_journal_calendar,
    journal_theme_options,
    render_journal_surface,
)

policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
context = AdminPrivacyContext(access_tier="operator", viewer_person_key="operator")

entries = [
    JournalEntry(
        "entry-1",
        "2026-06-24",
        "Quiet continuity page",
        "Operator-visible journal text.",
        href="/journal?date=2026-06-24",
    )
]

html = render_journal_surface(
    JournalSurfaceConfig(
        enabled=True,
        month_label="2026-06",
        calendar=build_journal_calendar("2026-06", entries, selected_date="2026-06-24"),
        entry=entries[0],
        entries=entries,
        theme="paper",
        theme_options=journal_theme_options("paper"),
    ),
    features={JOURNAL_FEATURE: True},
    privacy_policy=policy,
    privacy_context=context,
)
```

The built-in theme keys are `paper`, `white-paper`, `typewriter`, `script`,
`sepia`, `ledger`, `night-ink`, `violet-archive`, `matrix`,
`amber-terminal`, `blueprint`, and `glass`. Use `paper` as the default journal
reader theme, then let consuming runtimes choose a character-appropriate
setting from their own console settings.

Entries and calendar days with a privacy scope strip raw hrefs for non-owner
contexts and render the safe alternate or withheld placeholder. Raw details,
source links, page-turn URLs, and actions only render when the provided privacy
policy says the viewer can see that scope.

## Public Presence Surfaces

Public presence is the shared, reusable layer for persona-facing splash,
login, chat, connector-choice, media hero, social link, legal modal, logo, and
admin settings surfaces. PersonaConsole renders generic HTML/CSS/JS from escaped
configuration; it does not own auth, cookies, OAuth callbacks, provider SDK
calls, connector secrets, chat processors, uploads, settings persistence, or
deployment wiring.

```python
from personaconsole import (
    PUBLIC_PRESENCE_FEATURE,
    BrandAssets,
    ConnectorGroup,
    ConnectorOption,
    LoginPageConfig,
    PublicMediaConfig,
    PublicMediaSource,
    PublicSplashPageConfig,
    render_login_page,
    render_public_splash_page,
)

brand = BrandAssets(
    name="Example Persona",
    small_logo_url="/static/example-small.svg",
    large_logo_url="/static/example-large.svg",
    home_url="/",
)

media = PublicMediaConfig(
    kind="video",
    sources=[PublicMediaSource("/media/hero.mp4", "video/mp4")],
    poster_url="/media/hero.jpg",
    audio_src="/media/hero-audio.mp3",
    muted=True,
)

connectors = [
    ConnectorGroup(
        "Connect",
        connectors=[
            ConnectorOption(
                "web_chat",
                "Web chat",
                href="/login/web-chat",
                status="Ready",
                tone="good",
                configured=True,
            )
        ],
    )
]

home_html = render_public_splash_page(
    PublicSplashPageConfig(
        brand=brand,
        title="Example Persona",
        description="Generic public homepage.",
        media=media,
        chat_href="/chat",
    )
)

login_html = render_login_page(
    LoginPageConfig(
        brand=brand,
        title="Sign in",
        connector_groups=connectors,
        email_action="/login/email",
    )
)
```

`PublicMediaConfig` supports images, slideshows, video sources, poster images,
optional separate audio, focus position, overlays, and muted-by-default sound
controls. `ConnectorOption` and `ConnectorGroup` are display models only:
`key`, `label`, `href`, `action`, `icon`, `status`, `tone`, `description`,
`configured`, `enabled`, and `selected`.

The admin side can render `PublicSettingsSurfaceConfig` with
`render_public_settings_surface(...)` behind `features["public_presence"]`.
Consumers should persist any changed logo, media, social-link, connector, and
theme values in their own settings store.

PersonaEngine can later provide provider-neutral connector/capability metadata
that consumers pass into PersonaConsole, but PersonaConsole should remain a renderer
and configuration model only.

## Admin Authentication Pages

Admin auth pages are reusable HTML shells for runtime operator login and forced
password-change flows. PersonaConsole renders branded forms, banners,
auth-state summaries, help/legal links, and no-JS-safe form markup. Consumers
own credential verification, session cookies, CSRF, device trust, lockouts,
audits, and persistence.

```python
from personaconsole import (
    AdminAuthSummaryItem,
    AdminLoginPageConfig,
    AdminPasswordChangePageConfig,
    BrandAssets,
    render_admin_login_page,
    render_admin_password_change_page,
)

brand = BrandAssets(name="Example Runtime", small_logo_url="/static/logo.svg")

login_html = render_admin_login_page(
    AdminLoginPageConfig(
        brand=brand,
        title="Admin Login",
        subtitle="Operator session required.",
        form_action="/login",
        next_path="/runtime",
        status_message="Use a configured operator account.",
        status_tone="info",
        summary_items=[
            AdminAuthSummaryItem("Session", "required", "info"),
        ],
    )
)

password_html = render_admin_password_change_page(
    AdminPasswordChangePageConfig(
        brand=brand,
        subject_label="Operator",
        form_action="/login/password-change",
        next_path="/runtime",
        min_length=8,
    )
)
```

For public-safety, the admin auth renderers only emit same-origin root-relative
form actions, hidden next paths, static asset paths, help/legal links, and logo
URLs. Unsafe absolute or protocol-relative values fall back to local defaults.

## Workflow Surfaces

The operations workflow layer is shared, opt-in markup for repeated runtime
admin pages: worker/task posture, safe log rows, feature/settings summaries,
persona state panels, continuity items, bridge status, and agent-session rows.
Consumers pass already-authorized display data and own all mutations, provider
calls, restarts, secret reads, and private routes.

```python
from personaconsole import (
    AGENT_OPS_FEATURE,
    OPERATIONS_FEATURE,
    PERSONA_RUNTIME_FEATURE,
    AgentOpsSurfaceConfig,
    AgentSessionRow,
    BridgeStatusCard,
    ContinuityItem,
    OperationsSurfaceConfig,
    OpsLogEvent,
    OpsSettingItem,
    OpsStatusCard,
    OpsTableRow,
    PersonaPanel,
    PersonaRuntimeSurfaceConfig,
    SurfaceAction,
    TerminalStreamConfig,
    TerminalStreamEvent,
    render_workflow_sections,
)

html = render_workflow_sections(
    operations=OperationsSurfaceConfig(
        enabled=True,
        status_cards=[OpsStatusCard("Workers", "lagging", "/workers", "Queue above target")],
        tasks=[OpsTableRow("reply-review", "Review pending replies", "waiting", "/tasks/reply-review")],
        logs=[OpsLogEvent("Privacy", "safe log summary", level="warn")],
        settings=[OpsSettingItem("Webhook secret", True, "configured", secret=True)],
    ),
    persona=PersonaRuntimeSurfaceConfig(
        enabled=True,
        panels=[PersonaPanel("Traits", 8, "/persona/traits", "Active runtime rules")],
        continuity=[ContinuityItem("Memory", "Review-safe memory", "Ready for review")],
    ),
    agent_ops=AgentOpsSurfaceConfig(
        enabled=True,
        bridges=[BridgeStatusCard("Webhook", "healthy", counts=[{"label": "0 failed", "tone": "good"}])],
        sessions=[AgentSessionRow("session", "Fixture session", "review", objective="Inspect workflow gaps")],
        terminal_stream=TerminalStreamConfig(
            enabled=True,
            title="Read-Only Terminal",
            window_label="Latest buffered events",
            history_url="/agent/sessions/session/events/history",
            stream_url="/agent/sessions/session/events/live",
            before_cursor="older-cursor",
            after_cursor="current-cursor",
            max_rendered_events=120,
            has_more_before=True,
            events=[
                TerminalStreamEvent("evt-1", "Run shared admin smoke", role="input"),
                TerminalStreamEvent("evt-2", "Fixture check completed.", role="output"),
            ],
        ),
    ),
    features={
        OPERATIONS_FEATURE: True,
        PERSONA_RUNTIME_FEATURE: True,
        AGENT_OPS_FEATURE: True,
    },
)
```

Secret settings render only configured/not-configured posture, never raw
values. Rows that declare a privacy scope use the same safe-alternate contract
as messages, people, and review rows; raw hrefs are stripped for non-owner
contexts.

Terminal streams are read-only render surfaces. PersonaConsole renders the
current bounded event window, exposes cursor/data attributes, and provides
JavaScript hooks for `history_url` and `stream_url`. Consumers own event capture,
storage, endpoint authorization, retention windows, and any real command
execution. Initial pages should pass only a bounded recent slice; older history
should be returned in chunks by the consumer endpoint so long terminal histories
do not lock the server or browser.

## Shared Persona Editor

`render_persona_editor(...)` renders profile, trait, rule, mutable-state,
proposal, and history sections for persona admin pages. PersonaConsole does not
validate traits, assemble prompts, save state, approve proposals, or decide
review policy.

```python
from personaconsole import (
    PersonaChangeRow,
    PersonaEditorConfig,
    PersonaProfileField,
    PersonaProfileSection,
    PersonaProposalCard,
    PersonaRuleRow,
    PersonaStateField,
    PersonaTraitRow,
    SurfaceAction,
    render_persona_editor,
)

html = render_persona_editor(
    PersonaEditorConfig(
        enabled=True,
        profile_sections=[
            PersonaProfileSection(
                "identity",
                "Profile",
                fields=[PersonaProfileField("display", "Display", "Example Persona")],
            )
        ],
        traits=[PersonaTraitRow("warmth", "Warmth", "+4", "high", "approved", "good")],
        rules=[PersonaRuleRow("reply-length", "Reply Length", "Prefer short replies.", "voice")],
        state_fields=[
            PersonaStateField("mode", "Runtime mode", "review", pending_value="active", changed=True)
        ],
        proposals=[
            PersonaProposalCard(
                "proposal-one",
                "Trait proposal",
                changes=[
                    PersonaChangeRow(
                        "private-change",
                        "Owner-private change",
                        "raw private before",
                        "raw private after",
                        privacy_scope="owner_private",
                        safe_alternate="safe change summary",
                    )
                ],
                actions=[SurfaceAction("Approve", "/persona/proposals/one/approve", "good", method="post")],
            )
        ],
    ),
    privacy_policy=owner_private_policy,
    privacy_context=current_admin_context,
)
```

Consumers own source-of-truth storage, validation, proposal state machines,
prompt assembly, approval policy, persistence, audit logging, and authorization.
Use `privacy_scope` plus `safe_alternate` for private trait/rule/proposal text
that should render safely for non-owner operators.

## Shared Bridge Operations

`render_bridge_ops_surface(...)` renders provider-neutral bridge and webhook
posture. PersonaConsole does not verify webhooks, send messages, claim queue
work, call provider APIs, manage browser/container state, or perform OAuth.

```python
from personaconsole import (
    BridgeDeliveryRow,
    BridgeHeartbeatRow,
    BridgeOpsSurfaceConfig,
    BridgeProviderCapabilityRow,
    BridgeQueueRow,
    BridgeStatusCard,
    BridgeWebhookRow,
    DashboardMetric,
    render_bridge_ops_surface,
)

html = render_bridge_ops_surface(
    BridgeOpsSurfaceConfig(
        enabled=True,
        metrics=[DashboardMetric("Failed", 1, "/bridge/failed", tone="bad")],
        bridges=[BridgeStatusCard("Webhook", "healthy", route="verify/reply")],
        webhooks=[BridgeWebhookRow("verify", "Verify endpoint", "healthy", method="POST")],
        queues=[BridgeQueueRow("inbound", "Inbound queue", "degraded", queued=4, failed=1)],
        heartbeats=[BridgeHeartbeatRow("worker", "Worker heartbeat", "stale", checkpoint="worker-loop")],
        providers=[
            BridgeProviderCapabilityRow(
                "chat",
                "Chat provider",
                provider="example-chat",
                capability="messages",
                configured=True,
                enabled=True,
                docs_href="/docs/providers/chat",
            )
        ],
        deliveries=[
            BridgeDeliveryRow(
                "private-failure",
                "Private delivery",
                "failed",
                detail="raw private failure",
                privacy_scope="owner_private",
                safe_alternate="safe delivery summary",
            )
        ],
    ),
    privacy_policy=owner_private_policy,
    privacy_context=current_admin_context,
)
```

Consumers own adapter execution, delivery queues, credentials, callback routes,
provider-specific policy, provider documentation URLs, browser/container state,
OAuth, and deployment wiring.

## Shared Command Intake

`render_command_intake_surface(...)` renders a parsed command preview with
candidate targets, risk checks, confirmation steps, queued commands, and recent
history. PersonaConsole does not parse commands, execute work, authorize
operators, persist queues, call providers, or touch local files.

```python
from personaconsole import (
    CommandCandidateRow,
    CommandConfirmationStep,
    CommandIntakeSurfaceConfig,
    CommandParsedField,
    CommandQueueRow,
    CommandRiskRow,
    SurfaceAction,
    render_command_intake_surface,
)

html = render_command_intake_surface(
    CommandIntakeSurfaceConfig(
        enabled=True,
        form_action="/commands/preview",
        input_value="Change the runtime schedule",
        parsed_fields=[CommandParsedField("intent", "Intent", "Adjust schedule")],
        candidates=[CommandCandidateRow("schedule", "Schedule rule", "setting", "0.93")],
        risks=[CommandRiskRow("side-effect", "Runtime side effect", "medium")],
        confirmations=[
            CommandConfirmationStep(
                "operator",
                "Operator confirmation",
                "pending",
                actions=[SurfaceAction("Confirm", "/commands/confirm", "good", method="post")],
            )
        ],
        queue=[CommandQueueRow("queued", "Queued command", command="Adjust schedule")],
    ),
    privacy_policy=owner_private_policy,
    privacy_context=current_admin_context,
)
```

Consumers own parsing, target lookup, policy evaluation, confirmation
semantics, queue storage, execution, audit logging, permissions, and side
effects. Use `privacy_scope` plus `safe_alternate` for private prompt text,
candidate details, queued commands, and history.

## Shared Availability Monitor

`render_availability_monitor_surface(...)` renders schedule windows, live
monitor checks, policy posture, scenario QA, and recent events. PersonaConsole
does not run schedulers, probe providers, restart workers, store events, or
decide availability policy.

```python
from personaconsole import (
    AvailabilityMonitorRow,
    AvailabilityMonitorSurfaceConfig,
    AvailabilityPolicyRow,
    AvailabilityScenarioRow,
    AvailabilityWindowRow,
    render_availability_monitor_surface,
)

html = render_availability_monitor_surface(
    AvailabilityMonitorSurfaceConfig(
        enabled=True,
        windows=[
            AvailabilityWindowRow(
                "day",
                "Daytime window",
                "open",
                starts_at="09:00",
                ends_at="17:00",
                timezone="UTC",
            )
        ],
        monitors=[AvailabilityMonitorRow("queue", "Queue latency", "healthy", value="12s", target="30s")],
        policies=[AvailabilityPolicyRow("review", "Review gate", "active", requirement="operator confirmation")],
        scenarios=[AvailabilityScenarioRow("preflight", "Reply preflight", "ready", current_step="policy check")],
    ),
    privacy_policy=owner_private_policy,
    privacy_context=current_admin_context,
)
```

Consumers own schedule evaluation, worker control, route probing, provider
calls, scenario execution, event retention, alerts, permissions, and runtime
policy. Use `privacy_scope` plus `safe_alternate` for private schedule details,
scenario notes, and monitor events.

## Shared Settings Editor

`render_settings_editor(...)` renders grouped runtime-owned settings without
moving persistence, reveal permission, validation policy, restarts, audit
logging, or secret lookup into PersonaConsole.

```python
from personaconsole import (
    SettingsEditorConfig,
    SettingsField,
    SettingsGroup,
    SettingsValidationMessage,
    SurfaceAction,
    render_settings_editor,
)

html = render_settings_editor(
    SettingsEditorConfig(
        enabled=True,
        form_action="/settings/runtime/save",
        restart_required=True,
        messages=[SettingsValidationMessage("Interval needs review.", "interval", "warn")],
        actions=[SurfaceAction("Restart runtime", "/settings/runtime/restart", "warn", method="post")],
        groups=[
            SettingsGroup(
                "runtime",
                "Runtime",
                fields=[
                    SettingsField("provider", "Provider", "provider", "select", "example", options=["example", "backup"]),
                    SettingsField("api-key", "API key", "api_key", "secret", True, display_value="configured"),
                    SettingsField("interval", "Interval", "interval", "number", 15, pending_value=30, changed=True),
                ],
            )
        ],
    )
)
```

Secret/redacted fields render posture such as `configured` and empty password
inputs by default. Raw current or pending secret values are not echoed into the
HTML. Consumers provide action hrefs for reveal, save, reset, restart, and audit
flows and enforce authorization on those routes.

## Shared System Health

`render_system_health_surface(...)` renders sanitized runtime posture without
connecting to databases, probing services, reading secrets, or deciding
remediation policy.

```python
from personaconsole import (
    DashboardMetric,
    StatusTab,
    SystemAuditFilterState,
    SystemAuditRow,
    SystemDatabaseCard,
    SystemHealthCheck,
    SystemHealthGroup,
    SystemHealthSurfaceConfig,
    SystemPaginationState,
    SystemReadinessProbe,
    SystemSecretCoverageRow,
    SystemSecretFilterState,
    SystemSecretInventoryRow,
    SystemTableSummary,
    render_system_health_surface,
)

html = render_system_health_surface(
    SystemHealthSurfaceConfig(
        enabled=True,
        tabs=[StatusTab("All", "/health", 12, active=True)],
        metrics=[DashboardMetric("Database", "degraded", "/health/database", tone="warn")],
        health_groups=[
            SystemHealthGroup(
                "runtime",
                "Runtime Checks",
                checks=[SystemHealthCheck("worker", "Worker queue", "lagging", tone="warn")],
            )
        ],
        databases=[SystemDatabaseCard("runtime-db", "Runtime database", "degraded", database="runtime_db")],
        tables=[SystemTableSummary("audit_events", "stale", tone="warn", rows=41)],
        secret_coverage=[
            SystemSecretCoverageRow(
                "webhooks",
                "Webhook secrets",
                "missing",
                tone="warn",
                missing=1,
                section="webhooks",
                source="runtime",
                import_status="needs import",
                last_checked="1m ago",
            )
        ],
        secret_filters=SystemSecretFilterState(query="webhook", result_count=1, total_count=4, clear_href="/health/secrets"),
        secret_rows=[
            SystemSecretInventoryRow(
                "webhook-token",
                "Webhook token",
                section="webhooks",
                source="runtime",
                status="missing",
                tone="warn",
                value_kind="secret",
                present=False,
                active=True,
                summary="Key name and status only.",
            )
        ],
        secret_pagination=SystemPaginationState(page=1, page_count=1, total=1, limit=25),
        readiness=[SystemReadinessProbe("launch", "Launch preflight", "ready", checked_at="09:00")],
        audit_rows=[
            SystemAuditRow(
                "private-audit",
                "Owner-private audit event",
                summary="raw private audit text",
                privacy_scope="owner_private",
                safe_alternate="safe audit summary",
                entity="runtime_settings",
                source="admin_console",
            )
        ],
        audit_filters=SystemAuditFilterState(
            query="settings",
            actor="operator",
            action="update",
            entity="runtime_settings",
            source="admin_console",
            status="held",
            result_count=1,
            total_count=12,
            clear_href="/health/audit",
        ),
        audit_pagination=SystemPaginationState(page=1, page_count=2, total=12, limit=10, next_href="/health/audit?page=2"),
    ),
    privacy_policy=owner_private_policy,
    privacy_context=current_admin_context,
)
```

Consumers own the database inspection queries, migration checks, service probes,
secret inventory, audit retention, remediation actions, and authorization. Pass
only display-safe summaries unless owner-private redaction policy and safe
alternates are supplied.

Audit and secret filters are rendered as a public-safe summary of filters the
consumer already applied. PersonaConsole does not parse query strings, fetch
additional rows, read secret values, import credentials, or decide whether a
secret can be revealed. Secret rows should carry key names, coverage status,
source/import labels, and safe actions only.

## Shared Controls

Shared controls are small UI primitives that keep list and queue pages visually
consistent without moving URL construction, database filters, or authorization
into PersonaConsole.

```python
from personaconsole import StatusTab, render_status_tabs

html = render_status_tabs(
    [
        StatusTab("All", "/review", 12, active=True),
        StatusTab("Pending", "/review?status=pending", 3, tone="warn"),
        {"label": "Approved", "href": "/review?status=approved", "count": 8, "tone": "good"},
    ],
    aria_label="Review status",
)
```

`render_status_tabs(...)` emits both the generic PersonaConsole classes
(`pc-status-tabs`, `pc-status-tab`, `pc-status-tab-count`) and the legacy class
hooks (`status-tabs`, `status-tab`, `status-tab-count`) so consumers can migrate
page by page without breaking existing admin tests or styles.

Flash and action banners share the same incremental migration approach:

```python
from personaconsole import FlashBanner, flash_url, render_flash_banners

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
PYTHONPATH=/path/to/personaconsole/src python3 /path/to/personaconsole/scripts/consumer_integration_doctor.py --expected-version 1.0.33
```

The doctor verifies that `personaconsole` and its legacy compatibility shims
import, report the same version, expose adapter-health, availability-monitor,
admin-list, detail-dossier, media-library, worker-operations, token-health,
owner-private, message/activity/media/people/review/journal/operations/bridge/
terminal/persona-editor/command-intake/settings-editor/system-health helpers
plus shared controls, and can render a generic shell plus redacted feature
panels. It does not read runtime secrets, databases, private routes, or
consumer settings.
Filesystem paths are omitted from output unless `--show-paths` is explicitly
passed for local diagnostics.

## Dashboard Summary Cards

Repeated count/status cards should stay generic. Consumers own the underlying
database queries, routes, and labels, then pass a safe mapping plus display
specs into PersonaConsole:

```python
from personaconsole import DashboardMetricSpec, render_dashboard_summary_grid

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
- Keep secret-bearing and deployment-specific behavior out of PersonaConsole.
