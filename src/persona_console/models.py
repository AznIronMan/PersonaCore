from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


@dataclass(frozen=True)
class NavItem:
    label: str
    href: str
    active: str | None = None
    badge: int | str | None = None
    external: bool = False
    feature: str = ""


@dataclass(frozen=True)
class NavGroup:
    label: str
    items: Sequence[NavItem | Mapping[str, object]]
    key: str | None = None


@dataclass(frozen=True)
class StatusPill:
    label: str
    tone: str = "neutral"
    title: str = ""


@dataclass(frozen=True)
class UserPill:
    display_name: str
    username: str = ""
    tier: str = ""
    source: str = ""
    initials: str = ""


@dataclass(frozen=True)
class ThemeTokens:
    accent: str = "rgb(244 114 182)"
    accent_soft: str = "rgb(251 207 232)"
    accent_surface: str = "rgb(131 24 67 / 0.32)"
    background: str = "rgb(2 6 23)"
    surface: str = "rgb(15 23 42)"
    surface_raised: str = "rgb(15 23 42 / 0.98)"
    surface_muted: str = "rgb(30 41 59 / 0.72)"
    border: str = "rgb(51 65 85)"
    text: str = "rgb(248 250 252)"
    muted: str = "rgb(148 163 184)"
    success: str = "rgb(52 211 153)"
    warning: str = "rgb(251 191 36)"
    danger: str = "rgb(248 113 113)"
    info: str = "rgb(56 189 248)"
    font_stack: str = (
        'Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, '
        '"Segoe UI", sans-serif'
    )

    def css_variables(self) -> str:
        values = {
            "--pc-accent": self.accent,
            "--pc-accent-soft": self.accent_soft,
            "--pc-accent-surface": self.accent_surface,
            "--pc-bg": self.background,
            "--pc-surface": self.surface,
            "--pc-surface-raised": self.surface_raised,
            "--pc-surface-muted": self.surface_muted,
            "--pc-border": self.border,
            "--pc-text": self.text,
            "--pc-muted": self.muted,
            "--pc-success": self.success,
            "--pc-warning": self.warning,
            "--pc-danger": self.danger,
            "--pc-info": self.info,
            "--pc-font": self.font_stack,
        }
        return "\n".join(f"  {name}: {value};" for name, value in values.items())


@dataclass(frozen=True)
class PersonaConsoleConfig:
    brand_name: str
    page_title: str
    page_subtitle: str = ""
    active: str = "dashboard"
    features: Mapping[str, bool] = field(default_factory=dict)
    nav_groups: Sequence[NavGroup | Mapping[str, object]] = field(default_factory=tuple)
    nav_badges: Mapping[str, int] = field(default_factory=dict)
    status_pills: Sequence[StatusPill | Mapping[str, object] | str] = field(default_factory=tuple)
    user: UserPill | Mapping[str, object] | None = None
    app_version: str = ""
    icon_url: str = ""
    home_url: str = "/"
    static_base_url: str = "/persona-console/static"
    theme: ThemeTokens = field(default_factory=ThemeTokens)
    live_url: str = ""
    live_interval: int | None = None
    live_hold_selector: str = ""
    updated_label: str = "Updated now"
    include_refresh: bool = True
    max_width_class: str = "pc-container"
    legacy_refresh_global: str = ""


PersonaCoreConfig = PersonaConsoleConfig


@dataclass(frozen=True)
class DashboardAction:
    label: str
    href: str
    tone: str = "neutral"


@dataclass(frozen=True)
class DashboardFilter:
    label: str
    href: str
    key: str = ""
    active: bool = False
    color: str = ""


