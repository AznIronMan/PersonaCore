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
