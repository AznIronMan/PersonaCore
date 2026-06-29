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
class BrandAssets:
    name: str = ""
    small_logo_url: str = ""
    large_logo_url: str = ""
    wordmark_url: str = ""
    favicon_url: str = ""
    signature_text: str = ""
    alt_text: str = ""
    home_url: str = "/"


@dataclass(frozen=True)
class PublicMediaSource:
    src: str
    mime_type: str = ""
    media: str = ""
    label: str = ""
    poster_url: str = ""


@dataclass(frozen=True)
class PublicMediaConfig:
    kind: str = "image"
    src: str = ""
    poster_url: str = ""
    alt_text: str = ""
    sources: Sequence[PublicMediaSource | Mapping[str, object]] = field(default_factory=tuple)
    audio_src: str = ""
    muted: bool = True
    autoplay: bool = True
    loop: bool = True
    controls: bool = True
    focus_x: str = "50%"
    focus_y: str = "50%"
    overlay: str = "medium"
    interval_ms: int = 7000


@dataclass(frozen=True)
class PublicLink:
    label: str
    href: str
    icon: str = ""
    title: str = ""
    external: bool = True
    rel: str = "noopener noreferrer"


@dataclass(frozen=True)
class LegalNotice:
    key: str
    label: str
    href: str = ""
    body: str = ""


@dataclass(frozen=True)
class PublicThemeOption:
    key: str
    label: str
    selected: bool = False
    description: str = ""


@dataclass(frozen=True)
class ConnectorOption:
    key: str
    label: str
    href: str = ""
    action: str = ""
    icon: str = ""
    status: str = ""
    tone: str = "neutral"
    description: str = ""
    configured: bool = False
    enabled: bool = True
    selected: bool = False


@dataclass(frozen=True)
class ConnectorGroup:
    label: str = ""
    connectors: Sequence[ConnectorOption | Mapping[str, object]] = field(default_factory=tuple)
    key: str = ""
    description: str = ""


@dataclass(frozen=True)
class PublicSplashPageConfig:
    brand: BrandAssets | Mapping[str, object] | None = None
    title: str = "Persona"
    subtitle: str = ""
    description: str = ""
    media: PublicMediaConfig | Mapping[str, object] | None = None
    chat_label: str = "Chat"
    chat_href: str = "/chat"
    social_links: Sequence[PublicLink | Mapping[str, object]] = field(default_factory=tuple)
    update_form_action: str = ""
    update_form_label: str = "Get updates"
    update_form_placeholder: str = "email@example.com"
    update_form_source: str = "public-splash"
    legal_notices: Sequence[LegalNotice | Mapping[str, object]] = field(default_factory=tuple)
    static_base_url: str = "/persona-console/static"
    theme: str = "studio"
    page_title: str = ""
    meta_description: str = ""


@dataclass(frozen=True)
class LoginPageConfig:
    brand: BrandAssets | Mapping[str, object] | None = None
    title: str = "Sign in"
    subtitle: str = ""
    media: PublicMediaConfig | Mapping[str, object] | None = None
    connector_groups: Sequence[ConnectorGroup | Mapping[str, object]] = field(default_factory=tuple)
    email_action: str = ""
    email_label: str = "Email"
    email_placeholder: str = "email@example.com"
    email_enabled: bool = True
    phone_action: str = ""
    phone_label: str = "Phone"
    phone_placeholder: str = "+1 555 0100"
    phone_enabled: bool = False
    next_url: str = ""
    status_message: str = ""
    status_tone: str = "neutral"
    legal_notices: Sequence[LegalNotice | Mapping[str, object]] = field(default_factory=tuple)
    static_base_url: str = "/persona-console/static"
    theme: str = "studio"
    page_title: str = ""


