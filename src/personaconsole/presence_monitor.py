from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    DashboardMetric,
    PresenceChannelRow,
    PresenceMonitorSurfaceConfig,
    PresencePolicyNotice,
    PresenceScheduleWindow,
    PresenceSourceFreshnessRow,
    PresenceStateCard,
    PresenceTransitionRow,
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
from .render import render_live_controls

PRESENCE_MONITOR_FEATURE = "presence_monitor"

T = TypeVar("T")

_TONE_ALIASES = {
    "active": "good",
    "available": "good",
    "away": "warn",
    "bad": "bad",
    "blocked": "bad",
    "busy": "warn",
    "closed": "neutral",
    "danger": "bad",
    "degraded": "warn",
    "disabled": "neutral",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "good": "good",
    "healthy": "good",
    "held": "warn",
    "hidden": "neutral",
    "idle": "neutral",
    "info": "info",
    "live": "good",
    "missing": "bad",
    "neutral": "neutral",
    "offline": "neutral",
    "online": "good",
    "paused": "warn",
    "private": "warn",
    "ready": "good",
    "scheduled": "info",
    "stale": "warn",
    "unknown": "neutral",
    "warn": "warn",
    "warning": "warn",
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
    return cls(**{key: value for key, value in data.items() if key in allowed})


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _key(value: object, default: str = "item") -> str:
    raw = str(value or default or "").strip().lower().replace("_", "-")
    safe = "".join(char for char in raw if char.isalnum() or char == "-")
    return safe or default


def _attrs(**attrs: object) -> str:
    parts: list[str] = []
    for name, value in attrs.items():
        if value not in (None, False, ""):
            parts.append(f' {name.replace("_", "-")}="{escape(str(value), quote=True)}"')
    return "".join(parts)


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
    return f'<span class="pc-presence-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-presence-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], features: Mapping[str, bool] | None) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label or (action.feature and not feature_enabled(features, action.feature, default=True)):
        return ""
    method = str(action.method or "").strip().upper()
    cls = f"pc-presence-action pc-dashboard-tone-{_tone(action.tone)}"
    body = escape(str(action.label))
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{_attrs(title=action.title)}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(str(action.href), quote=True)}"{_attrs(data_method=method) if method else ""}{_attrs(title=action.title)}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], features: Mapping[str, bool] | None) -> str:
    body = "".join(_action_html(action, features) for action in actions)
    return f'<div class="pc-presence-actions">{body}</div>' if body else ""


def presence_monitor_feature_enabled(
    config: PresenceMonitorSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, PresenceMonitorSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or PRESENCE_MONITOR_FEATURE), default=True)


def _status_html(status: object, tone: object = "") -> str:
    if not status:
        return ""
    return f'<span class="pc-surface-status pc-dashboard-tone-{_tone(tone or status)}">{escape(str(status))}</span>'


def _metric_html(raw_metric: DashboardMetric | Mapping[str, object]) -> str:
    metric = _coerce(raw_metric, DashboardMetric, {"label": "Metric", "value": ""})
    body = (
        f'<span>{escape(str(metric.label))}</span>'
        f'<strong>{escape(str(metric.value))}</strong>'
        f'<small>{escape(str(metric.detail))}</small>'
    )
    cls = f"pc-presence-metric pc-dashboard-tone-{_tone(metric.tone)}"
    if metric.href:
        return f'<a class="{cls}" href="{escape(str(metric.href), quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _facts_html(pairs: Sequence[tuple[str, object]]) -> str:
    parts = [
        f'<span><b>{escape(label)}</b>{escape(str(value))}</span>'
        for label, value in pairs
        if value not in ("", None)
    ]
    return f'<div class="pc-presence-facts">{"".join(parts)}</div>' if parts else ""


