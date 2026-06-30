from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    AgentOpsSurfaceConfig,
    AgentSessionRow,
    BridgeStatusCard,
    ContinuityItem,
    OpsLogEvent,
    OpsSettingItem,
    OpsStatusCard,
    OpsTableRow,
    OperationsSurfaceConfig,
    PersonaPanel,
    PersonaRuntimeSurfaceConfig,
    SurfaceAction,
    SurfaceBadge,
)
from .privacy import (
    WITHHELD_PRIVATE_TEXT,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    PrivacyRenderMode,
    can_view_raw_private,
    feature_enabled,
    privacy_render_mode,
    render_private_text,
)
from .terminal import render_terminal_stream

OPERATIONS_FEATURE = "operations"
PERSONA_RUNTIME_FEATURE = "persona"
AGENT_OPS_FEATURE = "agent_ops"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "critical": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "fail": "bad",
    "missing": "bad",
    "red": "bad",
    "rose": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
    "held": "warn",
    "hold": "warn",
    "lagging": "warn",
    "pending": "warn",
    "queued": "warn",
    "review": "warn",
    "amber": "warn",
    "yellow": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "applied": "good",
    "approved": "good",
    "green": "good",
    "info": "info",
    "blue": "info",
    "cyan": "info",
    "neutral": "neutral",
    "unknown": "neutral",
    "": "neutral",
}


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _coerce(value: T | Mapping[str, object], cls: type[T], defaults: Mapping[str, Any] | None = None) -> T:
    if isinstance(value, cls):
        return value
    data = {**(defaults or {}), **_mapping(value)}
    allowed = {field.name for field in fields(cls)}
    data = {key: value for key, value in data.items() if key in allowed}
    return cls(**data)


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
    return "".join(parts)


def _link_or_tag(tag: str, href: str, class_name: str, body: str, *, title: str = "") -> str:
    if href:
        return f'<a class="{class_name}" href="{escape(href, quote=True)}"{_attrs(title=title)}>{body}</a>'
    return f'<{tag} class="{class_name}"{_attrs(title=title)}>{body}</{tag}>'


def _panel_head(title: str, subtitle: str) -> str:
    return (
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(subtitle))}</div>'
        "</div></div>"
    )


def _private_text(
    text: object,
    *,
    privacy_scope: str,
    safe_alternate: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not privacy_scope:
        return str(text or "")
    if policy is None:
        return str(safe_alternate or "").strip() or WITHHELD_PRIVATE_TEXT
    return render_private_text(
        str(text or ""),
        safe_alternate=safe_alternate,
        policy=policy,
        context=context,
        scope=privacy_scope,
    )


def _raw_href(
    href: str,
    *,
    privacy_scope: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not href or not privacy_scope:
        return href
    if policy is None:
        return ""
    if not policy.is_owner_private_scope(privacy_scope):
        return href
    return href if can_view_raw_private(policy, context, privacy_scope) else ""


def _private_class(
    *,
    privacy_scope: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not privacy_scope:
        return ""
    if policy is None:
        return " is-private"
    mode = privacy_render_mode(
        policy,
        context,
        privacy_scope,
        has_safe_alternate=False,
        hide_without_safe_alternate=True,
    )
    return " is-private" if mode != PrivacyRenderMode.RAW else ""


def _badge_html(raw_badge: SurfaceBadge | Mapping[str, object] | str) -> str:
    badge = SurfaceBadge(str(raw_badge)) if isinstance(raw_badge, str) else _coerce(raw_badge, SurfaceBadge)
    if not badge.label:
        return ""
    return f'<span class="pc-surface-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-surface-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], features: Mapping[str, bool] | None) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label:
        return ""
    if action.feature and not feature_enabled(features, action.feature, default=True):
        return ""
    tone = _tone(action.tone)
    method = str(action.method or "").strip().upper()
    method_attr = f' data-method="{escape(method, quote=True)}"' if method else ""
    title = f' title="{escape(str(action.title), quote=True)}"' if action.title else ""
    body = escape(str(action.label))
    cls = f"pc-workflow-action pc-dashboard-tone-{tone}"
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{title}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(action.href, quote=True)}"{method_attr}{title}>{body}</a>'


def _actions_html(
    actions: Sequence[SurfaceAction | Mapping[str, object]],
    features: Mapping[str, bool] | None,
) -> str:
    body = "".join(_action_html(action, features) for action in actions)
    return f'<div class="pc-workflow-actions">{body}</div>' if body else ""


def operations_surface_feature_enabled(
    config: OperationsSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, OperationsSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or OPERATIONS_FEATURE), default=True)


def persona_runtime_surface_feature_enabled(
    config: PersonaRuntimeSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, PersonaRuntimeSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or PERSONA_RUNTIME_FEATURE),
        default=True,
    )