@dataclass(frozen=True)
class ChatPageConfig:
    brand: BrandAssets | Mapping[str, object] | None = None
    title: str = "Chat"
    subtitle: str = ""
    media: PublicMediaConfig | Mapping[str, object] | None = None
    api_me_url: str = "/api/chat/me"
    api_history_url: str = "/api/chat/history"
    api_message_url: str = "/api/chat/message"
    api_upload_url: str = ""
    api_settings_url: str = "/api/chat/settings"
    api_availability_url: str = ""
    login_href: str = "/login"
    logout_href: str = ""
    composer_placeholder: str = "Type a message..."
    initial_presence_label: str = "Available"
    settings_themes: Sequence[PublicThemeOption | Mapping[str, object] | str] = field(default_factory=tuple)
    connector_groups: Sequence[ConnectorGroup | Mapping[str, object]] = field(default_factory=tuple)
    legal_notices: Sequence[LegalNotice | Mapping[str, object]] = field(default_factory=tuple)
    static_base_url: str = "/persona-console/static"
    theme: str = "studio"
    page_title: str = ""


@dataclass(frozen=True)
class PublicSettingsSurfaceConfig:
    enabled: bool = False
    feature: str = "public_presence"
    title: str = "Public Presence"
    subtitle: str = "Splash, login, chat, connector, and media settings"
    brand: BrandAssets | Mapping[str, object] | None = None
    splash_media: PublicMediaConfig | Mapping[str, object] | None = None
    login_media: PublicMediaConfig | Mapping[str, object] | None = None
    chat_media: PublicMediaConfig | Mapping[str, object] | None = None
    connector_groups: Sequence[ConnectorGroup | Mapping[str, object]] = field(default_factory=tuple)
    social_links: Sequence[PublicLink | Mapping[str, object]] = field(default_factory=tuple)
    theme_options: Sequence[PublicThemeOption | Mapping[str, object] | str] = field(default_factory=tuple)
    brand_action: str = ""
    media_action: str = ""
    connector_action: str = ""
    social_action: str = ""
    settings_action: str = ""


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
    brand_assets: BrandAssets | Mapping[str, object] | None = None
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
class SurfaceAction:
    label: str
    href: str = ""
    tone: str = "neutral"
    method: str = ""
    title: str = ""
    disabled: bool = False
    feature: str = ""


@dataclass(frozen=True)
class SettingsOption:
    key: str
    label: str = ""
    selected: bool = False
    disabled: bool = False
    description: str = ""


@dataclass(frozen=True)
class AdminListColumn:
    key: str
    label: str = ""
    href: str = ""
    sortable: bool = False
    active: bool = False
    direction: str = ""
    align: str = "left"
    width: str = ""
    priority: int = 0
    hidden_mobile: bool = False
    title: str = ""


@dataclass(frozen=True)
class AdminListCell:
    key: str
    value: Any = ""
    label: str = ""
    href: str = ""
    tone: str = "neutral"
    title: str = ""
    detail: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    mono: bool = False
    nowrap: bool = False
    numeric: bool = False
    muted: bool = False


@dataclass(frozen=True)
class AdminListRow:
    key: str
    cells: Sequence[AdminListCell | Mapping[str, object]] = field(default_factory=tuple)
    href: str = ""
    tone: str = "neutral"
    title: str = ""
    summary: str = ""
    summary_privacy_scope: str = ""
    summary_safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class AdminListFilterField:
    name: str
    label: str = ""
    value: Any = ""
    kind: str = "text"
    placeholder: str = ""
    options: Sequence[SettingsOption | Mapping[str, object] | str] = field(default_factory=tuple)
    hidden: bool = False


@dataclass(frozen=True)
class AdminListPagination:
    count: str | int = ""
    page: str | int = ""
    page_count: str | int = ""
    previous_href: str = ""
    next_href: str = ""
    previous_label: str = "Previous"
    next_label: str = "Next"
    summary: str = ""