def _state_card_html(
    raw_card: PresenceStateCard | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    card = _coerce(raw_card, PresenceStateCard, {"key": "state", "label": "Presence"})
    detail = _private_text(card.detail, privacy_scope=card.privacy_scope, safe_alternate=card.safe_alternate, policy=policy, context=context)
    href = _raw_href(card.href, privacy_scope=card.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=card.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-presence-card-head">'
        f'<strong>{escape(str(card.label))}</strong>{_status_html(card.status, card.tone)}</div>'
        + _facts_html((("Mode", card.mode), ("Channel", card.channel), ("Last seen", card.last_seen), ("Next change", card.next_change)))
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(card.badges)
        + _actions_html(card.actions, features)
    )
    cls = f"pc-presence-card pc-dashboard-tone-{_tone(card.tone or card.status)}{private}"
    if href and not card.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _row_common(
    *,
    key: str,
    label: object,
    status: object,
    tone: object,
    facts: Sequence[tuple[str, object]],
    body_text: object,
    href: str,
    privacy_scope: str,
    safe_alternate: str,
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str],
    actions: Sequence[SurfaceAction | Mapping[str, object]],
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    detail = _private_text(body_text, privacy_scope=privacy_scope, safe_alternate=safe_alternate, policy=policy, context=context)
    raw_href = _raw_href(href, privacy_scope=privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=privacy_scope, policy=policy, context=context)
    content = (
        '<div class="pc-presence-row-main">'
        '<div class="pc-presence-row-title">'
        f'<strong>{escape(str(label))}</strong>{_status_html(status, tone)}</div>'
        + _facts_html(facts)
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(badges)
        + "</div>"
        + _actions_html(actions, features)
    )
    cls = f"pc-presence-row pc-dashboard-tone-{_tone(tone or status)}{private}"
    if raw_href and not actions:
        return f'<a class="{cls}" href="{escape(raw_href, quote=True)}" data-presence-row="{escape(key, quote=True)}">{content}</a>'
    return f'<article class="{cls}" data-presence-row="{escape(key, quote=True)}">{content}</article>'


def _channel_html(
    raw_row: PresenceChannelRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, PresenceChannelRow, {"key": "channel", "label": "Channel"})
    return _row_common(
        key=_key(row.key),
        label=row.label,
        status=row.status,
        tone=row.tone,
        facts=(("Channel", row.channel), ("Mode", row.mode), ("Audience", row.audience), ("Last seen", row.last_seen), ("Freshness", row.freshness)),
        body_text=row.detail,
        href=row.href,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        badges=row.badges,
        actions=row.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _schedule_html(
    raw_row: PresenceScheduleWindow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, PresenceScheduleWindow, {"key": "schedule", "label": "Schedule"})
    text = row.detail or row.policy
    return _row_common(
        key=_key(row.key),
        label=row.label,
        status=row.status,
        tone=row.tone,
        facts=(("Start", row.starts_at), ("End", row.ends_at), ("Zone", row.timezone), ("Repeat", row.repeat), ("Channel", row.channel)),
        body_text=text,
        href=row.href,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        badges=row.badges,
        actions=row.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _source_html(
    raw_row: PresenceSourceFreshnessRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, PresenceSourceFreshnessRow, {"key": "source", "label": "Source"})
    return _row_common(
        key=_key(row.key),
        label=row.label,
        status=row.status,
        tone=row.tone,
        facts=(("Source", row.source), ("Last seen", row.last_seen), ("Lag", row.lag), ("Target", row.target)),
        body_text=row.detail,
        href=row.href,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        badges=row.badges,
        actions=row.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _policy_html(
    raw_row: PresencePolicyNotice | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, PresencePolicyNotice, {"key": "policy", "label": "Policy"})
    text = row.detail or row.summary
    return _row_common(
        key=_key(row.key),
        label=row.label,
        status=row.status,
        tone=row.tone,
        facts=(),
        body_text=text,
        href=row.href,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        badges=row.badges,
        actions=row.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _transition_html(
    raw_row: PresenceTransitionRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, PresenceTransitionRow, {"key": "transition", "label": "Transition"})
    return _row_common(
        key=_key(row.key),
        label=row.label,
        status=row.status,
        tone=row.tone,
        facts=(("From", row.from_state), ("To", row.to_state), ("Actor", row.actor), ("Time", row.timestamp)),
        body_text=row.summary,
        href=row.href,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        badges=row.badges,
        actions=row.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _section_html(title: str, body: str, *, subtitle: str = "", class_name: str = "") -> str:
    if not body:
        return ""
    return (
        f'<section class="pc-presence-section {escape(class_name, quote=True)}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(subtitle)}</div>'
        f"</div></div>{body}</section>"
    )


def render_presence_monitor_surface(
    config: PresenceMonitorSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, PresenceMonitorSurfaceConfig)
    if not presence_monitor_feature_enabled(model, features):
        return ""
    tabs = render_status_tabs(model.tabs) if model.tabs else ""
    metrics = "".join(_metric_html(metric) for metric in model.metrics)
    metrics_html = f'<div class="pc-presence-metrics">{metrics}</div>' if metrics else ""
    states = "".join(_state_card_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.states)
    state_html = f'<div class="pc-presence-card-grid">{states}</div>' if states else ""
    channels = "".join(_channel_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.channels)
    schedule = "".join(_schedule_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.schedule)
    sources = "".join(_source_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.sources)
    policies = "".join(_policy_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.policies)
    transitions = "".join(_transition_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.transitions)
    actions = _actions_html(model.actions, features)
    live = render_live_controls(model.live_refresh) if model.live_refresh else ""
    has_content = any((tabs, metrics_html, state_html, channels, schedule, sources, policies, transitions, actions, live))
    body = (
        tabs
        + metrics_html
        + state_html
        + live
        + _section_html("Channels", channels, subtitle="Current channel posture and freshness")
        + _section_html("Schedule", schedule, subtitle="Upcoming runtime-owned windows")
        + _section_html("Sources", sources, subtitle="Adapter freshness and stale checks")
        + _section_html("Policy Notes", policies, subtitle="Sanitized operator-facing policy posture")
        + _section_html("Recent Transitions", transitions, subtitle="Sanitized state changes")
        + actions
        if has_content
        else f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    )
    return (
        f'<section id="{escape(_key(model.key, "presence-monitor"), quote=True)}" class="pc-presence-monitor-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div>{_status_html(model.status, model.status_tone)}</div>'
        f"{body}</section>"
    )


__all__ = [
    "PRESENCE_MONITOR_FEATURE",
    "presence_monitor_feature_enabled",
    "render_presence_monitor_surface",
]