def agent_ops_surface_feature_enabled(
    config: AgentOpsSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, AgentOpsSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or AGENT_OPS_FEATURE), default=True)


def _ops_status_card_html(
    raw_card: OpsStatusCard | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
) -> str:
    card = _coerce(raw_card, OpsStatusCard)
    body = (
        '<div class="pc-workflow-card-head">'
        f"<strong>{escape(str(card.label))}</strong>"
        f'<span class="pc-surface-status pc-dashboard-tone-{_tone(card.tone or card.status)}">{escape(str(card.status))}</span>'
        "</div>"
        + (f'<div class="pc-workflow-card-subtitle">{escape(str(card.meta))}</div>' if card.meta else "")
        + (f"<p>{escape(str(card.detail))}</p>" if card.detail else "")
        + _badges_html(card.badges)
        + _actions_html(card.actions, features)
    )
    href = "" if card.actions else card.href
    return _link_or_tag("article", href, f"pc-ops-card pc-dashboard-tone-{_tone(card.tone or card.status)}", body)


def _ops_row_html(raw_row: OpsTableRow | Mapping[str, object], *, features: Mapping[str, bool] | None) -> str:
    row = _coerce(raw_row, OpsTableRow)
    meta = "".join(
        part
        for part in [
            f"<span>{escape(str(row.owner))}</span>" if row.owner else "",
            f"<time>{escape(str(row.timestamp))}</time>" if row.timestamp else "",
        ]
    )
    body = (
        '<div class="pc-workflow-row-main">'
        '<div class="pc-workflow-row-title">'
        f"<strong>{escape(str(row.label))}</strong>"
        + (
            f'<span class="pc-surface-status pc-dashboard-tone-{_tone(row.tone or row.status)}">'
            f"{escape(str(row.status))}</span>"
            if row.status
            else ""
        )
        + "</div>"
        + (f'<div class="pc-workflow-row-meta-inline">{meta}</div>' if meta else "")
        + (f"<p>{escape(str(row.detail))}</p>" if row.detail else "")
        + _badges_html(row.badges)
        + "</div>"
        + _actions_html(row.actions, features)
    )
    href = "" if row.actions else row.href
    return _link_or_tag("article", href, f"pc-workflow-row pc-ops-row pc-dashboard-tone-{_tone(row.tone or row.status)}", body)


