from __future__ import annotations

import argparse
from dataclasses import replace
from html import escape
import os
from pathlib import Path

from personaconsole import (
    ACTIVITY_FEATURE,
    ADMIN_LIST_FEATURE,
    AGENT_OPS_FEATURE,
    AVAILABILITY_MONITOR_FEATURE,
    JOURNAL_FEATURE,
    MEDIA_LIBRARY_FEATURE,
    MEDIA_FEATURE,
    MESSAGES_FEATURE,
    OPERATIONS_FEATURE,
    PEOPLE_FEATURE,
    BRIDGE_OPS_FEATURE,
    COMMAND_INTAKE_FEATURE,
    PERSONA_EDITOR_FEATURE,
    PERSONA_RUNTIME_FEATURE,
    PUBLIC_PRESENCE_FEATURE,
    REVIEW_FEATURE,
    SETTINGS_EDITOR_FEATURE,
    SYSTEM_HEALTH_FEATURE,
    TERMINAL_STREAM_FEATURE,
    WORKER_OPERATIONS_FEATURE,
    ActivityEvent,
    ActivitySurfaceConfig,
    AgentOpsSurfaceConfig,
    AgentSessionRow,
    AdminAuthLink,
    AdminAuthSummaryItem,
    AdminLoginPageConfig,
    AdminListCell,
    AdminListColumn,
    AdminListFilterField,
    AdminListPagination,
    AdminListRow,
    AdminListSurfaceConfig,
    AdminPrivacyContext,
    AdminPasswordChangePageConfig,
    AvailabilityEventRow,
    AvailabilityMonitorRow,
    AvailabilityMonitorSurfaceConfig,
    AvailabilityPolicyRow,
    AvailabilityScenarioRow,
    AvailabilityWindowRow,
    BrandAssets,
    BridgeDeliveryRow,
    BridgeHeartbeatRow,
    BridgeOpsSurfaceConfig,
    BridgeProviderCapabilityRow,
    BridgeQueueRow,
    BridgeStatusCard,
    BridgeWebhookRow,
    ChatPageConfig,
    CommandCandidateRow,
    CommandConfirmationStep,
    CommandHistoryRow,
    CommandIntakeSurfaceConfig,
    CommandParsedField,
    CommandQueueRow,
    CommandRiskRow,
    ConnectorGroup,
    ConnectorOption,
    ContinuityItem,
    DashboardAction,
    DashboardActivityItem,
    DashboardAdapterCard,
    DashboardAttention,
    DashboardAttentionItem,
    DashboardData,
    DashboardFilter,
    DashboardFlow,
    DashboardFlowBucket,
    DashboardFlowSegment,
    DashboardHealthMetric,
    DashboardHealthStrip,
    DashboardMetric,
    DashboardQueueRow,
    DashboardRouteCard,
    DashboardSparkBucket,
    DetailDossierActionSlot,
    DetailDossierAuditRow,
    DetailDossierField,
    DetailDossierHeader,
    DetailDossierMetric,
    DetailDossierRelatedLink,
    DetailDossierSection,
    DetailDossierSourceTable,
    DetailDossierSurfaceConfig,
    DetailDossierTableCell,
    DetailDossierTableColumn,
    DetailDossierTableRow,
    DetailDossierTimelineEvent,
    JournalDetail,
    JournalEntry,
    JournalMarker,
    JournalSurfaceConfig,
    LegalNotice,
    LoginPageConfig,
    LiveRefreshConfig,
    MediaArtifactCard,
    MediaLibraryActionSlot,
    MediaLibraryItem,
    MediaLibraryMetadata,
    MediaLibrarySurfaceConfig,
    MediaSurfaceConfig,
    MessageAttachment,
    MessageConversation,
    MessageSurfaceConfig,
    MessageTranscriptItem,
    NavGroup,
    NavItem,
    OperationsSurfaceConfig,
    OpsLogEvent,
    OpsSettingItem,
    OpsStatusCard,
    OpsTableRow,
    OwnerPrivateScopePolicy,
    PeopleSurfaceConfig,
    PersonListRow,
    PersonRelationshipSummary,
    PersonTag,
    PersonaChangeRow,
    PersonaConsoleConfig,
    PersonaEditorConfig,
    PersonaPanel,
    PersonaProfileField,
    PersonaProfileSection,
    PersonaProposalCard,
    PersonaRuleRow,
    PersonaRuntimeSurfaceConfig,
    PersonaStateField,
    PersonaTraitRow,
    PublicLink,
    PublicMediaConfig,
    PublicMediaSource,
    PublicSettingsSurfaceConfig,
    PublicSplashPageConfig,
    ReviewAgendaItem,
    ReviewBoardRow,
    ReviewQueueCard,
    ReviewQueueSection,
    ReviewSurfaceConfig,
    SettingsEditorConfig,
    SettingsField,
    SettingsGroup,
    SettingsValidationMessage,
    StatusTab,
    StatusPill,
    SurfaceAction,
    SurfaceAdapterBinding,
    SurfaceAssetRequirement,
    SurfaceBadge,
    SurfaceRegistration,
    SurfaceRegistryConfig,
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
    TerminalStreamConfig,
    TerminalStreamEvent,
    ThemeTokens,
    TokenHealthCheck,
    TokenHealthConfig,
    UserPill,
    WorkerControlActionSlot,
    WorkerDeadLetterRow,
    WorkerDryRunCandidate,
    WorkerOperationsSurfaceConfig,
    WorkerProcessEvent,
    WorkerReadinessRow,
    WorkerRollbackCandidate,
    WorkerRunTelemetryRow,
    WorkerScheduleRow,
    build_journal_calendar,
    build_admin_brand_settings_group,
    journal_theme_options,
    public_theme_options,
    register_static_assets,
    render_bridge_ops_surface,
    render_admin_login_page,
    render_admin_password_change_page,
    render_chat_page,
    render_command_intake_surface,
    render_availability_monitor_surface,
    render_admin_list_surface,
    render_dashboard_sections,
    render_detail_dossier_surface,
    render_journal_surface,
    render_login_page,
    render_media_library_surface,
    render_people_surface,
    render_persona_editor,
    render_public_settings_surface,
    render_public_splash_page,
    render_review_surface,
    render_settings_editor,
    render_shell_html,
    render_status_tabs,
    render_surface_registry_report,
    render_surface_sections,
    render_system_health_surface,
    render_worker_operations_surface,
    render_workflow_sections,
)


_SPLASH_IMAGE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 1400 900'%3E"
    "%3Crect width='1400' height='900' fill='%2310100f'/%3E"
    "%3Cpath d='M0 620 C260 520 420 730 700 610 S1110 420 1400 520 V900 H0 Z' fill='%23ef476f' opacity='.74'/%3E"
    "%3Cpath d='M0 170 C260 80 520 250 780 150 S1170 20 1400 130 V0 H0 Z' fill='%2312b5b0' opacity='.62'/%3E"
    "%3Ccircle cx='1090' cy='330' r='190' fill='%23f7b538' opacity='.72'/%3E"
    "%3C/svg%3E"
)
_LOGIN_IMAGE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 1200'%3E"
    "%3Crect width='900' height='1200' fill='%23181714'/%3E"
    "%3Crect x='110' y='160' width='680' height='880' rx='24' fill='%23f8f4eb' opacity='.9'/%3E"
    "%3Cpath d='M180 720 H720 M220 820 H640 M260 920 H600' stroke='%2312b5b0' stroke-width='42' stroke-linecap='round'/%3E"
    "%3Ccircle cx='450' cy='440' r='150' fill='%23ef476f' opacity='.86'/%3E"
    "%3C/svg%3E"
)
_CHAT_IMAGE = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 900 1200'%3E"
    "%3Crect width='900' height='1200' fill='%23111111'/%3E"
    "%3Cpath d='M100 220 H720 Q790 220 790 290 V410 Q790 480 720 480 H330 L180 600 V480 H100 Q40 480 40 410 V290 Q40 220 100 220 Z' fill='%2312b5b0' opacity='.82'/%3E"
    "%3Cpath d='M180 660 H800 Q860 660 860 720 V850 Q860 910 800 910 H310 L160 1030 V910 H180 Q120 910 120 850 V720 Q120 660 180 660 Z' fill='%23ef476f' opacity='.82'/%3E"
    "%3Ccircle cx='690' cy='360' r='58' fill='%23f7b538'/%3E"
    "%3C/svg%3E"
)
_SMALL_LOGO = (
    "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 128 128'%3E"
    "%3Crect width='128' height='128' rx='24' fill='%2310100f'/%3E"
    "%3Cpath d='M28 90 L64 24 L100 90 Z' fill='%23ef476f'/%3E"
    "%3Ccircle cx='64' cy='76' r='14' fill='%2312b5b0'/%3E"
    "%3C/svg%3E"
)


def fixture_public_brand() -> BrandAssets:
    return BrandAssets(
        name="Example Persona",
        small_logo_url=_SMALL_LOGO,
        large_logo_url=_SMALL_LOGO,
        signature_text="shared public surface",
        home_url="/public/splash",
    )


def fixture_connector_groups() -> tuple[ConnectorGroup, ...]:
    return (
        ConnectorGroup(
            "Sign in or connect",
            key="login",
            description="Consumer runtimes provide the actual auth and provider routes.",
            connectors=(
                ConnectorOption(
                    "web_chat",
                    "Web Chat",
                    href="/public/chat",
                    icon="chat",
                    status="Ready",
                    tone="good",
                    description="Browser chat entry point.",
                    configured=True,
                    selected=True,
                ),
                ConnectorOption(
                    "email",
                    "Email",
                    href="/login/email",
                    icon="@",
                    status="Ready",
                    tone="info",
                    description="Email code login.",
                    configured=True,
                ),
                ConnectorOption(
                    "social",
                    "Social",
                    action="connect",
                    icon="share",
                    status="Needs setup",
                    tone="warn",
                    description="Provider route can be added by the runtime.",
                    configured=False,
                ),
            ),
        ),
    )


def build_public_splash_config(*, static_base_url: str = "/persona-console/static") -> PublicSplashPageConfig:
    return PublicSplashPageConfig(
        brand=fixture_public_brand(),
        title="Example Persona",
        subtitle="Public home",
        description="A reusable splash page with configurable media, chat call-to-action, social links, and legal copy.",
        media=PublicMediaConfig(
            kind="slideshow",
            sources=(
                PublicMediaSource(_SPLASH_IMAGE, "image/svg+xml", label="Abstract public hero"),
                PublicMediaSource(_LOGIN_IMAGE, "image/svg+xml", label="Paper login hero"),
                PublicMediaSource(_CHAT_IMAGE, "image/svg+xml", label="Chat hero"),
            ),
            overlay="medium",
            muted=True,
        ),
        chat_label="Chat with Example Persona",
        chat_href="/public/chat",
        social_links=(
            PublicLink("Updates", "/public/updates", icon="news", external=False),
            PublicLink("Community", "/public/community", icon="group", external=False),
        ),
        update_form_action="/public/updates",
        legal_notices=(
            LegalNotice("terms", "Terms", body="Consumer runtimes provide their own public legal copy."),
            LegalNotice("privacy", "Privacy", href="/privacy"),
        ),
        static_base_url=static_base_url,
        page_title="Example Persona Home",
        meta_description="Generic public homepage fixture for PersonaConsole.",
    )


def build_login_page_config(*, static_base_url: str = "/persona-console/static") -> LoginPageConfig:
    return LoginPageConfig(
        brand=fixture_public_brand(),
        title="Sign in to chat",
        subtitle="A media-led login surface with connector choices and muted-by-default controls.",
        media=PublicMediaConfig(kind="image", src=_LOGIN_IMAGE, alt_text="Abstract login art", overlay="soft"),
        connector_groups=fixture_connector_groups(),
        email_action="/login/email",
        phone_action="/login/phone",
        phone_enabled=True,
        next_url="/public/chat",
        status_message="Choose any configured method to continue.",
        status_tone="info",
        legal_notices=(LegalNotice("terms", "Terms", body="Example terms appear in a reusable modal."),),
        static_base_url=static_base_url,
    )