@dataclass(frozen=True)
class AdminListSurfaceConfig:
    enabled: bool = False
    feature: str = "admin_list"
    key: str = "admin-list"
    title: str = "Admin List"
    subtitle: str = ""
    columns: Sequence[AdminListColumn | Mapping[str, object] | str] = field(default_factory=tuple)
    rows: Sequence[AdminListRow | Mapping[str, object]] = field(default_factory=tuple)
    filters: Sequence[DashboardFilter | Mapping[str, object]] = field(default_factory=tuple)
    filter_fields: Sequence[AdminListFilterField | Mapping[str, object]] = field(default_factory=tuple)
    filter_action: str = ""
    filter_method: str = "get"
    filter_submit_label: str = "Filter"
    reset_href: str = ""
    status_tabs: Sequence[StatusTab | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    pagination: AdminListPagination | Mapping[str, object] | None = None
    empty_label: str = "No rows found."
    row_label: str = "row"
    table_label: str = ""
    card_label: str = ""
    mobile_card_primary_key: str = ""
    mobile_card_secondary_key: str = ""


@dataclass(frozen=True)
class DetailDossierHeader:
    title: str = ""
    subtitle: str = ""
    entity_type: str = ""
    eyebrow: str = ""
    status: str = ""
    tone: str = "neutral"
    href: str = ""
    avatar_url: str = ""
    avatar_alt: str = ""
    initials: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    privacy_scope: str = ""
    safe_alternate: str = ""


@dataclass(frozen=True)
class DetailDossierField:
    key: str
    label: str = ""
    value: Any = ""
    detail: str = ""
    href: str = ""
    tone: str = "neutral"
    title: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    mono: bool = False
    numeric: bool = False
    muted: bool = False
    wide: bool = False


@dataclass(frozen=True)
class DetailDossierMetric:
    key: str
    label: str
    value: Any = ""
    detail: str = ""
    href: str = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class DetailDossierTableColumn:
    key: str
    label: str = ""
    align: str = "left"
    title: str = ""
    hidden_mobile: bool = False


@dataclass(frozen=True)
class DetailDossierTableCell:
    key: str
    value: Any = ""
    label: str = ""
    href: str = ""
    tone: str = "neutral"
    detail: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    mono: bool = False
    numeric: bool = False
    muted: bool = False


@dataclass(frozen=True)
class DetailDossierTableRow:
    key: str
    cells: Sequence[DetailDossierTableCell | Mapping[str, object]] = field(default_factory=tuple)
    tone: str = "neutral"
    title: str = ""
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class DetailDossierSourceTable:
    key: str
    title: str = ""
    subtitle: str = ""
    columns: Sequence[DetailDossierTableColumn | Mapping[str, object] | str] = field(default_factory=tuple)
    rows: Sequence[DetailDossierTableRow | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No source rows."


@dataclass(frozen=True)
class DetailDossierSection:
    key: str
    title: str = ""
    subtitle: str = ""
    fields: Sequence[DetailDossierField | Mapping[str, object]] = field(default_factory=tuple)
    body: str = ""
    body_html: str = ""
    body_privacy_scope: str = ""
    body_safe_alternate: str = ""
    tone: str = "neutral"
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    table: DetailDossierSourceTable | Mapping[str, object] | None = None


@dataclass(frozen=True)
class DetailDossierTimelineEvent:
    key: str
    title: str
    when: str = ""
    summary: str = ""
    detail: str = ""
    actor: str = ""
    href: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class DetailDossierRelatedLink:
    key: str
    label: str
    href: str = ""
    summary: str = ""
    tone: str = "neutral"
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class DetailDossierAuditRow:
    key: str
    label: str
    value: Any = ""
    actor: str = ""
    when: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""


@dataclass(frozen=True)
class DetailDossierActionSlot:
    key: str
    label: str
    body: str = ""
    body_html: str = ""
    description: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class DetailDossierSurfaceConfig:
    enabled: bool = False
    feature: str = "detail_dossier"
    key: str = "detail-dossier"
    header: DetailDossierHeader | Mapping[str, object] | None = None
    fields: Sequence[DetailDossierField | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DetailDossierMetric | Mapping[str, object]] = field(default_factory=tuple)
    sections: Sequence[DetailDossierSection | Mapping[str, object]] = field(default_factory=tuple)
    source_tables: Sequence[DetailDossierSourceTable | Mapping[str, object]] = field(default_factory=tuple)
    timeline: Sequence[DetailDossierTimelineEvent | Mapping[str, object]] = field(default_factory=tuple)
    related_links: Sequence[DetailDossierRelatedLink | Mapping[str, object]] = field(default_factory=tuple)
    audit_rows: Sequence[DetailDossierAuditRow | Mapping[str, object]] = field(default_factory=tuple)
    action_slots: Sequence[DetailDossierActionSlot | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No detail data."


@dataclass(frozen=True)
class SettingsValidationMessage:
    message: str
    field_key: str = ""
    tone: str = "bad"
    title: str = ""


@dataclass(frozen=True)
class SettingsChange:
    label: str
    before: str | int | float | bool = ""
    after: str | int | float | bool = ""
    field_key: str = ""
    before_display: str = ""
    after_display: str = ""
    tone: str = "warn"
    secret: bool = False
    restart_required: bool = False


@dataclass(frozen=True)
class SettingsField:
    key: str
    label: str = ""
    name: str = ""
    kind: str = "text"
    value: Any = ""
    display_value: str = ""
    pending_value: Any = None
    pending_display_value: str = ""
    placeholder: str = ""
    help_text: str = ""
    status: str = ""
    tone: str = "neutral"
    required: bool = False
    readonly: bool = False
    disabled: bool = False
    secret: bool = False
    redacted: bool = False
    changed: bool = False
    restart_required: bool = False
    rows: int = 4
    min_value: str | int | float = ""
    max_value: str | int | float = ""
    step: str | int | float = ""
    autocomplete: str = ""
    input_mode: str = ""
    code_language: str = ""
    options: Sequence[SettingsOption | Mapping[str, object] | str] = field(default_factory=tuple)
    messages: Sequence[SettingsValidationMessage | Mapping[str, object] | str] = field(default_factory=tuple)
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SettingsGroup:
    key: str
    title: str
    description: str = ""
    fields: Sequence[SettingsField | Mapping[str, object]] = field(default_factory=tuple)
    status: str = ""
    tone: str = "neutral"
    restart_required: bool = False
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SettingsEditorConfig:
    enabled: bool = False
    feature: str = "settings_editor"
    key: str = "settings-editor"
    title: str = "Settings"
    subtitle: str = "Runtime-owned configuration"
    form_action: str = ""
    form_method: str = "post"
    groups: Sequence[SettingsGroup | Mapping[str, object]] = field(default_factory=tuple)
    changes: Sequence[SettingsChange | Mapping[str, object]] = field(default_factory=tuple)
    messages: Sequence[SettingsValidationMessage | Mapping[str, object] | str] = field(default_factory=tuple)
    banners: Sequence[FlashBanner | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    save_label: str = "Save settings"
    reset_label: str = "Reset"
    reset_href: str = ""
    restart_required: bool = False
    empty_label: str = "No editable settings configured."


@dataclass(frozen=True)
class SystemHealthCheck:
    key: str
    label: str = ""
    status: str = "unknown"
    tone: str = "neutral"
    value: str | int | float | bool = ""
    summary: str = ""
    detail: str = ""
    href: str = ""
    updated: str = ""
    required: bool = False
    blocked: bool = False
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemHealthGroup:
    key: str
    title: str
    description: str = ""
    status: str = ""
    tone: str = "neutral"
    checks: Sequence[SystemHealthCheck | Mapping[str, object]] = field(default_factory=tuple)
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemDatabaseCard:
    key: str
    label: str = "Database"
    status: str = "unknown"
    tone: str = "neutral"
    database: str = ""
    user: str = ""
    host: str = ""
    schema_version: str | int = ""
    tables: str | int = ""
    records: str | int = ""
    latency: str = ""
    summary: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemTableSummary:
    name: str
    status: str = "unknown"
    tone: str = "neutral"
    schema: str = ""
    rows: str | int = ""
    owner: str = ""
    updated: str = ""
    detail: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemAuditRow:
    key: str
    label: str
    action: str = ""
    actor: str = ""
    status: str = ""
    timestamp: str = ""
    summary: str = ""
    detail: str = ""
    tone: str = "neutral"
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemSecretCoverageRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    present: str | int = ""
    missing: str | int = ""
    required: str | int = ""
    optional: str | int = ""
    summary: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemReadinessProbe:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    summary: str = ""
    detail: str = ""
    checked_at: str = ""
    required: bool = True
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class SystemHealthSurfaceConfig:
    enabled: bool = False
    feature: str = "system_health"
    key: str = "system-health"
    title: str = "System Health"
    subtitle: str = "Runtime, database, audit, and readiness posture"
    tabs: Sequence[StatusTab | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    health_groups: Sequence[SystemHealthGroup | Mapping[str, object]] = field(default_factory=tuple)
    databases: Sequence[SystemDatabaseCard | Mapping[str, object]] = field(default_factory=tuple)
    tables: Sequence[SystemTableSummary | Mapping[str, object]] = field(default_factory=tuple)
    audit_rows: Sequence[SystemAuditRow | Mapping[str, object]] = field(default_factory=tuple)
    secret_coverage: Sequence[SystemSecretCoverageRow | Mapping[str, object]] = field(default_factory=tuple)
    readiness: Sequence[SystemReadinessProbe | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No system posture data configured."


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
class CommandParsedField:
    key: str
    label: str
    value: str | int | float | bool = ""
    status: str = ""
    tone: str = "neutral"
    detail: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommandCandidateRow:
    key: str
    label: str
    kind: str = ""
    score: str | int | float = ""
    status: str = ""
    tone: str = "neutral"
    summary: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommandRiskRow:
    key: str
    label: str
    severity: str = ""
    status: str = ""
    tone: str = "neutral"
    summary: str = ""
    detail: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommandConfirmationStep:
    key: str
    label: str
    status: str = "pending"
    tone: str = "neutral"
    detail: str = ""
    required: bool = True
    completed: bool = False
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommandQueueRow:
    key: str
    label: str
    status: str = "queued"
    tone: str = "neutral"
    command: str = ""
    actor: str = ""
    target: str = ""
    timestamp: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommandHistoryRow:
    key: str
    label: str
    result: str = ""
    tone: str = "neutral"
    command: str = ""
    actor: str = ""
    target: str = ""
    timestamp: str = ""
    duration: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class CommandIntakeSurfaceConfig:
    enabled: bool = False
    feature: str = "command_intake"
    key: str = "command-intake"
    title: str = "Command Intake"
    subtitle: str = "Parsed command preview, risk posture, confirmation state, queue, and history"
    tabs: Sequence[StatusTab | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    form_action: str = ""
    form_method: str = "post"
    input_name: str = "command"
    input_label: str = "Command"
    input_placeholder: str = "Describe the operator intent..."
    input_value: str = ""
    input_privacy_scope: str = ""
    input_safe_alternate: str = ""
    submit_label: str = "Preview"
    queue_label: str = "Queue command"
    queue_href: str = ""
    queue_method: str = "post"
    parsed_fields: Sequence[CommandParsedField | Mapping[str, object]] = field(default_factory=tuple)
    candidates: Sequence[CommandCandidateRow | Mapping[str, object]] = field(default_factory=tuple)
    risks: Sequence[CommandRiskRow | Mapping[str, object]] = field(default_factory=tuple)
    confirmations: Sequence[CommandConfirmationStep | Mapping[str, object]] = field(default_factory=tuple)
    queue: Sequence[CommandQueueRow | Mapping[str, object]] = field(default_factory=tuple)
    history: Sequence[CommandHistoryRow | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No command preview data configured."


@dataclass(frozen=True)
class AvailabilityWindowRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    starts_at: str = ""
    ends_at: str = ""
    timezone: str = ""
    recurrence: str = ""
    channel: str = ""
    summary: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class AvailabilityMonitorRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    value: str | int | float | bool = ""
    target: str | int | float | bool = ""
    last_seen: str = ""
    next_check: str = ""
    detail: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class AvailabilityPolicyRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    requirement: str = ""
    summary: str = ""
    detail: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class AvailabilityScenarioRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    current_step: str = ""
    expected_result: str = ""
    last_run: str = ""
    next_run: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class AvailabilityEventRow:
    key: str
    label: str
    status: str = ""
    tone: str = "neutral"
    timestamp: str = ""
    source: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class AvailabilityMonitorSurfaceConfig:
    enabled: bool = False
    feature: str = "availability_monitor"
    key: str = "availability-monitor"
    title: str = "Availability Monitor"
    subtitle: str = "Schedule windows, live checks, policy posture, scenarios, and events"
    tabs: Sequence[StatusTab | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    windows: Sequence[AvailabilityWindowRow | Mapping[str, object]] = field(default_factory=tuple)
    monitors: Sequence[AvailabilityMonitorRow | Mapping[str, object]] = field(default_factory=tuple)
    policies: Sequence[AvailabilityPolicyRow | Mapping[str, object]] = field(default_factory=tuple)
    scenarios: Sequence[AvailabilityScenarioRow | Mapping[str, object]] = field(default_factory=tuple)
    events: Sequence[AvailabilityEventRow | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No availability monitor items configured."


@dataclass(frozen=True)
class OpsStatusCard:
    label: str
    status: str
    href: str = ""
    detail: str = ""
    meta: str = ""
    tone: str = "neutral"
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class OpsTableRow:
    key: str
    label: str
    status: str = ""
    href: str = ""
    detail: str = ""
    owner: str = ""
    timestamp: str = ""
    tone: str = "neutral"
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class OpsLogEvent:
    label: str
    message: str
    timestamp: str = ""
    source: str = ""
    level: str = ""
    href: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class OpsSettingItem:
    label: str
    value: str | int | float | bool = ""
    status: str = ""
    href: str = ""
    detail: str = ""
    tone: str = "neutral"
    secret: bool = False
    changed: bool = False
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class OperationsSurfaceConfig:
    enabled: bool = False
    feature: str = "operations"
    title: str = "Operations"
    subtitle: str = "Workers, tasks, logs, and settings posture"
    status_cards: Sequence[OpsStatusCard | Mapping[str, object]] = field(default_factory=tuple)
    tasks: Sequence[OpsTableRow | Mapping[str, object]] = field(default_factory=tuple)
    logs: Sequence[OpsLogEvent | Mapping[str, object]] = field(default_factory=tuple)
    settings: Sequence[OpsSettingItem | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No operational items found."


@dataclass(frozen=True)
class PersonaPanel:
    label: str
    value: str | int | float = ""
    href: str = ""
    summary: str = ""
    detail: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class ContinuityItem:
    label: str
    title: str
    summary: str = ""
    href: str = ""
    timestamp: str = ""
    kind: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaRuntimeSurfaceConfig:
    enabled: bool = False
    feature: str = "persona"
    title: str = "Persona Runtime"
    subtitle: str = "Persona state, continuity, and memory posture"
    panels: Sequence[PersonaPanel | Mapping[str, object]] = field(default_factory=tuple)
    continuity: Sequence[ContinuityItem | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No persona runtime items found."


@dataclass(frozen=True)
class PersonaProfileField:
    key: str
    label: str
    value: str | int | float | bool = ""
    detail: str = ""
    href: str = ""
    status: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaProfileSection:
    key: str
    title: str
    description: str = ""
    status: str = ""
    tone: str = "neutral"
    fields: Sequence[PersonaProfileField | Mapping[str, object]] = field(default_factory=tuple)
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaTraitRow:
    key: str
    label: str
    value: str | int | float = ""
    intensity: str | int | float = ""
    status: str = ""
    tone: str = "neutral"
    summary: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaRuleRow:
    key: str
    label: str
    rule: str = ""
    category: str = ""
    priority: str | int = ""
    status: str = ""
    tone: str = "neutral"
    summary: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaStateField:
    key: str
    label: str
    value: str | int | float | bool = ""
    display_value: str = ""
    pending_value: str | int | float | bool = ""
    pending_display_value: str = ""
    field_type: str = "text"
    status: str = ""
    tone: str = "neutral"
    detail: str = ""
    changed: bool = False
    secret: bool = False
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaChangeRow:
    key: str
    label: str
    before: str | int | float | bool = ""
    after: str | int | float | bool = ""
    status: str = ""
    tone: str = "neutral"
    actor: str = ""
    timestamp: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaProposalCard:
    key: str
    title: str
    status: str = "pending"
    tone: str = "warn"
    summary: str = ""
    source: str = ""
    target: str = ""
    proposed_by: str = ""
    updated: str = ""
    href: str = ""
    changes: Sequence[PersonaChangeRow | Mapping[str, object]] = field(default_factory=tuple)
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class PersonaEditorConfig:
    enabled: bool = False
    feature: str = "persona_editor"
    key: str = "persona-editor"
    title: str = "Persona Editor"
    subtitle: str = "Profile, traits, rules, mutable state, proposals, and change history"
    tabs: Sequence[StatusTab | Mapping[str, object]] = field(default_factory=tuple)
    profile_sections: Sequence[PersonaProfileSection | Mapping[str, object]] = field(default_factory=tuple)
    traits: Sequence[PersonaTraitRow | Mapping[str, object]] = field(default_factory=tuple)
    rules: Sequence[PersonaRuleRow | Mapping[str, object]] = field(default_factory=tuple)
    state_fields: Sequence[PersonaStateField | Mapping[str, object]] = field(default_factory=tuple)
    proposals: Sequence[PersonaProposalCard | Mapping[str, object]] = field(default_factory=tuple)
    history: Sequence[PersonaChangeRow | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No persona editor items configured."


@dataclass(frozen=True)
class BridgeStatusCard:
    label: str
    status: str
    href: str = ""
    route: str = ""
    detail: str = ""
    last_seen: str = ""
    tone: str = "neutral"
    counts: Sequence[str | Mapping[str, object]] = field(default_factory=tuple)
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class BridgeWebhookRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    method: str = ""
    path: str = ""
    verification: str = ""
    last_seen: str = ""
    detail: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class BridgeQueueRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    queued: str | int = ""
    failed: str | int = ""
    claimed: str | int = ""
    last_in: str = ""
    last_out: str = ""
    policy: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class BridgeHeartbeatRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    checkpoint: str = ""
    latency: str = ""
    last_seen: str = ""
    detail: str = ""
    href: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class BridgeProviderCapabilityRow:
    key: str
    label: str
    provider: str = ""
    capability: str = ""
    status: str = "unknown"
    tone: str = "neutral"
    configured: bool = False
    enabled: bool = False
    docs_href: str = ""
    detail: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class BridgeDeliveryRow:
    key: str
    label: str
    status: str = "unknown"
    tone: str = "neutral"
    direction: str = ""
    provider: str = ""
    target: str = ""
    attempts: str | int = ""
    timestamp: str = ""
    detail: str = ""
    href: str = ""
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class BridgeOpsSurfaceConfig:
    enabled: bool = False
    feature: str = "bridge_ops"
    key: str = "bridge-ops"
    title: str = "Bridge Operations"
    subtitle: str = "Provider-neutral webhook, queue, heartbeat, capability, and delivery posture"
    tabs: Sequence[StatusTab | Mapping[str, object]] = field(default_factory=tuple)
    metrics: Sequence[DashboardMetric | Mapping[str, object]] = field(default_factory=tuple)
    bridges: Sequence[BridgeStatusCard | Mapping[str, object]] = field(default_factory=tuple)
    webhooks: Sequence[BridgeWebhookRow | Mapping[str, object]] = field(default_factory=tuple)
    queues: Sequence[BridgeQueueRow | Mapping[str, object]] = field(default_factory=tuple)
    heartbeats: Sequence[BridgeHeartbeatRow | Mapping[str, object]] = field(default_factory=tuple)
    providers: Sequence[BridgeProviderCapabilityRow | Mapping[str, object]] = field(default_factory=tuple)
    deliveries: Sequence[BridgeDeliveryRow | Mapping[str, object]] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    empty_label: str = "No bridge operation items configured."


@dataclass(frozen=True)
class AgentSessionRow:
    key: str
    title: str
    status: str = ""
    href: str = ""
    objective: str = ""
    model: str = ""
    reasoning: str = ""
    repo: str = ""
    updated: str = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)


@dataclass(frozen=True)
class TerminalStreamEvent:
    key: str
    text: str
    timestamp: str = ""
    role: str = "output"
    label: str = ""
    source: str = ""
    sequence: str | int = ""
    tone: str = "neutral"
    privacy_scope: str = ""
    safe_alternate: str = ""
    truncated: bool = False
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)


@dataclass(frozen=True)
class TerminalStreamConfig:
    enabled: bool = False
    feature: str = "terminal_stream"
    key: str = "terminal-stream"
    title: str = "Terminal Stream"
    subtitle: str = "Read-only current event window"
    status: str = ""
    status_tone: str = "neutral"
    events: Sequence[TerminalStreamEvent | Mapping[str, object]] = field(default_factory=tuple)
    initial_position: str = "current"
    window_label: str = "Current buffered window"
    before_cursor: str = ""
    after_cursor: str = ""
    history_url: str = ""
    stream_url: str = ""
    poll_interval_ms: int = 4000
    max_rendered_events: int = 200
    has_more_before: bool = False
    has_more_after: bool = True
    truncated_before: bool = False
    truncated_after: bool = False
    autoscroll: bool = True
    empty_label: str = "No terminal events in the current window."


@dataclass(frozen=True)
class AgentOpsSurfaceConfig:
    enabled: bool = False
    feature: str = "agent_ops"
    title: str = "Bridge And Agent Ops"
    subtitle: str = "Integration bridges, sessions, preflight, and read-only operational posture"
    bridges: Sequence[BridgeStatusCard | Mapping[str, object]] = field(default_factory=tuple)
    sessions: Sequence[AgentSessionRow | Mapping[str, object]] = field(default_factory=tuple)
    statuses: Sequence[OpsStatusCard | Mapping[str, object]] = field(default_factory=tuple)
    terminal_stream: TerminalStreamConfig | Mapping[str, object] | None = None
    empty_label: str = "No bridge or agent operations found."


@dataclass(frozen=True)
class JournalMarker:
    label: str
    tone: str = "neutral"
    title: str = ""


@dataclass(frozen=True)
class JournalDetail:
    label: str
    value: str | int | float | bool = ""
    tone: str = "neutral"


@dataclass(frozen=True)
class JournalCalendarDay:
    date: str
    day: str | int
    href: str = ""
    in_month: bool = True
    has_entry: bool = False
    selected: bool = False
    title: str = ""
    markers: Sequence[JournalMarker | SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    privacy_scope: str = ""


@dataclass(frozen=True)
class JournalEntry:
    key: str
    date: str
    title: str
    text: str = ""
    href: str = ""
    subtitle: str = ""
    author_label: str = "Persona"
    privacy_label: str = ""
    timestamp: str = ""
    summary: str = ""
    legacy: bool = False
    legacy_label: str = "Legacy continuity format"
    previous_href: str = ""
    next_href: str = ""
    previous_label: str = "Previous Page"
    next_label: str = "Next Page"
    details_title: str = "Source And Provenance"
    details: Sequence[JournalDetail | Mapping[str, object]] = field(default_factory=tuple)
    markers: Sequence[JournalMarker | SurfaceBadge | Mapping[str, object] | str] = field(default_factory=tuple)
    actions: Sequence[SurfaceAction | Mapping[str, object]] = field(default_factory=tuple)
    privacy_scope: str = ""
    safe_alternate: str = ""


@dataclass(frozen=True)
class JournalThemeOption:
    key: str
    label: str
    href: str = ""
    selected: bool = False
    title: str = ""


@dataclass(frozen=True)
class JournalSurfaceConfig:
    enabled: bool = False
    feature: str = "journal"
    title: str = "Journal"
    subtitle: str = "Continuity pages"
    month_label: str = ""
    previous_month_href: str = ""
    next_month_href: str = ""
    previous_month_label: str = "Prev"
    next_month_label: str = "Next"
    calendar: Sequence[JournalCalendarDay | Mapping[str, object]] = field(default_factory=tuple)
    entry: JournalEntry | Mapping[str, object] | None = None
    entries: Sequence[JournalEntry | Mapping[str, object]] = field(default_factory=tuple)
    theme: str = "paper"
    theme_options: Sequence[JournalThemeOption | Mapping[str, object] | str] = field(default_factory=tuple)
    empty_label: str = "No journal entry selected."
    calendar_empty_label: str = "No journal days available."


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
