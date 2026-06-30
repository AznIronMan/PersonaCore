from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    AvailabilityEventRow,
    AvailabilityMonitorRow,
    AvailabilityMonitorSurfaceConfig,
    AvailabilityPolicyRow,
    AvailabilityScenarioRow,
    AvailabilityWindowRow,
    DashboardMetric,
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

AVAILABILITY_MONITOR_FEATURE = "availability_monitor"

T = TypeVar("T")

_TONE_ALIASES = {
    "active": "good",
    "bad": "bad",
    "blocked": "bad",
    "closed": "neutral",
    "danger": "bad",
    "degraded": "warn",
    "disabled": "neutral",
    "due": "warn",
    "error": "bad",
    "failed": "bad",
    "good": "good",
    "healthy": "good",
    "held": "warn",
    "info": "info",
    "missed": "bad",
    "neutral": "neutral",
    "ok": "good",
    "open": "good",
    "paused": "warn",
    "pending": "warn",
    "ready": "good",
    "review": "warn",
    "running": "info",
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
    data = {key: value for key, value in data.items() if key in allowed}
    return cls(**data)


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
    return f'<span class="pc-availability-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-availability-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], features: Mapping[str, bool] | None) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label or (action.feature and not feature_enabled(features, action.feature, default=True)):
        return ""
    body = escape(str(action.label))
    method = str(action.method or "").strip().upper()
    cls = f"pc-availability-action pc-dashboard-tone-{_tone(action.tone)}"
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{_attrs(title=action.title)}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(action.href, quote=True)}"{_attrs(data_method=method) if method else ""}{_attrs(title=action.title)}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], features: Mapping[str, bool] | None) -> str:
    body = "".join(_action_html(action, features) for action in actions)
    return f'<div class="pc-availability-actions">{body}</div>' if body else ""


def availability_monitor_feature_enabled(
    config: AvailabilityMonitorSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, AvailabilityMonitorSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or AVAILABILITY_MONITOR_FEATURE), default=True)


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
    cls = f"pc-availability-metric pc-dashboard-tone-{_tone(metric.tone)}"
    if metric.href:
        return f'<a class="{cls}" href="{escape(str(metric.href), quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _facts_html(pairs: Sequence[tuple[str, object]]) -> str:
    parts = [
        f'<span><b>{escape(label)}</b>{escape(str(value))}</span>'
        for label, value in pairs
        if value not in ("", None)
    ]
    return f'<div class="pc-availability-facts">{"".join(parts)}</div>' if parts else ""