def build_admin_login_page_config(*, static_base_url: str = "/persona-console/static") -> AdminLoginPageConfig:
    return AdminLoginPageConfig(
        brand=fixture_public_brand(),
        title="Admin Login",
        subtitle="Operator session required.",
        form_action="/login",
        next_path="/runtime",
        status_message="Use a configured operator account.",
        status_tone="info",
        summary_items=(
            AdminAuthSummaryItem("Session", "required", "info", "Fixture auth shell only; consumers own verification."),
        ),
        help_links=(AdminAuthLink("Help", "/admin/help"),),
        legal_links=(AdminAuthLink("Privacy", "/privacy"),),
        static_base_url=static_base_url,
    )


def build_admin_password_change_page_config(
    *,
    static_base_url: str = "/persona-console/static",
) -> AdminPasswordChangePageConfig:
    return AdminPasswordChangePageConfig(
        brand=fixture_public_brand(),
        title="Change Admin Password",
        subtitle="Fixture Operator needs a new password.",
        subject_label="Fixture Operator",
        form_action="/login/password-change",
        next_path="/runtime",
        min_length=8,
        status_message="Password change challenge is active.",
        status_tone="info",
        summary_items=(
            AdminAuthSummaryItem("Challenge", "active", "good", "Consumer runtime owns challenge validation."),
        ),
        help_links=(AdminAuthLink("Sign in instead", "/login"),),
        static_base_url=static_base_url,
    )


def build_chat_page_config(*, static_base_url: str = "/persona-console/static") -> ChatPageConfig:
    return ChatPageConfig(
        brand=fixture_public_brand(),
        title="Chat with Example Persona",
        subtitle="A generic chat shell; the consumer runtime owns identity, history, files, and message processing.",
        media=PublicMediaConfig(kind="image", src=_CHAT_IMAGE, alt_text="Abstract chat art", overlay="strong"),
        api_me_url="/api/chat/me",
        api_history_url="/api/chat/history",
        api_message_url="/api/chat/message",
        api_upload_url="/api/chat/upload",
        api_settings_url="/api/chat/settings",
        login_href="/public/login",
        logout_href="/logout",
        composer_placeholder="Message Example Persona...",
        initial_presence_label="Fixture online",
        settings_themes=public_theme_options("studio"),
        connector_groups=fixture_connector_groups(),
        legal_notices=(LegalNotice("privacy", "Privacy", href="/privacy"),),
        static_base_url=static_base_url,
    )


def build_public_settings_surface_config() -> PublicSettingsSurfaceConfig:
    return PublicSettingsSurfaceConfig(
        enabled=True,
        brand=fixture_public_brand(),
        splash_media=PublicMediaConfig(kind="slideshow", src=_SPLASH_IMAGE, muted=True),
        login_media=PublicMediaConfig(kind="image", src=_LOGIN_IMAGE, muted=True),
        chat_media=PublicMediaConfig(kind="image", src=_CHAT_IMAGE, muted=True),
        connector_groups=fixture_connector_groups(),
        social_links=(
            PublicLink("Updates", "/public/updates", external=False),
            PublicLink("Community", "/public/community", external=False),
        ),
        theme_options=public_theme_options("studio"),
        settings_action="/settings/public-presence",
    )


def build_fixture_config(*, static_base_url: str = "/persona-console/static") -> PersonaConsoleConfig:
    return PersonaConsoleConfig(
        brand_name="Example Persona",
        page_title="Admin Overview",
        page_subtitle="Reference-style shared admin workspace",
        active="dashboard",
        features={
            MESSAGES_FEATURE: True,
            ACTIVITY_FEATURE: True,
            MEDIA_FEATURE: True,
            ADMIN_LIST_FEATURE: True,
            PEOPLE_FEATURE: True,
            REVIEW_FEATURE: True,
            JOURNAL_FEATURE: True,
            OPERATIONS_FEATURE: True,
            BRIDGE_OPS_FEATURE: True,
            COMMAND_INTAKE_FEATURE: True,
            PERSONA_EDITOR_FEATURE: True,
            PERSONA_RUNTIME_FEATURE: True,
            AGENT_OPS_FEATURE: True,
            AVAILABILITY_MONITOR_FEATURE: True,
            TERMINAL_STREAM_FEATURE: True,
            SETTINGS_EDITOR_FEATURE: True,
            SYSTEM_HEALTH_FEATURE: True,
            PUBLIC_PRESENCE_FEATURE: True,
            WORKER_OPERATIONS_FEATURE: True,
        },
        nav_groups=[
            NavGroup(
                "Overview",
                [
                    NavItem("Overview", "/", active="dashboard"),
                    NavItem("Activity", "/activity", active="activity", feature=ACTIVITY_FEATURE),
                ],
                key="overview",
            ),
            NavGroup(
                "Conversations",
                [
                    NavItem("Messages", "/messages", active="messages", badge="messages", feature=MESSAGES_FEATURE),
                    NavItem("Generic List", "/lists", active="lists", badge="lists", feature=ADMIN_LIST_FEATURE),
                    NavItem("People", "/people", active="people", badge="people", feature=PEOPLE_FEATURE),
                    NavItem("Media", "/media", active="media", badge="media", feature=MEDIA_FEATURE),
                ],
                key="conversations",
            ),
            NavGroup(
                "Operations",
                [
                    NavItem("Review Queue", "/review", active="review", badge="review"),
                    NavItem("Journal", "/journal", active="journal", badge="journal", feature=JOURNAL_FEATURE),
                    NavItem("Availability", "/availability", active="availability", badge="availability", feature=AVAILABILITY_MONITOR_FEATURE),
                    NavItem("Operations", "/operations", active="operations", badge="tasks", feature=OPERATIONS_FEATURE),
                    NavItem("Workers", "/workers", active="workers", badge="workers", feature=WORKER_OPERATIONS_FEATURE),
                    NavItem("Commands", "/commands", active="commands", badge="commands", feature=COMMAND_INTAKE_FEATURE),
                    NavItem("Persona", "/persona", active="persona", badge="persona", feature=PERSONA_RUNTIME_FEATURE),
                    NavItem("Persona Editor", "/persona/editor", active="persona-editor", feature=PERSONA_EDITOR_FEATURE),
                ],
                key="operations",
            ),
            NavGroup(
                "System",
                [
                    NavItem("Agent Ops", "/agent-ops", active="agent-ops", badge="agent_ops", feature=AGENT_OPS_FEATURE),
                    NavItem("Bridge Ops", "/bridge-ops", active="bridge-ops", feature=BRIDGE_OPS_FEATURE),
                    NavItem("Public Pages", "/settings/public-presence", active="public-presence", feature=PUBLIC_PRESENCE_FEATURE),
                    NavItem("Settings", "/settings", active="settings", feature=OPERATIONS_FEATURE),
                    NavItem("Health", "/health", active="health", feature=SYSTEM_HEALTH_FEATURE),
                ],
                key="system",
            ),
        ],
        nav_badges={
            "messages": 12,
            "lists": 2,
            "people": 3,
            "media": 9,
            "review": 4,
            "journal": 5,
            "availability": 2,
            "tasks": 6,
            "workers": 2,
            "commands": 3,
            "persona": 2,
            "agent_ops": 3,
            "health": 2,
        },
        status_pills=[
            StatusPill("Runtime active", "good"),
            StatusPill("Admin active", "good"),
            StatusPill("Review 4", "info"),
            StatusPill("Worker lag", "warn"),
        ],
        user=UserPill(
            display_name="Operator",
            username="operator",
            tier="admin",
            source="fixture",
        ),
        app_version="v1.0.33-fixture",
        brand_assets=fixture_public_brand(),
        static_base_url=static_base_url,
        theme=ThemeTokens(
            accent="rgb(239 71 111)",
            accent_soft="rgb(251 113 133)",
            accent_surface="rgb(80 25 40 / 0.38)",
            background="rgb(8 9 11)",
            surface="rgb(18 20 22)",
            surface_raised="rgb(24 26 28 / 0.98)",
            surface_muted="rgb(31 36 39 / 0.74)",
            border="rgb(64 70 74)",
            muted="rgb(156 163 175)",
            info="rgb(45 212 191)",
        ),
        live_refresh=LiveRefreshConfig(
            enabled=True,
            key="dashboard",
            url="/fragments/dashboard",
            interval_seconds=30,
            interval_options=(10, 30, 60),
            hold_selector="[data-live-hold]",
            stale_after_seconds=120,
            fallback_href="/",
        ),
    )