@dataclass(frozen=True)
class DashboardAttentionItem:
    label: str
    metric: str | int
    summary: str
    href: str = ""
    detail: str = ""
    tone: str = "neutral"
    actions: Sequence[DashboardAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class DashboardAttention:
    label: str = "All clear"
    tone: str = "good"
    count: int = 0
    title: str = "Dashboard"
    subtitle: str = "Live operational snapshot"
    refreshed_label: str = ""
    items: Sequence[DashboardAttentionItem | Mapping[str, object]] = field(default_factory=tuple)
    clear_title: str = "No active operator alerts"
    clear_summary: str = "Runtime signals are inside their normal bands."


@dataclass(frozen=True)
class DashboardMetric:
    label: str
    value: str | int | float
    href: str = ""
    detail: str = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class DashboardMetricSpec:
    label: str
    key: str
    href: str = ""
    detail: str = ""
    tone: str = "neutral"
    default: str | int | float = 0
    value_kind: str = "auto"
    max_length: int = 24


@dataclass(frozen=True)
class DashboardRouteCard:
    label: str
    href: str
    summary: str = ""
    detail: str = ""
    metric: str | int = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class DashboardHealthMetric:
    label: str
    value: str | int | float
    detail: str = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class DashboardHealthStrip:
    label: str
    href: str = ""
    tone: str = "good"
    meta: str = ""
    metrics: Sequence[DashboardHealthMetric | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class TokenHealthCheck:
    key: str
    label: str = ""
    group: str = "Integrations"
    secret_names: Sequence[str] = field(default_factory=tuple)
    required: bool = True
    enabled: bool = True
    configured: bool | None = None
    href: str = ""
    summary: str = ""
    detail: str = ""


@dataclass(frozen=True)
class TokenHealthConfig:
    enabled: bool = False
    feature: str = "token_health"
    title: str = "Token Health"
    subtitle: str = "Configured integration credentials"
    checks: Sequence[TokenHealthCheck | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No token checks configured."
    show_secret_names: bool = True


@dataclass(frozen=True)
class DashboardSparkBucket:
    label: str
    percent: int | float = 0
    href: str = ""
    tone: str = "neutral"
    title: str = ""


@dataclass(frozen=True)
class DashboardAdapterCard:
    label: str
    status: str
    href: str = ""
    tone: str = "neutral"
    route: str = ""
    policy: str = ""
    last_in: str = ""
    last_out: str = ""
    counts: Sequence[str | Mapping[str, Any]] = field(default_factory=tuple)
    detail: str = ""
    action_hint: str = ""
    sparkline: Sequence[DashboardSparkBucket | Mapping[str, object]] = field(default_factory=tuple)


AdapterHealthCard = DashboardAdapterCard
AdapterHealthSparkBucket = DashboardSparkBucket


@dataclass(frozen=True)
class AdapterHealthConfig:
    enabled: bool = False
    feature: str = "adapter_health"
    title: str = "Adapter health"
    subtitle: str = "Routes, queues, and recent provider activity"
    cards: Sequence[DashboardAdapterCard | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No adapter health checks configured."


@dataclass(frozen=True)
class SurfaceBadge:
    label: str
    tone: str = "neutral"


@dataclass(frozen=True)
class StatusTab:
    label: str
    href: str = ""
    count: str | int = ""
    active: bool = False
    tone: str = "neutral"
    title: str = ""


@dataclass(frozen=True)
class FlashBanner:
    message: str
    tone: str = "good"
    title: str = ""
    action_label: str = ""
    action_href: str = ""
    dismissible: bool = True
    dismiss_label: str = "Dismiss"


@dataclass(frozen=True)
class PersonTag:
    label: str
    href: str = ""
    tone: str = "neutral"
    title: str = ""


@dataclass(frozen=True)
class PersonRelationshipSummary:
    label: str = "Persona"
    score: str | int = ""
    tone: str = "neutral"
    score_percent: int | float = 0
    lanes: Sequence[PersonTag | SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    labels: Sequence[PersonTag | SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    meta: str = ""


@dataclass(frozen=True)
class PersonListRow:
    key: str
    label: str
    href: str = ""
    subtitle: str = ""
    external_id: str = ""
    trust_label: str = ""
    trust_tone: str = "neutral"
    linked_users: str | int = ""
    tags: Sequence[PersonTag | SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    relationship: PersonRelationshipSummary | Mapping[str, object] | None = None
    notes: str = ""
    notes_safe_alternate: str = ""
    notes_privacy_scope: str = ""
    updated: str = ""
    unlinked: bool = False
    badges: Sequence[PersonTag | SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class PeopleSurfaceConfig:
    enabled: bool = False
    feature: str = "people"
    title: str = "People"
    subtitle: str = "Canonical people records"
    rows: Sequence[PersonListRow | Mapping[str, object]] = field(default_factory=tuple)
    search_action: str = ""
    search_value: str = ""
    search_placeholder: str = "canonical name, external id, alias, admin address..."
    unlinked_name: str = "unlinked"
    unlinked_checked: bool = False
    sort: str = ""
    direction: str = ""
    filter_label: str = "Filter"
    reset_href: str = ""
    new_person_html: str = ""
    new_person_label: str = "+ New person - pre-seed identity before first contact"
    new_person_open: bool = False
    empty_label: str = "No people found."


@dataclass(frozen=True)
class ReviewBoardRow:
    kind: str
    status: str
    entity: str
    summary: str = ""
    href: str = ""
    risk: str = "neutral"
    actor: str = ""
    age: str = ""
    open_label: str = "Open"
    summary_safe_alternate: str = ""
    summary_privacy_scope: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReviewAgendaItem:
    label: str
    value: str | int = ""
    href: str = ""
    category: str = ""
    summary: str = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class ReviewQueueCard:
    label: str
    status: str = ""
    href: str = ""
    category: str = ""
    summary: str = ""
    tone: str = "neutral"
    meta: Sequence[tuple[str, str] | Mapping[str, object]] = field(default_factory=tuple)
    summary_safe_alternate: str = ""
    summary_privacy_scope: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class ReviewQueueSection:
    title: str
    subtitle: str = ""
    cards: Sequence[ReviewQueueCard | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No queued items."


@dataclass(frozen=True)
class ReviewSurfaceConfig:
    enabled: bool = False
    feature: str = "review"
    title: str = "Review"
    subtitle: str = "Operator-gated decisions and queues"
    filters: Sequence[DashboardFilter | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[DashboardAction | Mapping[str, object]] = field(default_factory=tuple)
    rows: Sequence[ReviewBoardRow | Mapping[str, object]] = field(default_factory=tuple)
    agenda: Sequence[ReviewAgendaItem | Mapping[str, object]] = field(default_factory=tuple)
    queue_sections: Sequence[ReviewQueueSection | Mapping[str, object]] = field(default_factory=tuple)
    board_title: str = "Decision Board"
    board_subtitle: str = "Actionable review rows"
    empty_label: str = "No decision rows found."
    agenda_title: str = "Review Agenda"
    agenda_subtitle: str = "Direct routes"


@dataclass(frozen=True)
class MessageAttachment:
    label: str
    href: str = ""
    media_type: str = ""
    status: str = ""
    detail: str = ""
    preview_url: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""


@dataclass(frozen=True)
class MessageConversation:
    key: str
    label: str
    href: str = ""
    provider: str = ""
    participant: str = ""
    summary: str = ""
    timestamp: str = ""
    unread: int = 0
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class MessageTranscriptItem:
    sender: str
    text: str
    timestamp: str = ""
    direction: str = "incoming"
    provider: str = ""
    meta: str = ""
    href: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    attachments: Sequence[MessageAttachment | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class MessageSurfaceConfig:
    enabled: bool = False
    feature: str = "messages"
    title: str = "Messages"
    subtitle: str = "Conversation review"
    filters: Sequence[DashboardFilter | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[DashboardAction | Mapping[str, object]] = field(default_factory=tuple)
    conversations: Sequence[MessageConversation | Mapping[str, object]] = field(default_factory=tuple)
    transcript: Sequence[MessageTranscriptItem | Mapping[str, object]] = field(default_factory=tuple)
    selected_key: str = ""
    conversation_title: str = "Conversations"
    transcript_title: str = "Transcript"
    transcript_meta: str = ""
    empty_label: str = "No conversations found."
    transcript_empty_label: str = "Select a conversation to inspect its messages."


@dataclass(frozen=True)
class ActivityEvent:
    label: str
    title: str
    timestamp: str = ""
    summary: str = ""
    href: str = ""
    provider: str = ""
    meta: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class ActivitySurfaceConfig:
    enabled: bool = False
    feature: str = "activity"
    title: str = "Activity"
    subtitle: str = "Recent runtime events"
    events: Sequence[ActivityEvent | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No recent activity found."


@dataclass(frozen=True)
class MediaArtifactCard:
    label: str
    href: str = ""
    preview_url: str = ""
    media_type: str = ""
    status: str = ""
    detail: str = ""
    timestamp: str = ""
    provider: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class MediaSurfaceConfig:
    enabled: bool = False
    feature: str = "media"
    title: str = "Media"
    subtitle: str = "Artifacts and shared assets"
    cards: Sequence[MediaArtifactCard | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No media artifacts found."


@dataclass(frozen=True)
class DashboardFlowSegment:
    label: str
    percent: int | float
    tone: str = "neutral"


@dataclass(frozen=True)
class DashboardFlowBucket:
    label: str
    inbound_percent: int | float = 0
    outbound_percent: int | float = 0
    href: str = ""
    title: str = ""
    segments: Sequence[DashboardFlowSegment | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class DashboardFlow:
    title: str = "Message flow"
    meta: str = ""
    inbound_total: str | int = ""
    outbound_total: str | int = ""
    buckets: Sequence[DashboardFlowBucket | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class DashboardQueueRow:
    label: str
    count: int
    href: str = ""
    tone: str = "neutral"
    total: int | None = None


@dataclass(frozen=True)
class DashboardActivityItem:
    label: str
    title: str
    href: str = ""
    timestamp: str = ""
    summary: str = ""
    meta: str = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class DashboardData:
    features: Mapping[str, bool] = field(default_factory=dict)
    attention: DashboardAttention | Mapping[str, object] | None = None
    filters: Sequence[DashboardFilter | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    routes: Sequence[DashboardRouteCard | Mapping[str, object]] = field(default_factory=tuple)
    health: DashboardHealthStrip | Mapping[str, object] | None = None
    token_health: TokenHealthConfig | Mapping[str, object] | None = None
    adapters: Sequence[DashboardAdapterCard | Mapping[str, object]] = field(default_factory=tuple)
    flow: DashboardFlow | Mapping[str, object] | None = None
    queue: Sequence[DashboardQueueRow | Mapping[str, object]] = field(default_factory=tuple)
    activity: Sequence[DashboardActivityItem | Mapping[str, object]] = field(default_factory=tuple)