def _window_html(
    raw_row: AvailabilityWindowRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, AvailabilityWindowRow, {"key": "window", "label": "Window"})
    summary = _private_text(row.summary, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
    detail = _private_text(row.detail, privacy_scope=row.privacy_scope, safe_alternate="", policy=policy, context=context)
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-availability-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}</div>'
        + _facts_html((("Start", row.starts_at), ("End", row.ends_at), ("Zone", row.timezone), ("Repeat", row.recurrence), ("Channel", row.channel)))
        + (f'<p>{escape(summary)}</p>' if summary else "")
        + (f'<small>{escape(detail)}</small>' if detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-availability-row pc-availability-window pc-dashboard-tone-{_tone(row.tone or row.status)}{private}"
    if href and not row.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _monitor_html(raw_row: AvailabilityMonitorRow | Mapping[str, object], *, features: Mapping[str, bool] | None) -> str:
    row = _coerce(raw_row, AvailabilityMonitorRow, {"key": "monitor", "label": "Monitor"})
    body = (
        '<div class="pc-availability-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}</div>'
        + _facts_html((("Value", row.value), ("Target", row.target), ("Last seen", row.last_seen), ("Next check", row.next_check)))
        + (f'<p>{escape(str(row.detail))}</p>' if row.detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-availability-row pc-availability-monitor-row pc-dashboard-tone-{_tone(row.tone or row.status)}"
    if row.href and not row.actions:
        return f'<a class="{cls}" href="{escape(row.href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _policy_html(raw_row: AvailabilityPolicyRow | Mapping[str, object], *, features: Mapping[str, bool] | None) -> str:
    row = _coerce(raw_row, AvailabilityPolicyRow, {"key": "policy", "label": "Policy"})
    body = (
        '<div class="pc-availability-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}</div>'
        + _facts_html((("Requirement", row.requirement),))
        + (f'<p>{escape(str(row.summary))}</p>' if row.summary else "")
        + (f'<small>{escape(str(row.detail))}</small>' if row.detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-availability-row pc-availability-policy-row pc-dashboard-tone-{_tone(row.tone or row.status)}"
    if row.href and not row.actions:
        return f'<a class="{cls}" href="{escape(row.href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _scenario_html(
    raw_row: AvailabilityScenarioRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, AvailabilityScenarioRow, {"key": "scenario", "label": "Scenario"})
    detail = _private_text(row.detail, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-availability-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}</div>'
        + _facts_html((("Step", row.current_step), ("Expected", row.expected_result), ("Last run", row.last_run), ("Next run", row.next_run)))
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-availability-row pc-availability-scenario-row pc-dashboard-tone-{_tone(row.tone or row.status)}{private}"
    if href and not row.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _event_html(
    raw_row: AvailabilityEventRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, AvailabilityEventRow, {"key": "event", "label": "Event"})
    detail = _private_text(row.detail, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-availability-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone or row.status)}</div>'
        + _facts_html((("When", row.timestamp), ("Source", row.source)))
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-availability-row pc-availability-event-row pc-dashboard-tone-{_tone(row.tone or row.status)}{private}"
    if href and not row.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _section_html(title: str, body: str, *, subtitle: str = "", empty: str = "") -> str:
    if not body and not empty:
        return ""
    content = body or f'<p class="pc-dashboard-empty">{escape(empty)}</p>'
    return (
        '<section class="pc-availability-section pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        + (f'<div class="pc-dashboard-section-meta">{escape(subtitle)}</div>' if subtitle else "")
        + f'</div></div><div class="pc-availability-list">{content}</div></section>'
    )


def render_availability_monitor_surface(
    config: AvailabilityMonitorSurfaceConfig | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    model = _coerce(config, AvailabilityMonitorSurfaceConfig)
    if not availability_monitor_feature_enabled(model, features):
        return ""

    key = _key(model.key, "availability-monitor")
    actions = _actions_html(model.actions, features)
    tabs = render_status_tabs(model.tabs) if model.tabs else ""
    metrics = "".join(_metric_html(metric) for metric in model.metrics)
    metrics_html = f'<div class="pc-availability-metrics">{metrics}</div>' if metrics else ""
    windows = "".join(_window_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.windows)
    monitors = "".join(_monitor_html(row, features=features) for row in model.monitors)
    policies = "".join(_policy_html(row, features=features) for row in model.policies)
    scenarios = "".join(_scenario_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.scenarios)
    events = "".join(_event_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.events)
    has_content = any((tabs, metrics_html, windows, monitors, policies, scenarios, events, actions))
    empty = "" if has_content else f'<p class="pc-dashboard-empty">{escape(str(model.empty_label))}</p>'

    return (
        f'<section id="{escape(key, quote=True)}" class="pc-availability-monitor-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title or "Availability Monitor"))}</div>'
        + (f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>' if model.subtitle else "")
        + f'</div>{actions}</div>{tabs}{metrics_html}{empty}'
        + _section_html("Schedule Windows", windows, subtitle="Consumer-owned availability windows")
        + _section_html("Live Monitors", monitors, subtitle="Read-only checks and queue posture")
        + _section_html("Policy Posture", policies, subtitle="Runtime-owned guardrails")
        + _section_html("Scenario QA", scenarios, subtitle="Scripted availability scenarios")
        + _section_html("Monitor Events", events, subtitle="Recent sanitized monitor events")
        + "</section>"
    )


__all__ = [
    "AVAILABILITY_MONITOR_FEATURE",
    "availability_monitor_feature_enabled",
    "render_availability_monitor_surface",
]