def _ops_log_html(
    raw_log: OpsLogEvent | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    log = _coerce(raw_log, OpsLogEvent)
    message = _private_text(
        log.message,
        privacy_scope=log.privacy_scope,
        safe_alternate=log.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(log.href, privacy_scope=log.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=log.privacy_scope, policy=policy, context=context)
    tone = _tone(log.tone or log.level)
    body = (
        '<span class="pc-dashboard-activity-dot" aria-hidden="true"></span>'
        '<div class="pc-dashboard-activity-main">'
        '<div class="pc-dashboard-activity-title-row">'
        f'<span class="pc-dashboard-activity-label">{escape(str(log.label))}</span>'
        f"<strong>{escape(message)}</strong>"
        f"<time>{escape(str(log.timestamp))}</time></div>"
        '<div class="pc-surface-row-meta">'
        + (f"<span>{escape(str(log.level))}</span>" if log.level else "")
        + (f"<span>{escape(str(log.source))}</span>" if log.source else "")
        + _badges_html(log.badges)
        + "</div></div>"
    )
    return _link_or_tag(
        "article",
        href,
        f"pc-dashboard-activity-item pc-ops-log pc-dashboard-tone-{tone}{private}",
        body,
    )


def _setting_value(setting: OpsSettingItem) -> str:
    if setting.secret:
        return "configured" if bool(setting.value) else "not configured"
    if isinstance(setting.value, bool):
        return "on" if setting.value else "off"
    return str(setting.value if setting.value is not None else "")


def _ops_setting_html(raw_setting: OpsSettingItem | Mapping[str, object], *, features: Mapping[str, bool] | None) -> str:
    setting = _coerce(raw_setting, OpsSettingItem)
    value = _setting_value(setting)
    changed = '<span class="pc-surface-badge pc-dashboard-tone-warn">changed</span>' if setting.changed else ""
    body = (
        '<div class="pc-workflow-row-main">'
        '<div class="pc-workflow-row-title">'
        f"<strong>{escape(str(setting.label))}</strong>"
        f'<span class="pc-surface-status pc-dashboard-tone-{_tone(setting.tone or setting.status)}">'
        f"{escape(str(setting.status or value))}</span>"
        "</div>"
        + (f'<p>{escape(str(setting.detail))}</p>' if setting.detail else "")
        + f'<div class="pc-workflow-row-meta-inline"><span>{escape(value)}</span>{changed}</div>'
        + _badges_html(setting.badges)
        + "</div>"
        + _actions_html(setting.actions, features)
    )
    href = "" if setting.actions else setting.href
    return _link_or_tag(
        "article",
        href,
        f"pc-workflow-row pc-setting-row pc-dashboard-tone-{_tone(setting.tone or setting.status)}",
        body,
    )


def render_operations_surface(
    config: OperationsSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, OperationsSurfaceConfig)
    if not operations_surface_feature_enabled(model, features):
        return ""
    cards = "".join(_ops_status_card_html(card, features=features) for card in model.status_cards)
    tasks = "".join(_ops_row_html(row, features=features) for row in model.tasks)
    logs = "".join(_ops_log_html(log, policy=privacy_policy, context=privacy_context) for log in model.logs)
    settings = "".join(_ops_setting_html(setting, features=features) for setting in model.settings)
    empty = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>' if not cards + tasks + logs + settings else ""
    return (
        '<section id="operations" class="pc-operations-surface pc-dashboard-panel pc-workflow-surface">'
        f"{_panel_head(model.title, model.subtitle)}"
        + (f'<div class="pc-workflow-card-grid">{cards}</div>' if cards else "")
        + (
            '<div class="pc-workflow-subsection"><div class="pc-dashboard-section-title">Tasks</div>'
            f'<div class="pc-workflow-list">{tasks}</div></div>'
            if tasks
            else ""
        )
        + (
            '<div class="pc-workflow-subsection"><div class="pc-dashboard-section-title">Logs</div>'
            f'<div class="pc-dashboard-activity-list">{logs}</div></div>'
            if logs
            else ""
        )
        + (
            '<div class="pc-workflow-subsection"><div class="pc-dashboard-section-title">Settings Posture</div>'
            f'<div class="pc-workflow-list">{settings}</div></div>'
            if settings
            else ""
        )
        + empty
        + "</section>"
    )


def _persona_panel_html(
    raw_panel: PersonaPanel | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    panel = _coerce(raw_panel, PersonaPanel)
    label = _private_text(
        panel.label,
        privacy_scope=panel.privacy_scope,
        safe_alternate=panel.safe_alternate,
        policy=policy,
        context=context,
    )
    summary = _private_text(
        panel.summary,
        privacy_scope=panel.privacy_scope,
        safe_alternate=panel.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        panel.detail,
        privacy_scope=panel.privacy_scope,
        safe_alternate="",
        policy=policy,
        context=context,
    )
    href = _raw_href(panel.href, privacy_scope=panel.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=panel.privacy_scope, policy=policy, context=context)
    value = str(panel.value if panel.value is not None else "")
    body = (
        '<div class="pc-workflow-card-head">'
        f"<strong>{escape(label)}</strong>"
        + (f'<span class="pc-surface-status pc-dashboard-tone-{_tone(panel.tone)}">{escape(value)}</span>' if value else "")
        + "</div>"
        + (f"<p>{escape(summary)}</p>" if summary else "")
        + (f"<small>{escape(detail)}</small>" if detail else "")
        + _badges_html(panel.badges)
        + _actions_html(panel.actions, features)
    )
    row_href = "" if panel.actions else href
    return _link_or_tag("article", row_href, f"pc-persona-panel pc-dashboard-tone-{_tone(panel.tone)}{private}", body)


def _continuity_item_html(
    raw_item: ContinuityItem | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    item = _coerce(raw_item, ContinuityItem)
    title = _private_text(
        item.title,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    summary = _private_text(
        item.summary,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(item.href, privacy_scope=item.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=item.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-workflow-row-main">'
        '<div class="pc-workflow-row-title">'
        f"<strong>{escape(title)}</strong>"
        + (f'<span class="pc-surface-status pc-dashboard-tone-{_tone(item.tone)}">{escape(str(item.label))}</span>' if item.label else "")
        + "</div>"
        '<div class="pc-workflow-row-meta-inline">'
        + (f"<span>{escape(str(item.kind))}</span>" if item.kind else "")
        + (f"<time>{escape(str(item.timestamp))}</time>" if item.timestamp else "")
        + "</div>"
        + (f"<p>{escape(summary)}</p>" if summary else "")
        + _badges_html(item.badges)
        + "</div>"
        + _actions_html(item.actions, features)
    )
    row_href = "" if item.actions else href
    return _link_or_tag(
        "article",
        row_href,
        f"pc-workflow-row pc-continuity-row pc-dashboard-tone-{_tone(item.tone)}{private}",
        body,
    )


def render_persona_runtime_surface(
    config: PersonaRuntimeSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, PersonaRuntimeSurfaceConfig)
    if not persona_runtime_surface_feature_enabled(model, features):
        return ""
    panels = [
        _persona_panel_html(panel, features=features, policy=privacy_policy, context=privacy_context)
        for panel in model.panels
    ]
    continuity = [
        _continuity_item_html(item, features=features, policy=privacy_policy, context=privacy_context)
        for item in model.continuity
    ]
    empty = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>' if not panels + continuity else ""
    return (
        '<section id="persona-runtime" class="pc-persona-surface pc-dashboard-panel pc-workflow-surface">'
        f"{_panel_head(model.title, model.subtitle)}"
        + (f'<div class="pc-workflow-card-grid">{"".join(panels)}</div>' if panels else "")
        + (
            '<div class="pc-workflow-subsection"><div class="pc-dashboard-section-title">Continuity</div>'
            f'<div class="pc-workflow-list">{"".join(continuity)}</div></div>'
            if continuity
            else ""
        )
        + empty
        + "</section>"
    )


def _count_badges_html(counts: Sequence[str | Mapping[str, object]]) -> str:
    badges: list[str] = []
    for raw_count in counts:
        if isinstance(raw_count, Mapping):
            label = str(raw_count.get("label") or raw_count.get("value") or "")
            tone = _tone(raw_count.get("tone"))
        else:
            label = str(raw_count or "")
            tone = "neutral"
        if label:
            badges.append(f'<span class="pc-surface-badge pc-dashboard-tone-{tone}">{escape(label)}</span>')
    return f'<div class="pc-surface-badges">{"".join(badges)}</div>' if badges else ""


def _bridge_card_html(raw_bridge: BridgeStatusCard | Mapping[str, object], *, features: Mapping[str, bool] | None) -> str:
    bridge = _coerce(raw_bridge, BridgeStatusCard)
    body = (
        '<div class="pc-workflow-card-head">'
        f"<strong>{escape(str(bridge.label))}</strong>"
        f'<span class="pc-surface-status pc-dashboard-tone-{_tone(bridge.tone or bridge.status)}">{escape(str(bridge.status))}</span>'
        "</div>"
        '<div class="pc-workflow-row-meta-inline">'
        + (f"<span>{escape(str(bridge.route))}</span>" if bridge.route else "")
        + (f"<time>{escape(str(bridge.last_seen))}</time>" if bridge.last_seen else "")
        + "</div>"
        + (f"<p>{escape(str(bridge.detail))}</p>" if bridge.detail else "")
        + _count_badges_html(bridge.counts)
        + _badges_html(bridge.badges)
        + _actions_html(bridge.actions, features)
    )
    row_href = "" if bridge.actions else bridge.href
    return _link_or_tag("article", row_href, f"pc-bridge-card pc-dashboard-tone-{_tone(bridge.tone or bridge.status)}", body)


def _agent_session_html(
    raw_session: AgentSessionRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    session = _coerce(raw_session, AgentSessionRow)
    title = _private_text(
        session.title,
        privacy_scope=session.privacy_scope,
        safe_alternate=session.safe_alternate,
        policy=policy,
        context=context,
    )
    objective = _private_text(
        session.objective,
        privacy_scope=session.privacy_scope,
        safe_alternate=session.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(session.href, privacy_scope=session.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=session.privacy_scope, policy=policy, context=context)
    meta = "".join(
        part
        for part in [
            f"<span>{escape(str(session.model))}</span>" if session.model else "",
            f"<span>{escape(str(session.reasoning))}</span>" if session.reasoning else "",
            f"<span>{escape(str(session.repo))}</span>" if session.repo else "",
            f"<time>{escape(str(session.updated))}</time>" if session.updated else "",
        ]
    )
    body = (
        '<div class="pc-workflow-row-main">'
        '<div class="pc-workflow-row-title">'
        f"<strong>{escape(title)}</strong>"
        + (
            f'<span class="pc-surface-status pc-dashboard-tone-{_tone(session.tone or session.status)}">'
            f"{escape(str(session.status))}</span>"
            if session.status
            else ""
        )
        + "</div>"
        + (f'<div class="pc-workflow-row-meta-inline">{meta}</div>' if meta else "")
        + (f"<p>{escape(objective)}</p>" if objective else "")
        + _badges_html(session.badges)
        + "</div>"
        + _actions_html(session.actions, features)
    )
    row_href = "" if session.actions else href
    return _link_or_tag(
        "article",
        row_href,
        f"pc-workflow-row pc-agent-session pc-dashboard-tone-{_tone(session.tone or session.status)}{private}",
        body,
    )


def render_agent_ops_surface(
    config: AgentOpsSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, AgentOpsSurfaceConfig)
    if not agent_ops_surface_feature_enabled(model, features):
        return ""
    bridges = "".join(_bridge_card_html(bridge, features=features) for bridge in model.bridges)
    statuses = "".join(_ops_status_card_html(status, features=features) for status in model.statuses)
    terminal = render_terminal_stream(
        model.terminal_stream,
        features=features,
        privacy_policy=privacy_policy,
        privacy_context=privacy_context,
    )
    sessions = [
        _agent_session_html(
            session,
            features=features,
            policy=privacy_policy,
            context=privacy_context,
        )
        for session in model.sessions
    ]
    empty = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>' if not bridges + statuses + "".join(sessions) + terminal else ""
    return (
        '<section id="agent-ops" class="pc-agent-ops-surface pc-dashboard-panel pc-workflow-surface">'
        f"{_panel_head(model.title, model.subtitle)}"
        + (f'<div class="pc-workflow-card-grid">{bridges}{statuses}</div>' if bridges or statuses else "")
        + (
            '<div class="pc-workflow-subsection"><div class="pc-dashboard-section-title">Sessions</div>'
            f'<div class="pc-workflow-list">{"".join(sessions)}</div></div>'
            if sessions
            else ""
        )
        + terminal
        + empty
        + "</section>"
    )


def render_workflow_sections(
    *,
    operations: OperationsSurfaceConfig | Mapping[str, object] | None = None,
    persona: PersonaRuntimeSurfaceConfig | Mapping[str, object] | None = None,
    agent_ops: AgentOpsSurfaceConfig | Mapping[str, object] | None = None,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    sections = [
        render_operations_surface(
            operations,
            features=features,
            privacy_policy=privacy_policy,
            privacy_context=privacy_context,
        ),
        render_persona_runtime_surface(
            persona,
            features=features,
            privacy_policy=privacy_policy,
            privacy_context=privacy_context,
        ),
        render_agent_ops_surface(
            agent_ops,
            features=features,
            privacy_policy=privacy_policy,
            privacy_context=privacy_context,
        ),
    ]
    return "\n".join(section for section in sections if section)