def render_dashboard_fragment() -> str:
    privacy_policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
    operator_context = AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )
    dashboard = DashboardData(
        attention=DashboardAttention(
            title="Operator Attention",
            subtitle="Shared first-screen rhythm for a generic persona runtime",
            label="Needs operator pass",
            tone="warn",
            count=4,
            refreshed_label="refreshed just now",
            items=[
                DashboardAttentionItem("Review", 4, "Items waiting for operator review.", "/review", tone="warn"),
                DashboardAttentionItem("Credentials", 1, "One optional webhook credential is missing.", "/health", tone="info"),
                DashboardAttentionItem("Workers", "42s", "Queue latency is above target.", "/workers", tone="bad"),
                DashboardAttentionItem("Messages", 12, "Unread conversations need triage.", "/messages", tone="warn"),
            ],
        ),
        filters=[
            DashboardFilter("All", "/", active=True, color="rgb(251 113 133)"),
            DashboardFilter("Messages", "/?surface=messages", key="messages", color="rgb(45 212 191)"),
            DashboardFilter("People", "/?surface=people", key="people", color="rgb(251 191 36)"),
            DashboardFilter("Media", "/?surface=media", key="media", color="rgb(129 140 248)"),
            DashboardFilter("Tasks", "/?surface=tasks", key="tasks", color="rgb(52 211 153)"),
            DashboardFilter("System", "/?surface=system", key="system", color="rgb(248 113 113)"),
        ],
        metrics=[
            DashboardMetric("Services", "6/6", "/health", "Admin, runtime, workers, storage", tone="good"),
            DashboardMetric("Messages", 128, "/messages", "Across active channels", tone="info"),
            DashboardMetric("People", 37, "/people", "Profiles with recent activity"),
            DashboardMetric("Open reviews", 4, "/review", "Needs operator pass", tone="warn"),
            DashboardMetric("Journal", 5, "/journal", "Continuity pages", tone="good"),
            DashboardMetric("Worker latency", "42s", "/workers", "P95 over last hour", tone="bad"),
            DashboardMetric("Artifacts", 9, "/media", "Queued or ready"),
        ],
        routes=[
            DashboardRouteCard("Messages", "/messages", "Scan conversations, summaries, and handoffs.", metric=12, tone="warn"),
            DashboardRouteCard("People", "/people", "Review profiles, notes, and visibility labels.", metric=37, tone="info"),
            DashboardRouteCard("Review Queue", "/review", "Approve, hold, or dismiss items.", metric=4, tone="warn"),
            DashboardRouteCard("Journal", "/journal", "Read continuity pages with safe provenance.", metric=5, tone="good"),
            DashboardRouteCard("Media", "/media", "Track artifacts, previews, and publishing status.", metric=9),
            DashboardRouteCard("Tasks", "/tasks", "Follow queued work and operator-owned next actions.", metric=6),
            DashboardRouteCard("Logs", "/logs", "Read sanitized runtime events and warnings.", metric=2, tone="info"),
            DashboardRouteCard("Settings", "/settings", "Adjust feature flags and integration posture.", metric="on"),
            DashboardRouteCard("Workers", "/workers", "Inspect queue health and retries.", metric="42s", tone="bad"),
        ],
        health=DashboardHealthStrip(
            "Runtime health",
            "/health",
            tone="good",
            meta="fixture runtime sampled just now",
            metrics=[
                DashboardHealthMetric("Runtime", "ok", "request path reachable", tone="good"),
                DashboardHealthMetric("Admin", "ok", "shell and assets loaded", tone="good"),
                DashboardHealthMetric("Workers", "lag", "one queue above target", tone="warn"),
                DashboardHealthMetric("Storage", "ok", "artifact index reachable", tone="good"),
            ],
        ),
        token_health=TokenHealthConfig(
            enabled=True,
            subtitle="Fixture credentials are status-only examples",
            checks=[
                TokenHealthCheck(
                    "social_provider",
                    "Social provider token",
                    "Social",
                    ["SOCIAL_PROVIDER_TOKEN"],
                    configured=True,
                ),
                TokenHealthCheck(
                    "messaging_provider",
                    "Messaging provider token",
                    "Messaging",
                    ["MESSAGING_PROVIDER_TOKEN"],
                    configured=True,
                ),
                TokenHealthCheck(
                    "webhook_verify",
                    "Webhook verify token",
                    "Webhooks",
                    ["WEBHOOK_VERIFY_TOKEN"],
                    required=False,
                    configured=False,
                ),
            ],
        ),
        adapters=[
            DashboardAdapterCard(
                "Messages",
                "healthy",
                "/messages",
                tone="good",
                route="inbound/outbound",
                policy="reply route enabled",
                last_in="2m ago",
                last_out="1m ago",
                counts=["128 in/24h", "117 out/24h"],
                sparkline=[
                    DashboardSparkBucket("oldest", 28, tone="good"),
                    DashboardSparkBucket("-6h", 42, tone="good"),
                    DashboardSparkBucket("-5h", 36, tone="good"),
                    DashboardSparkBucket("-4h", 63, tone="info"),
                    DashboardSparkBucket("-3h", 50, tone="good"),
                    DashboardSparkBucket("-2h", 74, tone="info"),
                    DashboardSparkBucket("now", 58, tone="good"),
                ],
            ),
            DashboardAdapterCard(
                "Workers",
                "lagging",
                "/workers",
                tone="warn",
                route="background queue",
                policy="retry on failure",
                last_in="4m ago",
                last_out="6m ago",
                counts=[{"label": "1 queued", "tone": "warn"}, {"label": "0 failed", "tone": "good"}],
                detail="One queue is above the expected latency target.",
            ),
            DashboardAdapterCard(
                "Social",
                "healthy",
                "/activity",
                tone="good",
                route="public engagement",
                policy="comments and likes visible by normal scope",
                last_in="5m ago",
                last_out="7m ago",
                counts=["41 events/24h", "0 failed"],
                detail="Public and group activity stays in the normal operator surface.",
            ),
        ],
        flow=DashboardFlow(
            "Conversation Flow",
            "Last 12 hours",
            inbound_total=128,
            outbound_total=117,
            buckets=[
                DashboardFlowBucket("00", 20, 16, segments=[DashboardFlowSegment("messages", 80, tone="info")]),
                DashboardFlowBucket("01", 35, 28, segments=[DashboardFlowSegment("messages", 65, tone="info")]),
                DashboardFlowBucket("02", 26, 20, segments=[DashboardFlowSegment("media", 20, tone="warn")]),
                DashboardFlowBucket("03", 50, 46, segments=[DashboardFlowSegment("messages", 72, tone="info")]),
                DashboardFlowBucket("04", 44, 39),
                DashboardFlowBucket("05", 66, 61, segments=[DashboardFlowSegment("media", 30, tone="warn")]),
                DashboardFlowBucket("06", 58, 51),
                DashboardFlowBucket("07", 72, 69, segments=[DashboardFlowSegment("messages", 70, tone="info")]),
                DashboardFlowBucket("08", 65, 60),
                DashboardFlowBucket("09", 84, 76),
                DashboardFlowBucket("10", 62, 57),
                DashboardFlowBucket("11", 77, 70),
            ],
        ),
        queue=[
            DashboardQueueRow("Pending", 4, "/pending?status=pending", tone="warn"),
            DashboardQueueRow("Held", 3, "/pending?status=held", tone="info"),
            DashboardQueueRow("Applied", 22, "/pending?status=applied", tone="good"),
            DashboardQueueRow("Failed", 1, "/pending?status=failed", tone="bad"),
            DashboardQueueRow("Cancelled", 2, "/pending?status=cancelled"),
        ],
        activity=[
            DashboardActivityItem("Review", "Four items queued", "/review", "09:42", "Waiting for operator pass.", tone="warn"),
            DashboardActivityItem("Messages", "Conversation summary refreshed", "/messages", "09:38", "Active channel state updated.", tone="info"),
            DashboardActivityItem("People", "Profile snapshot refreshed", "/people", "09:34", "Recent people notes rebuilt with privacy guards.", tone="good"),
            DashboardActivityItem("Workers", "Latency warning", "/workers", "09:31", "One worker is above target.", tone="bad"),
            DashboardActivityItem("Media", "Assets ready", "/media", "09:26", "Three generated assets are ready for inspection.", tone="good"),
        ],
    )
    admin_list_surface = render_admin_list_surface(
        AdminListSurfaceConfig(
            enabled=True,
            key="generic-list",
            title="Generic List",
            subtitle="Shared list/table renderer for consumer-owned rows and actions.",
            columns=[
                AdminListColumn("name", "Name", href="/lists?sort=name", sortable=True, active=True, direction="asc"),
                AdminListColumn("status", "Status", align="center"),
                AdminListColumn("summary", "Summary"),
                AdminListColumn("updated", "Updated", align="right", hidden_mobile=True),
            ],
            status_tabs=[
                StatusTab("All", "/lists", 2, active=True),
                StatusTab("Held", "/lists?status=held", 1, tone="warn"),
            ],
            filters=[
                DashboardFilter("Ready", "/lists?status=ready", key="ready", active=True),
                DashboardFilter("Held", "/lists?status=held", key="held", color="rgb(251 191 36)"),
            ],
            filter_fields=[
                AdminListFilterField("q", "Search", "example", "search", placeholder="Find rows"),
                AdminListFilterField("status", "Status", "ready", "select", options=["ready", "held", "archived"]),
            ],
            filter_action="/lists",
            reset_href="/lists",
            metrics=[
                DashboardMetric("Visible", 2, "/lists", "active filter", tone="good"),
                DashboardMetric("Held", 1, "/lists?status=held", "safe alternate shown", tone="warn"),
            ],
            actions=[SurfaceAction("New row", "/lists/new", "good")],
            rows=[
                AdminListRow(
                    "public",
                    cells=[
                        AdminListCell("name", "Example public row", href="/lists/public"),
                        AdminListCell("status", "ready", tone="good", badges=["configured"]),
                        AdminListCell("summary", "Consumer-owned summary rendered by PersonaConsole."),
                        AdminListCell("updated", "1m ago", mono=True, nowrap=True),
                    ],
                    actions=[SurfaceAction("Open", "/lists/public")],
                ),
                AdminListRow(
                    "owner-private",
                    cells=[
                        AdminListCell("name", "Owner-private row"),
                        AdminListCell("status", "held", tone="warn"),
                        AdminListCell(
                            "summary",
                            "raw fixture private admin-list summary",
                            href="/lists/private-raw",
                            privacy_scope="owner_private",
                            safe_alternate="Owner-private list cell summarized for operators.",
                        ),
                        AdminListCell("updated", "2m ago", mono=True, nowrap=True),
                    ],
                    summary="raw fixture private admin-list card summary",
                    summary_privacy_scope="owner_private",
                    summary_safe_alternate="Owner-private list card summarized for operators.",
                ),
            ],
            pagination=AdminListPagination(count=2, page=1, page_count=1),
            mobile_card_primary_key="name",
            mobile_card_secondary_key="status",
        ),
        features={ADMIN_LIST_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    detail_dossier_surface = render_detail_dossier_surface(
        DetailDossierSurfaceConfig(
            enabled=True,
            key="generic-detail",
            header=DetailDossierHeader(
                title="Example Detail",
                subtitle="Shared dossier renderer for consumer-owned profile, record, and source detail pages.",
                entity_type="Record",
                eyebrow="Detail",
                status="ready",
                tone="good",
                href="/detail/example",
                initials="ED",
                badges=["shared", SurfaceBadge("privacy-aware", tone="info")],
                actions=[SurfaceAction("Open record", "/detail/example", "good")],
            ),
            fields=[
                DetailDossierField("handle", "Handle", "@example", href="/detail/example", mono=True),
                DetailDossierField("status", "Status", "ready", tone="good"),
                DetailDossierField("owner", "Owner", "operator", detail="runtime-owned metadata"),
                DetailDossierField(
                    "private_context",
                    "Private Context",
                    "raw fixture private detail dossier field",
                    href="/detail/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private dossier field summarized for operators.",
                    wide=True,
                ),
            ],
            metrics=[
                DetailDossierMetric("messages", "Messages", 12, "last 7 days", href="/messages?detail=example", tone="info"),
                DetailDossierMetric("risk", "Risk", "low", "current assessment", tone="good"),
                DetailDossierMetric("reviews", "Reviews", 3, "queued", tone="warn"),
            ],
            sections=[
                DetailDossierSection(
                    "summary",
                    "Summary",
                    "Operator-readable context for the selected record.",
                    body="This public-safe fixture summary is rendered by the shared dossier surface.",
                    fields=[
                        DetailDossierField("source", "Source", "runtime"),
                        DetailDossierField("updated", "Updated", "1m ago", mono=True),
                    ],
                    badges=[SurfaceBadge("generic", tone="info")],
                ),
                DetailDossierSection(
                    "private-notes",
                    "Private Notes",
                    "Safe alternate text is shown when the operator cannot view owner-private content.",
                    body="raw fixture private detail dossier section",
                    body_privacy_scope="owner_private",
                    body_safe_alternate="Owner-private context is summarized without raw prose.",
                    tone="warn",
                ),
            ],
            source_tables=[
                DetailDossierSourceTable(
                    "sources",
                    "Source Rows",
                    "Rows from a consumer-owned backing store.",
                    columns=[
                        DetailDossierTableColumn("kind", "Kind"),
                        DetailDossierTableColumn("summary", "Summary"),
                        DetailDossierTableColumn("count", "Count", align="right", hidden_mobile=True),
                    ],
                    rows=[
                        DetailDossierTableRow(
                            "public-source",
                            cells=[
                                DetailDossierTableCell("kind", "message", mono=True),
                                DetailDossierTableCell("summary", "Public-safe source summary.", href="/detail/source/public"),
                                DetailDossierTableCell("count", 3, numeric=True),
                            ],
                            actions=[SurfaceAction("Open", "/detail/source/public")],
                        ),
                        DetailDossierTableRow(
                            "private-source",
                            cells=[
                                DetailDossierTableCell("kind", "note", mono=True),
                                DetailDossierTableCell(
                                    "summary",
                                    "raw fixture private detail dossier table",
                                    href="/detail/source/raw-private",
                                    privacy_scope="owner_private",
                                    safe_alternate="Owner-private table row summarized for operators.",
                                ),
                                DetailDossierTableCell("count", 1, numeric=True),
                            ],
                            tone="warn",
                        ),
                    ],
                )
            ],
            timeline=[
                DetailDossierTimelineEvent("created", "Created", "09:00", "Record created", actor="runtime"),
                DetailDossierTimelineEvent(
                    "private-update",
                    "Private update",
                    "09:22",
                    "raw fixture private detail dossier timeline",
                    href="/detail/timeline/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private timeline event summarized for operators.",
                    tone="warn",
                ),
            ],
            related_links=[
                DetailDossierRelatedLink("messages", "Messages", "/messages?detail=example", "12 rows", tone="info"),
                DetailDossierRelatedLink("review", "Review queue", "/review?detail=example", "3 items", tone="warn"),
            ],
            audit_rows=[
                DetailDossierAuditRow("updated", "Updated", "1m ago", actor="runtime", when="09:42"),
                DetailDossierAuditRow(
                    "private-audit",
                    "Private Audit",
                    "raw fixture private detail dossier audit",
                    actor="runtime",
                    when="09:37",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private audit value summarized.",
                    tone="warn",
                ),
            ],
            action_slots=[
                DetailDossierActionSlot(
                    "actions",
                    "Runtime Actions",
                    body="Consumer runtimes own form handlers and authorization.",
                    body_html='<form action="/review/example" method="post"><button type="submit">Queue Review</button></form>',
                    actions=[SurfaceAction("Review", "/review?detail=example", "warn")],
                )
            ],
        ),
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    people_surface = render_people_surface(
        PeopleSurfaceConfig(
            enabled=True,
            title="People",
            subtitle="Canonical people records with shared privacy-aware summaries.",
            search_action="/people",
            rows=[
                PersonListRow(
                    key="example-consumer",
                    label="Example Consumer",
                    href="/people/example-consumer",
                    subtitle='id 301 - "consumer"',
                    external_id="CN0001",
                    trust_label="internal",
                    trust_tone="info",
                    linked_users=4,
                    tags=[
                        PersonTag("Supportive", tone="good"),
                        PersonTag("Warm", tone="info"),
                        PersonTag("Needs review", tone="warn"),
                    ],
                    relationship=PersonRelationshipSummary(
                        label="Persona",
                        score="+54",
                        tone="good",
                        score_percent=78,
                        lanes=[PersonTag("trusted", tone="info"), PersonTag("familiar", tone="good")],
                        labels=[PersonTag("friend", tone="info"), PersonTag("review", tone="warn")],
                    ),
                    notes="Reads as calm and cooperative; the current handoff is clear enough for operator review.",
                    updated="1h ago",
                ),
                PersonListRow(
                    key="example-owner-private",
                    label="Owner-Private Profile",
                    href="/people/example-owner-private",
                    subtitle='id 346 - "owner lane"',
                    external_id="INT-OWNER",
                    trust_label="owner-private",
                    trust_tone="warn",
                    linked_users=1,
                    tags=[
                        PersonTag("Protected", tone="warn"),
                        PersonTag("Direct", tone="info"),
                    ],
                    relationship=PersonRelationshipSummary(
                        label="Persona",
                        score="+45",
                        tone="good",
                        score_percent=72,
                        lanes=[PersonTag("trusted", tone="info")],
                        labels=[PersonTag("private", tone="warn")],
                    ),
                    notes="raw fixture private people note",
                    notes_safe_alternate="Owner-private notes are summarized for operators.",
                    notes_privacy_scope="owner_private",
                    updated="2h ago",
                ),
            ],
            new_person_html='<p class="hint">Consumer runtimes own the actual create form and authorization.</p>',
        ),
        features={PEOPLE_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    review_tabs = render_status_tabs(
        [
            StatusTab("All", "/review", 8, active=True),
            StatusTab("Pending", "/review?status=pending", 4, tone="warn"),
            StatusTab("Ready", "/review?status=ready", 3, tone="good"),
            StatusTab("Failed", "/review?status=failed", 1, tone="bad"),
        ],
        aria_label="Review status",
    )
    review_surface = review_tabs + render_review_surface(
        ReviewSurfaceConfig(
            enabled=True,
            title="Review",
            subtitle="Operator-gated decisions and publishing queues.",
            filters=[
                DashboardFilter("All", "/review", key="8", active=True),
                DashboardFilter("Media", "/review?kind=media", key="1"),
                DashboardFilter("Messages", "/review?kind=message", key="2"),
            ],
            metrics=[
                DashboardMetric("Pending", 4, "/review?status=pending", "needs operator pass", tone="warn"),
                DashboardMetric("Failed", 1, "/review?status=failed", "retry needed", tone="bad"),
                DashboardMetric("Ready", 3, "/review?status=ready", "safe to inspect", tone="good"),
            ],
            actions=[
                DashboardAction("Persona proposals", "/persona/proposals", tone="info"),
                DashboardAction("Media review", "/review/media", tone="warn"),
            ],
            rows=[
                ReviewBoardRow(
                    "proposal",
                    "pending",
                    "persona:voice",
                    "Review proposed tone adjustment before applying.",
                    "/persona/proposals/1",
                    risk="warn",
                    actor="operator",
                    age="12m",
                    badges=[SurfaceBadge("diff", "info")],
                ),
                ReviewBoardRow(
                    "message",
                    "held",
                    "messages:owner-private",
                    "raw fixture private review summary",
                    "/messages/raw-private-review",
                    risk="bad",
                    actor="runtime",
                    age="now",
                    summary_safe_alternate="Owner-private review summary withheld for operators.",
                    summary_privacy_scope="owner_private",
                ),
                ReviewBoardRow(
                    "media",
                    "draft",
                    "media:asset-1",
                    "Generated asset is ready for operator inspection.",
                    "/review/media?q=asset-1",
                    risk="warn",
                    actor="media-worker",
                    age="28m",
                ),
            ],
            agenda=[
                ReviewAgendaItem("Persona proposals", 3, "/persona/proposals", "review queue", "Inspect current/proposed values.", "warn"),
                ReviewAgendaItem("Reflection", 12, "/review/reflection", "mind output", "Classify and link reflection notes.", "good"),
                ReviewAgendaItem("Media", 1, "/review/media", "draft assets", "Review generated artifacts.", "warn"),
                ReviewAgendaItem("Voice", 2, "/creation/voice", "audio clips", "Inspect queued clips.", "info"),
            ],
            queue_sections=[
                ReviewQueueSection(
                    "Publishing Queues",
                    "safe summaries",
                    cards=[
                        ReviewQueueCard(
                            "Example social draft",
                            status="draft",
                            href="/review/social?q=post-1",
                            category="social",
                            summary="Caption is ready for operator review.",
                            meta=[("Key", "post-1"), ("Source", "operator")],
                            tone="warn",
                        ),
                        ReviewQueueCard(
                            "Owner-private queue",
                            status="pending",
                            href="/review/private",
                            category="direct",
                            summary="raw fixture private queue summary",
                            summary_safe_alternate="Owner-private queue summarized for operators.",
                            summary_privacy_scope="owner_private",
                            tone="info",
                        ),
                    ],
                )
            ],
        ),
        features={REVIEW_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    journal_entries = [
        JournalEntry(
            "2026-06-24",
            "2026-06-24",
            "A steady day in the runtime",
            (
                "The day resolved into a quieter rhythm after the morning review queue. "
                "Messages stayed readable, the worker warning remained contained, and the "
                "operator-visible continuity notes were strong enough to carry forward.\n\n"
                "The important part was not the number of events. It was that the page kept "
                "the human texture of the day while preserving clear provenance for review."
            ),
            href="/journal?date=2026-06-24",
            subtitle="runtime continuity",
            author_label="example-persona",
            privacy_label="operator-safe",
            timestamp="21:40",
            summary="Readable continuity page with safe provenance.",
            previous_href="/journal?date=2026-06-23",
            next_href="/journal?date=2026-06-25",
            details=[
                JournalDetail("Source", "continuity_worker"),
                JournalDetail("Confidence", "0.82", "good"),
                JournalDetail("Format", "authored text", "info"),
            ],
            markers=[
                JournalMarker("focused", "good"),
                JournalMarker("reviewed", "info"),
                JournalMarker("operator-safe", "warn"),
            ],
            actions=[SurfaceAction("Open source", "/journal/source/2026-06-24")],
        ),
        JournalEntry(
            "2026-06-23",
            "2026-06-23",
            "Queued memory review",
            "A candidate memory moved into review after the evening summary pass.",
            href="/journal?date=2026-06-23",
            author_label="example-persona",
            privacy_label="operator-safe",
        ),
        JournalEntry(
            "2026-06-21",
            "2026-06-21",
            "Legacy structured continuity",
            "Current posture: steady.\nPeople: example consumer.\nNext action: review pending reply.",
            href="/journal?date=2026-06-21",
            author_label="example-persona",
            privacy_label="operator-safe",
            legacy=True,
        ),
    ]
    journal_surface = render_journal_surface(
        JournalSurfaceConfig(
            enabled=True,
            title="Journal",
            subtitle="Calendar-driven continuity reader with selectable page themes.",
            month_label="2026-06",
            previous_month_href="/journal?month=2026-05",
            next_month_href="/journal?month=2026-07",
            calendar=build_journal_calendar(
                "2026-06",
                journal_entries,
                selected_date="2026-06-24",
                href_template="/journal?date={date}",
            ),
            entry=journal_entries[0],
            entries=journal_entries,
            theme="paper",
            theme_options=journal_theme_options("paper"),
        ),
        features={JOURNAL_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    workflow_surfaces = render_workflow_sections(
        operations=OperationsSurfaceConfig(
            enabled=True,
            status_cards=[
                OpsStatusCard(
                    "Workers",
                    "lagging",
                    "/workers",
                    "One queue is above target latency.",
                    "background queue",
                    tone="warn",
                    badges=[SurfaceBadge("runtime-owned", "info")],
                    actions=[SurfaceAction("Inspect", "/workers")],
                ),
                OpsStatusCard(
                    "Tasks",
                    "6 open",
                    "/tasks",
                    "Operator and runtime-owned work queues.",
                    tone="info",
                    actions=[SurfaceAction("Open queue", "/tasks")],
                ),
            ],
            tasks=[
                OpsTableRow(
                    "reply-review",
                    "Review pending replies",
                    "waiting",
                    "/tasks/reply-review",
                    "Needs an operator decision before send.",
                    owner="operator",
                    timestamp="09:45",
                    tone="warn",
                    actions=[SurfaceAction("Review", "/review?kind=messages", "warn")],
                ),
                OpsTableRow(
                    "profile-rollups",
                    "Refresh profile rollups",
                    "running",
                    "/tasks/profile-rollups",
                    "Runtime worker is rebuilding public-safe summaries.",
                    owner="worker",
                    timestamp="09:38",
                    tone="info",
                ),
            ],
            logs=[
                OpsLogEvent(
                    "Review",
                    "Operator queued a decision",
                    "09:45",
                    "review",
                    "info",
                    "/logs/review",
                    tone="info",
                ),
                OpsLogEvent(
                    "Privacy",
                    "raw fixture private log line",
                    "09:34",
                    "privacy",
                    "warn",
                    "/logs/private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private log line summarized for operators.",
                    tone="warn",
                ),
            ],
            settings=[
                OpsSettingItem("Messages enabled", True, "enabled", "/settings/messages", tone="good"),
                OpsSettingItem("Webhook secret", True, "configured", "/settings/webhook", secret=True, tone="info"),
                OpsSettingItem("Media review hold", False, "disabled", "/settings/media-review", changed=True, tone="warn"),
            ],
        ),
        persona=PersonaRuntimeSurfaceConfig(
            enabled=True,
            panels=[
                PersonaPanel(
                    "Traits",
                    8,
                    "/persona/traits",
                    "Active runtime trait rules are available for operator inspection.",
                    tone="info",
                    badges=[SurfaceBadge("rules", "info")],
                    actions=[SurfaceAction("Open", "/persona/traits")],
                ),
                PersonaPanel(
                    "Continuity",
                    12,
                    "/persona/continuity",
                    "Recent continuity records have safe summaries.",
                    tone="good",
                ),
                PersonaPanel(
                    "raw fixture private persona panel",
                    summary="raw fixture private persona summary",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private persona state summarized for operators.",
                    tone="warn",
                ),
            ],
            continuity=[
                ContinuityItem(
                    "Memory",
                    "Review-safe memory promotion",
                    "Candidate memory is ready for a normal review queue.",
                    "/persona/memory/promotion",
                    "09:25",
                    "promotion",
                    tone="warn",
                    actions=[SurfaceAction("Review", "/review?kind=memory", "warn")],
                ),
                ContinuityItem(
                    "Journal",
                    "raw fixture private continuity title",
                    "raw fixture private continuity summary",
                    "/persona/private-continuity",
                    "09:12",
                    "journal",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private continuity item summarized for operators.",
                    tone="info",
                ),
            ],
        ),
        agent_ops=AgentOpsSurfaceConfig(
            enabled=True,
            bridges=[
                BridgeStatusCard(
                    "Webhook",
                    "healthy",
                    "/agent-ops/webhook",
                    "verify/reply",
                    "Webhook bridge is reachable.",
                    "2m ago",
                    tone="good",
                    counts=[{"label": "0 failed", "tone": "good"}, {"label": "12 handled", "tone": "info"}],
                ),
                BridgeStatusCard(
                    "SMS bridge",
                    "held",
                    "/agent-ops/sms",
                    "inbound",
                    "Inbound bridge is configured but paused.",
                    "14m ago",
                    tone="warn",
                    counts=["1 held"],
                    actions=[SurfaceAction("Inspect", "/agent-ops/sms", "warn")],
                ),
            ],
            statuses=[
                OpsStatusCard("Preflight", "ready", "/agent-ops/preflight", "Local read-only checks are green.", tone="good"),
            ],
            sessions=[
                AgentSessionRow(
                    "fixture-session",
                    "Fixture agent session",
                    "review",
                    "/agent-ops/sessions/fixture",
                    "Summarize operator-visible workflow gaps.",
                    model="example-model",
                    reasoning="standard",
                    repo="example-runtime",
                    updated="09:20",
                    tone="warn",
                    actions=[SurfaceAction("Open", "/agent-ops/sessions/fixture")],
                ),
                AgentSessionRow(
                    "private-session",
                    "raw fixture private agent session",
                    "held",
                    "/agent-ops/private-session",
                    objective="raw fixture private agent objective",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private agent session summarized for operators.",
                    tone="info",
                ),
            ],
            terminal_stream=TerminalStreamConfig(
                enabled=True,
                title="Read-Only Terminal",
                subtitle="Current buffered event window with chunked history",
                status="streaming",
                status_tone="good",
                window_label="Latest sanitized events",
                before_cursor="fixture-before-0100",
                after_cursor="fixture-after-0106",
                history_url="/agent-ops/sessions/fixture/events/history",
                stream_url="/agent-ops/sessions/fixture/events/live",
                poll_interval_ms=5000,
                max_rendered_events=6,
                has_more_before=True,
                has_more_after=True,
                events=[
                    TerminalStreamEvent("evt-0101", "Run fixture workflow check", "09:21:00", "input", "input", "operator", 101),
                    TerminalStreamEvent("evt-0102", "Session accepted by runtime queue.", "09:21:01", "system", "system", "runtime", 102),
                    TerminalStreamEvent("evt-0103", "Inspecting shared surface coverage.", "09:21:04", "output", "output", "agent", 103),
                    TerminalStreamEvent(
                        "evt-0104",
                        "raw fixture private terminal event",
                        "09:21:08",
                        "tool",
                        "tool",
                        "agent",
                        104,
                        privacy_scope="owner_private",
                        safe_alternate="Owner-private terminal event summarized for operators.",
                    ),
                    TerminalStreamEvent("evt-0105", "No blocking errors reported.", "09:21:11", "output", "output", "agent", 105, tone="good"),
                    TerminalStreamEvent("evt-0106", "Waiting for the next runtime event.", "09:21:14", "system", "status", "runtime", 106),
                ],
            ),
        ),
        features={
            OPERATIONS_FEATURE: True,
            PERSONA_RUNTIME_FEATURE: True,
            AGENT_OPS_FEATURE: True,
            TERMINAL_STREAM_FEATURE: True,
            SETTINGS_EDITOR_FEATURE: True,
        },
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    worker_operations_surface = render_worker_operations_surface(
        WorkerOperationsSurfaceConfig(
            enabled=True,
            title="Worker Operations",
            subtitle="Readiness, schedules, dead letters, rollback candidates, and review-first controls.",
            status_tabs=[
                StatusTab("All", "/workers", 6, active=True),
                StatusTab("Review", "/workers?status=review", 2, tone="warn"),
            ],
            metrics=[
                DashboardMetric("Ready", 5, "/workers?status=ready", "enabled workers", tone="good"),
                DashboardMetric("Degraded", 1, "/workers?status=degraded", "needs operator review", tone="warn"),
                DashboardMetric("Dead Letters", 1, "/workers#dead-letters", "open retry item", tone="bad"),
            ],
            readiness=[
                WorkerReadinessRow(
                    "reflection",
                    "Reflection worker",
                    "ready",
                    "good",
                    control_state="resume",
                    schedule_status="due soon",
                    next_run="2m",
                    last_run="13m",
                    summary="Keeps continuity summaries fresh without direct sends.",
                    href="/workers/reflection",
                ),
                WorkerReadinessRow(
                    "media",
                    "Media worker",
                    "degraded",
                    "warn",
                    control_state="dry_run",
                    schedule_status="paused",
                    next_run="held",
                    last_run="41m",
                    failures=1,
                    pending_controls=2,
                    summary="Review-first posture is active while provider health is checked.",
                    href="/workers/media",
                    badges=[SurfaceBadge("review-first", "warn")],
                    actions=[SurfaceAction("Inspect", "/workers/media", "warn")],
                ),
            ],
            schedules=[
                WorkerScheduleRow("reflection-schedule", "reflection", "Reflection schedule", status="enabled", cadence="15m", next_run="2m", last_run="13m"),
                WorkerScheduleRow("media-schedule", "media", "Media schedule", enabled=False, status="paused", tone="warn", cadence="30m", next_run="held", last_run="41m"),
            ],
            runs=[
                WorkerRunTelemetryRow("run-1", "reflection", "succeeded", "due", "09:40", duration="320ms", attempts=1, output="2 summaries refreshed", tone="good"),
                WorkerRunTelemetryRow(
                    "run-private",
                    "media",
                    "failed",
                    "dry_run",
                    "09:31",
                    attempts=2,
                    error="raw fixture private worker failure",
                    href="/workers/raw-private-run",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private worker failure summarized for operators.",
                    tone="bad",
                ),
            ],
            dead_letters=[
                WorkerDeadLetterRow(
                    "dead-private",
                    "media",
                    "open",
                    "provider",
                    "raw fixture private worker dead letter",
                    retries=2,
                    last_retry="09:20",
                    href="/workers/raw-private-dead-letter",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private dead letter summarized for operators.",
                )
            ],
            rollback_candidates=[
                WorkerRollbackCandidate("rollback-media", "media", "dry_run", "resume", "resume", 42, "operator", "09:22", "Queue a reviewed rollback after provider recovery."),
            ],
            dry_run_candidates=[
                WorkerDryRunCandidate(
                    "dry-private",
                    "self_learn",
                    "worker_dry_run",
                    "reflection",
                    "recorded",
                    "hold",
                    "raw fixture private worker dry-run candidate",
                    "09:18",
                    "warn",
                    "/workers/raw-private-dry-run",
                    "owner_private",
                    "Owner-private dry-run candidate summarized for operators.",
                )
            ],
            process_events=[
                WorkerProcessEvent("evt-1", "reflection", "run", "succeeded", "Reflection worker completed a due tick.", "09:40", "good", "/workers/reflection/runs/1"),
                WorkerProcessEvent(
                    "evt-private",
                    "media",
                    "dead_letter",
                    "open",
                    "raw fixture private worker process event",
                    "09:31",
                    "bad",
                    "/workers/raw-private-process",
                    "owner_private",
                    "Owner-private worker process event summarized for operators.",
                ),
            ],
            action_slots=[
                WorkerControlActionSlot(
                    "control-proposal",
                    "Queue Control Proposal",
                    "Consumer runtime owns proposal persistence and review.",
                    '<form action="/workers/proposals" method="post"><button type="submit">Queue Proposal</button></form>',
                )
            ],
            actions=[SurfaceAction("Open Workers", "/workers")],
        ),
        features={WORKER_OPERATIONS_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    bridge_ops_surface = render_bridge_ops_surface(
        BridgeOpsSurfaceConfig(
            enabled=True,
            title="Bridge Operations",
            subtitle="Provider-neutral webhook, queue, heartbeat, capability, and delivery posture.",
            tabs=[
                StatusTab("All", "/bridge-ops", 10, active=True),
                StatusTab("Healthy", "/bridge-ops?status=healthy", 5, tone="good"),
                StatusTab("Degraded", "/bridge-ops?status=degraded", 3, tone="warn"),
                StatusTab("Failed", "/bridge-ops?status=failed", 2, tone="bad"),
            ],
            metrics=[
                DashboardMetric("Adapters", 5, "/bridge-ops/adapters", "provider-neutral bridges", tone="info"),
                DashboardMetric("Queued", 4, "/bridge-ops/queues", "waiting for runtime workers", tone="warn"),
                DashboardMetric("Failed", 1, "/bridge-ops/deliveries?status=failed", "needs review", tone="bad"),
                DashboardMetric("Docs", 3, "/bridge-ops/providers", "configured capability links", tone="good"),
            ],
            bridges=[
                BridgeStatusCard("Webhook", "healthy", "/bridge-ops/webhook", "verify/reply", "Webhook bridge is reachable.", "2m ago", "good", counts=[{"label": "0 failed", "tone": "good"}]),
                BridgeStatusCard("Chat bridge", "healthy", "/bridge-ops/chat", "browser chat", "Chat ingress and reply paths are enabled.", "1m ago", "good", counts=["7 inbound"]),
                BridgeStatusCard("SMS bridge", "paused", route="phone/sms", detail="Inbound path is configured but paused.", last_seen="14m ago", tone="warn", actions=[SurfaceAction("Inspect", "/bridge-ops/sms", "warn")]),
            ],
            webhooks=[
                BridgeWebhookRow("verify", "Verify endpoint", "healthy", "good", "POST", "/webhooks/example/verify", "ok", "2m ago", "Signature and challenge checks passed."),
                BridgeWebhookRow("reply", "Reply callback", "degraded", "warn", "POST", "/webhooks/example/reply", "slow", "6m ago", "Callback responds but is above target latency."),
                BridgeWebhookRow("optional", "Optional callback", "missing", "warn", "POST", "/webhooks/example/optional", "not configured", actions=[SurfaceAction("Configure", "/bridge-ops/webhooks/optional", "warn")]),
            ],
            queues=[
                BridgeQueueRow("inbound", "Inbound queue", "degraded", "warn", queued=4, failed=1, claimed=2, last_in="1m ago", last_out="5m ago", policy="retry on failure"),
                BridgeQueueRow("outbound", "Outbound queue", "healthy", "good", queued=0, failed=0, claimed=1, last_in="3m ago", last_out="2m ago", policy="operator-reviewed sends"),
                BridgeQueueRow("disabled", "Disabled provider queue", "disabled", "neutral", queued=0, failed=0, actions=[SurfaceAction("Resume", "", disabled=True)]),
            ],
            heartbeats=[
                BridgeHeartbeatRow("worker", "Worker heartbeat", "stale", "warn", "worker-loop", "420ms", "14m ago", "Heartbeat is older than the target window."),
                BridgeHeartbeatRow("browser", "Browser bridge heartbeat", "healthy", "good", "browser-session", "80ms", "1m ago", "Bridge session is reporting normally."),
            ],
            providers=[
                BridgeProviderCapabilityRow("chat", "Chat provider", "example-chat", "messages", "ready", "good", configured=True, enabled=True, docs_href="/docs/providers/chat"),
                BridgeProviderCapabilityRow("email", "Email provider", "example-email", "email", "missing", "warn", configured=False, enabled=False, docs_href="/docs/providers/email"),
                BridgeProviderCapabilityRow("internal", "Internal peer", "example-peer", "handoff", "ready", "good", configured=True, enabled=True, docs_href="/docs/providers/internal"),
            ],
            deliveries=[
                BridgeDeliveryRow("sent", "Public delivery", "sent", "good", "outbound", "example-chat", "thread-1", 1, "09:00", "Delivered successfully."),
                BridgeDeliveryRow(
                    "private-failed",
                    "Owner-private delivery",
                    "failed",
                    "bad",
                    "outbound",
                    "example-chat",
                    "private-target",
                    3,
                    "09:05",
                    "raw fixture private bridge delivery failure",
                    href="/bridge-ops/deliveries/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private delivery failure summarized for operators.",
                ),
            ],
            actions=[
                SurfaceAction("Refresh bridges", "/bridge-ops/refresh", "info", method="post"),
                SurfaceAction("Open provider docs", "/bridge-ops/providers", "good"),
            ],
        ),
        features={BRIDGE_OPS_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    command_intake_surface = render_command_intake_surface(
        CommandIntakeSurfaceConfig(
            enabled=True,
            title="Command Intake",
            subtitle="Preview parsed commands, target candidates, risk checks, confirmations, queue, and history.",
            tabs=[
                StatusTab("Preview", "/commands", 1, active=True, tone="info"),
                StatusTab("Queued", "/commands?status=queued", 2, tone="warn"),
                StatusTab("Completed", "/commands?status=completed", 8, tone="good"),
            ],
            metrics=[
                DashboardMetric("Parsed", 1, "/commands", "ready for confirmation", tone="good"),
                DashboardMetric("Candidates", 3, "/commands/candidates", "possible targets", tone="info"),
                DashboardMetric("Risks", 1, "/commands/risks", "needs review", tone="warn"),
                DashboardMetric("Queued", 2, "/commands/queue", "runtime-owned execution", tone="warn"),
            ],
            form_action="/commands/preview",
            input_value="raw fixture private command prompt",
            input_privacy_scope="owner_private",
            input_safe_alternate="Owner-private command prompt summarized for operators.",
            submit_label="Preview command",
            queue_label="Queue command",
            queue_href="/commands/queue",
            parsed_fields=[
                CommandParsedField("intent", "Intent", "Adjust runtime schedule", status="parsed", tone="good"),
                CommandParsedField("scope", "Scope", "operator-reviewed", status="safe", tone="good"),
                CommandParsedField(
                    "private-parameter",
                    "Owner-private parameter",
                    "raw fixture private command parsed parameter",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private parsed parameter summarized for operators.",
                ),
            ],
            candidates=[
                CommandCandidateRow("schedule", "Schedule rule", "runtime setting", "0.93", "matched", "good", "Adjusts an existing schedule rule."),
                CommandCandidateRow("person", "Example person", "person", "0.81", "review", "info", "Candidate supplied by consumer lookup."),
                CommandCandidateRow(
                    "private-candidate",
                    "Owner-private candidate",
                    "private record",
                    "0.74",
                    "held",
                    "warn",
                    "raw fixture private command candidate summary",
                    detail="raw fixture private command candidate detail",
                    href="/commands/candidates/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private command candidate summarized for operators.",
                ),
            ],
            risks=[
                CommandRiskRow("side-effect", "Runtime side effect", "medium", "review", "warn", "Would change runtime-owned state after confirmation."),
                CommandRiskRow(
                    "private-risk",
                    "Owner-private risk",
                    "medium",
                    "held",
                    "warn",
                    "raw fixture private command risk summary",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private command risk summarized for operators.",
                ),
            ],
            confirmations=[
                CommandConfirmationStep("operator", "Operator confirmation", "pending", "warn", "Required before queueing.", actions=[SurfaceAction("Confirm", "/commands/confirm", "good", method="post")]),
                CommandConfirmationStep("dry-run", "Dry-run complete", "completed", "good", "Consumer parser accepted the preview."),
                CommandConfirmationStep("execution", "Execution route", "missing", "warn", "Runtime has not enabled this action.", actions=[SurfaceAction("Unavailable", "", disabled=True)]),
            ],
            queue=[
                CommandQueueRow("queued", "Queued command", "queued", "info", "Adjust runtime schedule", "operator", "schedule rule", "09:10", "Waiting for runtime worker.", href="/commands/queue/queued"),
                CommandQueueRow(
                    "private-queued",
                    "Owner-private queued command",
                    "held",
                    "warn",
                    "raw fixture private command queued command",
                    "operator",
                    "private target",
                    "09:12",
                    "raw fixture private command queue detail",
                    href="/commands/queue/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private queued command summarized for operators.",
                ),
            ],
            history=[
                CommandHistoryRow("completed", "Completed command", "completed", "good", "Refresh status cards", "operator", "dashboard", "08:40", "2s", "Completed by runtime worker."),
                CommandHistoryRow(
                    "private-history",
                    "Owner-private command history",
                    "completed",
                    "good",
                    "raw fixture private command history",
                    "operator",
                    "private target",
                    "08:05",
                    "4s",
                    "raw fixture private command history detail",
                    href="/commands/history/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private command history summarized for operators.",
                ),
            ],
            actions=[
                SurfaceAction("Open command docs", "/commands/docs", "info"),
                SurfaceAction("Refresh queue", "/commands/queue/refresh", "good", method="post"),
            ],
        ),
        features={COMMAND_INTAKE_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    availability_monitor_surface = render_availability_monitor_surface(
        AvailabilityMonitorSurfaceConfig(
            enabled=True,
            title="Availability Monitor",
            subtitle="Schedule windows, live monitor checks, policy posture, scenario QA, and events.",
            tabs=[
                StatusTab("Live", "/availability", 3, active=True, tone="good"),
                StatusTab("Review", "/availability?status=review", 1, tone="warn"),
                StatusTab("Paused", "/availability?status=paused", 1, tone="neutral"),
            ],
            metrics=[
                DashboardMetric("Open windows", 1, "/availability/windows", "current schedule", tone="good"),
                DashboardMetric("Warnings", 1, "/availability/warnings", "needs review", tone="warn"),
                DashboardMetric("Scenarios", 2, "/availability/scenarios", "QA checks", tone="info"),
                DashboardMetric("Events", 5, "/availability/events", "last hour", tone="good"),
            ],
            windows=[
                AvailabilityWindowRow("day", "Daytime window", "open", "good", "09:00", "17:00", "UTC", "weekday", "chat", "General replies are available."),
                AvailabilityWindowRow("quiet", "Quiet hours", "scheduled", "info", "22:00", "07:00", "UTC", "daily", "all", "Replies are held for review."),
                AvailabilityWindowRow(
                    "private-window",
                    "Owner-private window",
                    "held",
                    "warn",
                    "19:00",
                    "21:00",
                    "UTC",
                    "manual",
                    "private",
                    "raw fixture private availability window",
                    detail="raw fixture private availability detail",
                    href="/availability/windows/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private availability window summarized for operators.",
                ),
            ],
            monitors=[
                AvailabilityMonitorRow("queue", "Queue latency", "healthy", "good", "12s", "30s", "1m ago", "2m", "Worker queue is inside target."),
                AvailabilityMonitorRow("heartbeat", "Worker heartbeat", "stale", "warn", "14m", "5m", "14m ago", "1m", "Heartbeat is older than target.", actions=[SurfaceAction("Restart", "", disabled=True)]),
            ],
            policies=[
                AvailabilityPolicyRow("review", "Review gate", "active", "good", "operator confirmation", "Risky sends require operator confirmation."),
                AvailabilityPolicyRow("quiet", "Quiet-hours hold", "active", "info", "hold outside window", "Messages outside the active window remain queued."),
            ],
            scenarios=[
                AvailabilityScenarioRow("preflight", "Reply preflight", "ready", "good", "policy check", "queue or send", "08:30", "10:00", "Dry-run scenario is green."),
                AvailabilityScenarioRow(
                    "private-scenario",
                    "Owner-private scenario",
                    "review",
                    "warn",
                    "private preflight",
                    "hold",
                    "08:35",
                    "10:05",
                    "raw fixture private availability scenario",
                    href="/availability/scenarios/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private availability scenario summarized for operators.",
                ),
            ],
            events=[
                AvailabilityEventRow("queue-ok", "Queue check passed", "ok", "good", "09:05", "monitor", "Queue latency stayed inside target."),
                AvailabilityEventRow(
                    "private-event",
                    "Owner-private availability event",
                    "held",
                    "warn",
                    "09:10",
                    "monitor",
                    "raw fixture private availability event",
                    href="/availability/events/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private availability event summarized for operators.",
                ),
            ],
            actions=[
                SurfaceAction("Refresh monitor", "/availability/refresh", "info", method="post"),
                SurfaceAction("Open schedule", "/availability/windows", "good"),
            ],
        ),
        features={AVAILABILITY_MONITOR_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    persona_editor = render_persona_editor(
        PersonaEditorConfig(
            enabled=True,
            title="Persona Editor",
            subtitle="Profile, traits, rules, mutable state, proposals, and change history.",
            tabs=[
                StatusTab("All", "/persona/editor", 9, active=True),
                StatusTab("Draft", "/persona/editor?status=draft", 2, tone="info"),
                StatusTab("Pending", "/persona/editor?status=pending-review", 3, tone="warn"),
                StatusTab("Approved", "/persona/editor?status=approved", 4, tone="good"),
            ],
            profile_sections=[
                PersonaProfileSection(
                    "identity",
                    "Profile",
                    "Public-safe profile fields supplied by the consumer runtime.",
                    status="approved",
                    tone="good",
                    fields=[
                        PersonaProfileField("display-name", "Display name", "Example Persona", status="approved", tone="good"),
                        PersonaProfileField("voice-summary", "Voice summary", "Concise, warm, and operationally clear.", status="approved", tone="good"),
                        PersonaProfileField(
                            "owner-private-profile",
                            "Owner-private profile note",
                            "raw fixture private persona editor profile",
                            href="/persona/editor/raw-private-profile",
                            status="held",
                            tone="warn",
                            privacy_scope="owner_private",
                            safe_alternate="Owner-private profile field summarized for operators.",
                        ),
                    ],
                )
            ],
            traits=[
                PersonaTraitRow("warmth", "Warmth", "+4", "high", "approved", "good", "Keeps operator-facing messages calm."),
                PersonaTraitRow("directness", "Directness", "+3", "medium", "draft", "info", "Draft adjustment is visible for review."),
                PersonaTraitRow(
                    "owner-private-trait",
                    "Owner-private trait",
                    status="pending-review",
                    tone="warn",
                    summary="raw fixture private persona editor trait",
                    href="/persona/editor/raw-private-trait",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private trait summarized for operators.",
                ),
            ],
            rules=[
                PersonaRuleRow("reply-length", "Reply Length", "Prefer short replies unless a workflow needs detail.", "voice", 2, "approved", "good"),
                PersonaRuleRow("review-hold", "Review Hold", "Hold uncertain actions for operator review.", "safety", 1, "approved", "good"),
                PersonaRuleRow(
                    "owner-private-rule",
                    "Owner-private rule",
                    "raw fixture private persona editor rule",
                    "owner",
                    1,
                    "draft",
                    "warn",
                    href="/persona/editor/raw-private-rule",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private rule summarized for operators.",
                ),
            ],
            state_fields=[
                PersonaStateField("mode", "Runtime mode", "review", pending_value="active", field_type="select", status="draft", tone="info", changed=True),
                PersonaStateField("review-threshold", "Review threshold", 0.72, pending_value=0.8, field_type="number", status="pending-review", tone="warn", changed=True),
                PersonaStateField(
                    "private-state-secret",
                    "Private state secret",
                    "raw fixture private persona editor secret",
                    pending_value="new raw fixture persona editor secret",
                    pending_display_value="new secret staged",
                    field_type="secret",
                    status="pending-review",
                    tone="warn",
                    changed=True,
                    secret=True,
                    actions=[SurfaceAction("Reveal", "/persona/editor/reveal/private-state-secret", "info")],
                ),
            ],
            proposals=[
                PersonaProposalCard(
                    "voice-proposal",
                    "Voice rule proposal",
                    "pending-review",
                    "warn",
                    "Review a proposed voice rule before it becomes active.",
                    "operator",
                    "rule:reply-length",
                    "runtime",
                    "09:16",
                    "/persona/editor/proposals/voice-proposal",
                    changes=[
                        PersonaChangeRow("reply-length", "Reply Length", "Prefer short replies.", "Prefer short replies unless a workflow needs detail.", "pending", "warn", "runtime", "09:16"),
                        PersonaChangeRow(
                            "owner-private-change",
                            "Owner-private change",
                            "raw fixture private persona editor before",
                            "raw fixture private persona editor after",
                            "held",
                            "bad",
                            "runtime",
                            "09:17",
                            privacy_scope="owner_private",
                            safe_alternate="Owner-private proposal change summarized for operators.",
                        ),
                    ],
                    badges=[SurfaceBadge("review", "warn")],
                    actions=[
                        SurfaceAction("Approve", "/persona/editor/proposals/voice-proposal/approve", "good", method="post"),
                        SurfaceAction("Reject", "/persona/editor/proposals/voice-proposal/reject", "bad", method="post"),
                        SurfaceAction("Archive", "", "neutral", disabled=True),
                    ],
                )
            ],
            history=[
                PersonaChangeRow("history-mode", "Runtime mode", "idle", "review", "applied", "good", "operator", "08:30"),
                PersonaChangeRow("history-rule", "Review Hold", "draft", "approved", "approved", "good", "operator", "08:45"),
            ],
            actions=[
                SurfaceAction("New proposal", "/persona/editor/proposals/new", "info"),
                SurfaceAction("Open audit", "/persona/editor/audit", "warn"),
            ],
        ),
        features={PERSONA_EDITOR_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    settings_editor = render_settings_editor(
        SettingsEditorConfig(
            enabled=True,
            title="Runtime Settings",
            subtitle="Grouped editor contract with redacted values and runtime-owned actions.",
            form_action="/settings/runtime/save",
            restart_required=True,
            messages=[SettingsValidationMessage("Message interval changed from the current runtime value.", "message-interval", "warn")],
            actions=[
                SurfaceAction("Restart runtime", "/settings/runtime/restart", "warn", method="post"),
                SurfaceAction("Audit trail", "/settings/runtime/audit", "info"),
            ],
            groups=[
                build_admin_brand_settings_group(fixture_public_brand()),
                SettingsGroup(
                    "connectors",
                    "Connectors",
                    "Provider posture and runtime-owned credentials.",
                    fields=[
                        SettingsField("llm-provider", "LLM provider", "llm_provider", "select", "example-provider", options=["example-provider", "backup-provider"]),
                        SettingsField(
                            "provider-secret",
                            "Provider API key",
                            "provider_secret",
                            "secret",
                            "raw fixture private settings secret",
                            display_value="configured",
                            changed=True,
                            pending_display_value="new secret staged",
                            restart_required=True,
                            help_text="Secrets are shown as posture only. Consumers own reveal and save actions.",
                            actions=[SurfaceAction("Reveal", "/settings/runtime/reveal/provider-secret", "info")],
                        ),
                    ],
                ),
                SettingsGroup(
                    "behavior",
                    "Behavior",
                    "Safe editable runtime flags.",
                    fields=[
                        SettingsField("auto-reply", "Auto reply", "auto_reply", "boolean", True, placeholder="Enabled"),
                        SettingsField("message-interval", "Message interval", "message_interval", "number", 15, pending_value=30, changed=True, min_value=1, max_value=120, step=1),
                        SettingsField("runtime-json", "Runtime JSON preview", "runtime_json", "json", {"mode": "review", "safe": True}, readonly=True),
                    ],
                ),
            ],
        ),
        features={SETTINGS_EDITOR_FEATURE: True},
    )
    system_health_surface = render_system_health_surface(
        SystemHealthSurfaceConfig(
            enabled=True,
            title="System Health",
            subtitle="Generic runtime, database, audit, secret, and readiness posture.",
            tabs=[
                StatusTab("All", "/health", 12, active=True),
                StatusTab("Healthy", "/health?status=healthy", 6, tone="good"),
                StatusTab("Needs care", "/health?status=warn", 4, tone="warn"),
                StatusTab("Blocked", "/health?status=blocked", 2, tone="bad"),
            ],
            metrics=[
                DashboardMetric("Runtime", "ok", "/health/runtime", "admin and API reachable", tone="good"),
                DashboardMetric("Database", "degraded", "/health/database", "one table stale", tone="warn"),
                DashboardMetric("Audit events", 41, "/health/audit", "last 24 hours", tone="info"),
                DashboardMetric("Secret coverage", "6/7", "/health/secrets", "one optional missing", tone="warn"),
            ],
            health_groups=[
                SystemHealthGroup(
                    "runtime",
                    "Runtime Checks",
                    "Request path, worker, storage, and bridge health.",
                    status="degraded",
                    tone="warn",
                    checks=[
                        SystemHealthCheck("admin", "Admin server", "healthy", "good", "200", "Shell and shared assets are reachable.", updated="just now", required=True),
                        SystemHealthCheck("api", "Runtime API", "healthy", "good", "42ms", "Primary API route responds inside target.", updated="1m ago", required=True),
                        SystemHealthCheck("worker", "Background worker", "lagging", "warn", "42s", "One queue is above target latency.", updated="4m ago", required=True),
                        SystemHealthCheck("storage", "Artifact storage", "unknown", "neutral", "n/a", "Consumer runtime has not reported this probe yet.", updated="not sampled"),
                    ],
                ),
                SystemHealthGroup(
                    "webhooks",
                    "Webhook And Bridge Checks",
                    "Provider-neutral bridge posture.",
                    status="blocked",
                    tone="bad",
                    checks=[
                        SystemHealthCheck("verify", "Webhook verification", "healthy", "good", "ok", "Verification endpoint responded.", required=True),
                        SystemHealthCheck("reply", "Reply route", "blocked", "bad", "held", "Manual operator pass is required before replies resume.", required=True, blocked=True),
                    ],
                ),
            ],
            databases=[
                SystemDatabaseCard(
                    "runtime-db",
                    "Runtime database",
                    "degraded",
                    "warn",
                    database="runtime_db",
                    user="runtime_user",
                    host="internal",
                    schema_version="2026.06",
                    tables=12,
                    records="4.2k",
                    latency="42ms",
                    summary="Connection works; audit table freshness needs review.",
                    badges=[SurfaceBadge("consumer-owned", "info")],
                    actions=[SurfaceAction("Open DB checks", "/health/database", "warn")],
                ),
            ],
            tables=[
                SystemTableSummary("messages", "healthy", "good", "current", 128, "runtime", "2m ago", "conversation rows are available"),
                SystemTableSummary("people", "healthy", "good", "current", 37, "runtime", "8m ago", "profile rollups are current"),
                SystemTableSummary("audit_events", "stale", "warn", "current", 41, "admin", "1h ago", "freshness threshold exceeded"),
                SystemTableSummary("runtime_settings", "blocked", "bad", "pending", 19, "operator", "manual", "migration needs operator pass"),
            ],
            secret_coverage=[
                SystemSecretCoverageRow(
                    "providers",
                    "Provider credentials",
                    "configured",
                    "good",
                    present=3,
                    missing=0,
                    required=3,
                    optional=1,
                    summary="Required provider secrets are present.",
                    section="providers",
                    source="runtime",
                    configured=3,
                    import_status="imported",
                    last_checked="just now",
                ),
                SystemSecretCoverageRow(
                    "webhooks",
                    "Webhook secrets",
                    "missing optional",
                    "warn",
                    present=2,
                    missing=1,
                    required=2,
                    optional=2,
                    summary="One optional webhook secret is not configured.",
                    section="webhooks",
                    source="private file",
                    import_status="needs import",
                    last_checked="4m ago",
                ),
            ],
            secret_filters=SystemSecretFilterState(query="provider", section="providers", source="runtime", result_count=1, total_count=2, clear_href="/health/secrets"),
            secret_rows=[
                SystemSecretInventoryRow(
                    "provider-secret",
                    "Provider credential",
                    section="providers",
                    source="runtime",
                    status="configured",
                    tone="good",
                    value_kind="secret",
                    present=True,
                    active=True,
                    import_status="imported",
                    last_checked="just now",
                    summary="Key name and status only.",
                    href="/health/secrets?scope=providers",
                ),
                SystemSecretInventoryRow(
                    "webhook-secret",
                    "Webhook signing secret",
                    section="webhooks",
                    source="private file",
                    status="missing optional",
                    tone="warn",
                    value_kind="secret",
                    present=False,
                    active=True,
                    import_status="pending",
                    last_checked="4m ago",
                    summary="Value withheld; import stays runtime-owned.",
                ),
            ],
            secret_pagination=SystemPaginationState(page=1, page_count=1, total=2, limit=25),
            readiness=[
                SystemReadinessProbe("launch", "Launch preflight", "ready", "good", "Required runtime checks passed.", checked_at="09:00", required=True),
                SystemReadinessProbe("schema", "Schema migration", "needs review", "warn", "One migration is staged for operator approval.", checked_at="09:03", required=True),
                SystemReadinessProbe("token-scan", "Token scan", "blocked", "bad", "Manual token scan is required before promotion.", checked_at="09:05", required=True),
            ],
            audit_rows=[
                SystemAuditRow(
                    "settings",
                    "Settings update",
                    "changed",
                    "operator",
                    "applied",
                    "09:10",
                    "Runtime interval changed from 15 to 30.",
                    tone="info",
                    entity="runtime_settings",
                    source="admin_console",
                ),
                SystemAuditRow(
                    "owner-private-audit",
                    "Owner-private audit event",
                    "held",
                    "runtime",
                    "private",
                    "09:12",
                    "raw fixture private system audit",
                    tone="warn",
                    href="/audit/raw-private-fixture",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private system audit summarized for operators.",
                    entity="owner-private-state",
                    source="admin_console",
                ),
            ],
            audit_filters=SystemAuditFilterState(
                query="settings",
                actor="operator",
                action="changed",
                entity="runtime_settings",
                source="admin_console",
                status="applied",
                result_count=2,
                total_count=41,
                clear_href="/health/audit",
                summary="Audit payload values are summarized before rendering.",
            ),
            audit_pagination=SystemPaginationState(page=1, page_count=3, total=41, limit=20, next_href="/health/audit?page=2"),
            actions=[
                SurfaceAction("Refresh health", "/health/refresh", "info", method="post"),
                SurfaceAction("Open audit", "/health/audit", "warn"),
            ],
        ),
        features={SYSTEM_HEALTH_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    hold_form = """
<section class="panel">
  <div class="panel-head">
    <h2>Live Controls</h2>
    <span class="hint">30s cadence</span>
  </div>
  <form>
    <label>
      Queue filter
      <select data-live-hold>
        <option>All queues</option>
        <option>Review only</option>
        <option>Worker lag</option>
      </select>
    </label>
    <label>
      Operator note
      <textarea rows="4" data-live-hold placeholder="Hold live refresh while editing"></textarea>
    </label>
    <button type="button">Apply</button>
  </form>
</section>
"""
    surfaces = render_surface_sections(
        messages=MessageSurfaceConfig(
            enabled=True,
            filters=[
                DashboardFilter("All", "/messages", key="12", active=True, color="rgb(251 113 133)"),
                DashboardFilter("Chat", "/messages?platform=chat", key="7", color="rgb(45 212 191)"),
                DashboardFilter("Direct", "/messages?platform=direct", key="5", color="rgb(251 191 36)"),
            ],
            metrics=[
                DashboardMetric("Visible threads", 2, "/messages", "current filters", tone="info"),
                DashboardMetric("Selected messages", 2, "/messages/thread-1", "thread-1"),
                DashboardMetric("Unread", 2, "/messages?unread=1", "needs pass", tone="warn"),
            ],
            actions=[
                DashboardAction("Raw rows", "/messages?view=raw"),
                DashboardAction("Review queue", "/review", tone="warn"),
            ],
            conversations=[
                MessageConversation(
                    "thread-1",
                    "Example customer thread",
                    href="/messages/thread-1",
                    provider="Chat",
                    participant="Consumer",
                    summary="Conversation needs a response handoff.",
                    timestamp="09:42",
                    unread=2,
                    tone="warn",
                    badges=[SurfaceBadge("reply", "warn")],
                ),
                MessageConversation(
                    "thread-2",
                    "Owner-private direct thread",
                    href="/messages/thread-2/raw",
                    provider="Direct",
                    participant="Owner",
                    summary="raw fixture private thread text",
                    safe_alternate="Owner-private thread has an operator-safe summary.",
                    timestamp="09:31",
                    tone="info",
                    privacy_scope="owner_private",
                ),
            ],
            selected_key="thread-1",
            conversation_title="Threads",
            transcript_title="Selected conversation",
            transcript_meta="2 visible messages",
            transcript=[
                MessageTranscriptItem(
                    "Consumer",
                    "Can you check whether this is ready?",
                    timestamp="09:41",
                    provider="Chat",
                    attachments=[
                        MessageAttachment(
                            "Example attachment",
                            href="/media/example-asset",
                            media_type="image",
                            detail="public-safe fixture asset",
                            tone="info",
                        )
                    ],
                ),
                MessageTranscriptItem(
                    "Owner",
                    "raw fixture owner private message",
                    timestamp="09:40",
                    direction="outgoing",
                    provider="Direct",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private reply summarized for operators.",
                ),
            ],
        ),
        activity=ActivitySurfaceConfig(
            enabled=True,
            events=[
                ActivityEvent("Review", "Operator queued a decision", "09:45", "Item moved into review.", "/review", tone="warn"),
                ActivityEvent("Media", "Fixture asset ready", "09:35", "Preview generated for operator inspection.", "/media", tone="good"),
            ],
        ),
        media=MediaSurfaceConfig(
            enabled=True,
            cards=[
                MediaArtifactCard(
                    "Example generated asset",
                    href="/media/example-asset",
                    media_type="image",
                    status="ready",
                    detail="Public-safe fixture media card.",
                    timestamp="09:35",
                    provider="Media",
                    tone="good",
                ),
                MediaArtifactCard(
                    "raw fixture private media title",
                    href="/media/raw-private-fixture",
                    preview_url="/media/raw-private-fixture-preview",
                    media_type="image",
                    status="private",
                    detail="raw fixture private media detail",
                    safe_alternate="Owner-private media summarized for operators.",
                    privacy_scope="owner_private",
                    tone="info",
                ),
            ],
        ),
        features={MESSAGES_FEATURE: True, ACTIVITY_FEATURE: True, MEDIA_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    media_library_surface = render_media_library_surface(
        MediaLibrarySurfaceConfig(
            enabled=True,
            title="Media Library",
            subtitle="Reusable gallery, upload/import slots, and review posture.",
            status_tabs=[
                StatusTab("All", "/media/library", 4, active=True),
                StatusTab("Review", "/media/library?status=review", 1, tone="warn"),
            ],
            filters=[
                DashboardFilter("Images", "/media/library?type=image", key="images", active=True, color="rgb(45 212 191)"),
                DashboardFilter("Jobs", "/media/library?type=jobs", key="jobs", color="rgb(251 191 36)"),
            ],
            view_options=[
                DashboardFilter("Grid", "/media/library?view=grid", key="grid", active=True),
                DashboardFilter("List", "/media/library?view=list", key="list"),
            ],
            metrics=[
                DashboardMetric("Assets", 4, "/media/library", "visible", tone="info"),
                DashboardMetric("Sendable", 2, "/media/library?sendable=1", "ready", tone="good"),
            ],
            actions=[SurfaceAction("Upload", "/media/upload", tone="good")],
            action_slots=[
                MediaLibraryActionSlot(
                    "import",
                    "Import Media",
                    "Consumer runtimes own file validation and storage.",
                    actions=[
                        SurfaceAction("Import file", "/media/import", tone="info"),
                        SurfaceAction("Regenerate", "/media/jobs/regenerate", method="post", tone="warn"),
                    ],
                )
            ],
            items=[
                MediaLibraryItem(
                    "portrait",
                    "Example portrait anchor",
                    href="/media/library/portrait",
                    preview_url="/media/library/portrait.jpg",
                    media_type="image",
                    status="approved",
                    review_status="approved",
                    safety="safe",
                    sendability="sendable",
                    heat="low",
                    shareability="ready",
                    owner="example-persona",
                    source="upload",
                    detail="Public-safe reference card.",
                    badges=[SurfaceBadge("reference", "info")],
                    metadata=[
                        MediaLibraryMetadata("ratio", "Ratio", "4:5"),
                        MediaLibraryMetadata("quality", "Quality", "curated", tone="good"),
                    ],
                    actions=[SurfaceAction("Open", "/media/library/portrait")],
                    selected=True,
                ),
                MediaLibraryItem(
                    "voice",
                    "Voice note",
                    href="/media/library/voice",
                    preview_url="/media/library/voice.mp3",
                    media_type="audio",
                    status="review",
                    review_status="review",
                    safety="review",
                    sendability="manual",
                    source="received",
                    detail="Audio preview with local runtime-owned bytes.",
                ),
                MediaLibraryItem(
                    "file",
                    "Reference document",
                    href="/media/library/reference",
                    media_type="pdf",
                    status="stored",
                    source="import",
                    detail="Non-image fallback state.",
                ),
                MediaLibraryItem(
                    "private",
                    "raw fixture private media library title",
                    href="/media/raw-private-library",
                    preview_url="/media/raw-private-library-preview",
                    media_type="image",
                    status="private",
                    detail="raw fixture private media library detail",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private library item summarized for operators.",
                    metadata=[
                        MediaLibraryMetadata(
                            "note",
                            "Note",
                            "raw fixture private media library metadata",
                            privacy_scope="owner_private",
                            safe_alternate="Safe media library metadata.",
                        )
                    ],
                    actions=[SurfaceAction("Unsafe callback", "/oauth/callback")],
                ),
            ],
        ),
        features={MEDIA_LIBRARY_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    public_settings_surface = render_public_settings_surface(
        build_public_settings_surface_config(),
        features={PUBLIC_PRESENCE_FEATURE: True},
    )
    surface_registry = render_surface_registry_report(
        SurfaceRegistryConfig(
            enabled=True,
            features={
                "messages": True,
                "review": True,
                "system_health": True,
                "media_library": True,
                "public_presence": True,
            },
            nav_groups=[NavGroup("Core", (), key="core"), NavGroup("System", (), key="system")],
            surfaces=[
                SurfaceRegistration(
                    "messages",
                    "Messages",
                    feature="messages",
                    renderer="render_message_surface",
                    route_key="messages",
                    href="/messages",
                    nav_group="core",
                    active="messages",
                    required_assets=[SurfaceAssetRequirement("css", "Shared CSS", "/persona-console/static/persona-console.css")],
                    adapters=[SurfaceAdapterBinding("message_rows", "Message rows", "fixture adapter")],
                    summary="Consumer supplies transcript rows and route auth.",
                ),
                SurfaceRegistration(
                    "system-health",
                    "System Health",
                    feature="system_health",
                    renderer="render_system_health_surface",
                    route_key="system-health",
                    href="/health",
                    nav_group="system",
                    active="health",
                    adapters=[SurfaceAdapterBinding("runtime_probe_rows", "Runtime probes", "fixture adapter")],
                    summary="Consumer owns probes, database checks, and remediation.",
                ),
                SurfaceRegistration(
                    "media-library",
                    "Media Library",
                    feature="media_library",
                    renderer="render_media_library_surface",
                    route_key="media-library",
                    href="/media/library",
                    nav_group="core",
                    active="media-library",
                    required_assets=[SurfaceAssetRequirement("media-css", "Media CSS", "/persona-console/static/persona-console.css")],
                    adapters=[SurfaceAdapterBinding("media_rows", "Media rows", "fixture adapter")],
                    summary="Consumer owns file storage and upload validation.",
                ),
            ],
        ),
        available_renderers={
            "render_message_surface": True,
            "render_system_health_surface": True,
            "render_media_library_surface": True,
        },
        available_assets={"css": True, "media-css": True},
    )
    return (
        render_dashboard_sections(dashboard)
        + admin_list_surface
        + detail_dossier_surface
        + people_surface
        + review_surface
        + journal_surface
        + workflow_surfaces
        + worker_operations_surface
        + bridge_ops_surface
        + command_intake_surface
        + availability_monitor_surface
        + persona_editor
        + settings_editor
        + system_health_surface
        + surface_registry
        + public_settings_surface
        + media_library_surface
        + surfaces
        + hold_form
    )


def render_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    base = static_base_url.rstrip("/")
    return render_shell_html(
        build_fixture_config(static_base_url=static_base_url),
        render_dashboard_fragment(),
        current_path="/",
        extra_head=f'<link rel="stylesheet" href="{escape(base)}/persona-public.css">',
        extra_body_end=f'<script src="{escape(base)}/persona-public.js"></script>',
    )


def render_public_splash_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    return render_public_splash_page(build_public_splash_config(static_base_url=static_base_url))


def render_login_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    return render_login_page(build_login_page_config(static_base_url=static_base_url))


def render_admin_login_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    return render_admin_login_page(build_admin_login_page_config(static_base_url=static_base_url))


def render_admin_password_change_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    return render_admin_password_change_page(build_admin_password_change_page_config(static_base_url=static_base_url))


def render_chat_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    return render_chat_page(build_chat_page_config(static_base_url=static_base_url))


def render_public_settings_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    base = static_base_url.rstrip("/")
    config = replace(
        build_fixture_config(static_base_url=static_base_url),
        active="public-presence",
        page_title="Public Presence",
        page_subtitle="Reusable splash, login, chat, media, and connector settings.",
        live_refresh=None,
        live_url="",
        live_interval=None,
    )
    return render_shell_html(
        config,
        render_public_settings_surface(
            build_public_settings_surface_config(),
            features={PUBLIC_PRESENCE_FEATURE: True},
        ),
        current_path="/settings/public-presence",
        extra_head=f'<link rel="stylesheet" href="{escape(base)}/persona-public.css">',
        extra_body_end=f'<script src="{escape(base)}/persona-public.js"></script>',
    )


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
    except ImportError as exc:  # pragma: no cover - only hit without FastAPI.
        raise RuntimeError("Install the PersonaConsole FastAPI example dependencies first") from exc

    app = FastAPI(title="PersonaConsole Fixture")
    register_static_assets(app)

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return render_fixture_page()

    @app.get("/public/splash", response_class=HTMLResponse)
    def public_splash() -> str:
        return render_public_splash_fixture_page()

    @app.get("/public/login", response_class=HTMLResponse)
    def login_page() -> str:
        return render_login_fixture_page()

    @app.get("/admin/login", response_class=HTMLResponse)
    def admin_login_page() -> str:
        return render_admin_login_fixture_page()

    @app.get("/admin/password-change", response_class=HTMLResponse)
    def admin_password_change_page() -> str:
        return render_admin_password_change_fixture_page()

    @app.get("/public/chat", response_class=HTMLResponse)
    def chat_page() -> str:
        return render_chat_fixture_page()

    @app.get("/settings/public-presence", response_class=HTMLResponse)
    def public_settings() -> str:
        return render_public_settings_fixture_page()

    @app.get("/fragments/dashboard", response_class=HTMLResponse)
    def dashboard_fragment() -> str:
        return render_dashboard_fragment()

    return app


def _default_static_base_for_output(output: Path) -> str:
    root = Path(__file__).resolve().parents[1]
    static_dir = Path(__file__).resolve().parents[1] / "src" / "personaconsole" / "static"
    output_parent = output.resolve().parent
    try:
        output_parent.relative_to(root)
    except ValueError:
        return "/persona-console/static"
    return os.path.relpath(static_dir, output_parent)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the public-safe PersonaConsole fixture page.")
    parser.add_argument("--output", type=Path, help="Write HTML to this file instead of stdout.")
    parser.add_argument("--static-base-url", help="Override the static asset base URL.")
    args = parser.parse_args()

    static_base_url = args.static_base_url
    if not static_base_url and args.output:
        static_base_url = _default_static_base_for_output(args.output)
    html = render_fixture_page(static_base_url=static_base_url or "/persona-console/static")

    if args.output:
        args.output.write_text(html, encoding="utf-8")
    else:
        print(html)


if __name__ == "__main__":
    main()
