from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    DashboardMetric,
    InfrastructureActionSlot,
    InfrastructureCertificateRow,
    InfrastructureCheckRow,
    InfrastructureDnsRecordRow,
    InfrastructureEndpointRow,
    InfrastructurePostureSurfaceConfig,
    InfrastructureWarningRow,
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

INFRASTRUCTURE_POSTURE_FEATURE = "infrastructure_posture"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "expired": "bad",
    "failed": "bad",
    "invalid": "bad",
    "missing": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
    "expiring": "warn",
    "pending": "warn",
    "propagating": "warn",
    "stale": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "valid": "good",
    "verified": "good",
    "info": "info",
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
    return f'<span class="pc-infra-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-infra-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], features: Mapping[str, bool] | None) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label or (action.feature and not feature_enabled(features, action.feature, default=True)):
        return ""
    method = str(action.method or "").strip().upper()
    cls = f"pc-infra-action pc-dashboard-tone-{_tone(action.tone)}"
    body = escape(str(action.label))
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{_attrs(title=action.title)}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(str(action.href), quote=True)}"{_attrs(data_method=method) if method else ""}{_attrs(title=action.title)}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], features: Mapping[str, bool] | None) -> str:
    body = "".join(_action_html(action, features) for action in actions)
    return f'<div class="pc-infra-actions">{body}</div>' if body else ""


def infrastructure_posture_feature_enabled(
    config: InfrastructurePostureSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, InfrastructurePostureSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or INFRASTRUCTURE_POSTURE_FEATURE), default=True)


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
    cls = f"pc-infra-metric pc-dashboard-tone-{_tone(metric.tone)}"
    return f'<a class="{cls}" href="{escape(str(metric.href), quote=True)}">{body}</a>' if metric.href else f'<article class="{cls}">{body}</article>'


def _facts_html(pairs: Sequence[tuple[str, object]]) -> str:
    parts = [
        f'<span><b>{escape(label)}</b>{escape(str(value))}</span>'
        for label, value in pairs
        if value not in ("", None)
    ]
    return f'<div class="pc-infra-facts">{"".join(parts)}</div>' if parts else ""


def _row_html(
    *,
    key: str,
    label: object,
    status: object,
    tone: object,
    facts: Sequence[tuple[str, object]],
    detail: object,
    href: str,
    privacy_scope: str,
    safe_alternate: str,
    badges: Sequence[SurfaceBadge | Mapping[str, object] | str],
    actions: Sequence[SurfaceAction | Mapping[str, object]],
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    text = _private_text(detail, privacy_scope=privacy_scope, safe_alternate=safe_alternate, policy=policy, context=context)
    safe_href = _raw_href(href, privacy_scope=privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=privacy_scope, policy=policy, context=context)
    facts_html = "" if private else _facts_html(facts)
    body = (
        '<div class="pc-infra-row-main">'
        '<div class="pc-infra-row-title">'
        f'<strong>{escape(str(label))}</strong>{_status_html(status, tone)}</div>'
        + facts_html
        + (f'<p>{escape(text)}</p>' if text else "")
        + _badges_html(badges)
        + "</div>"
        + _actions_html(actions, features)
    )
    cls = f"pc-infra-row pc-dashboard-tone-{_tone(tone or status)}{private}"
    if safe_href and not actions:
        return f'<a class="{cls}" href="{escape(safe_href, quote=True)}" data-infra-row="{escape(key, quote=True)}">{body}</a>'
    return f'<article class="{cls}" data-infra-row="{escape(key, quote=True)}">{body}</article>'


def _dns_html(row: InfrastructureDnsRecordRow | Mapping[str, object], *, features: Mapping[str, bool] | None, policy: OwnerPrivateScopePolicy | None, context: AdminPrivacyContext | Mapping[str, Any] | None) -> str:
    item = _coerce(row, InfrastructureDnsRecordRow, {"key": "dns", "label": "DNS record"})
    detail = item.detail or item.value
    return _row_html(
        key=_key(item.key),
        label=item.label,
        status=item.status,
        tone=item.tone,
        facts=(("Type", item.record_type), ("Name", item.name), ("Expected", item.expected_value), ("TTL", item.ttl), ("Provider", item.provider), ("Checked", item.last_checked)),
        detail=detail,
        href=item.href,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        badges=item.badges,
        actions=item.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _cert_html(row: InfrastructureCertificateRow | Mapping[str, object], *, features: Mapping[str, bool] | None, policy: OwnerPrivateScopePolicy | None, context: AdminPrivacyContext | Mapping[str, Any] | None) -> str:
    item = _coerce(row, InfrastructureCertificateRow, {"key": "cert", "label": "Certificate"})
    return _row_html(
        key=_key(item.key),
        label=item.label,
        status=item.status,
        tone=item.tone,
        facts=(("Subject", item.subject), ("Issuer", item.issuer), ("Expires", item.expires_at), ("Days", item.days_remaining), ("Renewal", item.renewal), ("Checked", item.last_checked)),
        detail=item.detail,
        href=item.href,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        badges=item.badges,
        actions=item.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _endpoint_html(row: InfrastructureEndpointRow | Mapping[str, object], *, features: Mapping[str, bool] | None, policy: OwnerPrivateScopePolicy | None, context: AdminPrivacyContext | Mapping[str, Any] | None) -> str:
    item = _coerce(row, InfrastructureEndpointRow, {"key": "endpoint", "label": "Endpoint"})
    detail = item.detail or item.url
    return _row_html(
        key=_key(item.key),
        label=item.label,
        status=item.status,
        tone=item.tone,
        facts=(("Method", item.method), ("Code", item.code), ("Latency", item.latency), ("Checked", item.last_checked)),
        detail=detail,
        href=item.href,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        badges=item.badges,
        actions=item.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _check_html(row: InfrastructureCheckRow | Mapping[str, object], *, features: Mapping[str, bool] | None, policy: OwnerPrivateScopePolicy | None, context: AdminPrivacyContext | Mapping[str, Any] | None) -> str:
    item = _coerce(row, InfrastructureCheckRow, {"key": "check", "label": "Check"})
    return _row_html(
        key=_key(item.key),
        label=item.label,
        status=item.status,
        tone=item.tone,
        facts=(("Source", item.source), ("Target", item.target), ("Observed", item.observed), ("Expected", item.expected), ("Checked", item.last_checked)),
        detail=item.detail,
        href=item.href,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        badges=item.badges,
        actions=item.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _warning_html(row: InfrastructureWarningRow | Mapping[str, object], *, features: Mapping[str, bool] | None, policy: OwnerPrivateScopePolicy | None, context: AdminPrivacyContext | Mapping[str, Any] | None) -> str:
    item = _coerce(row, InfrastructureWarningRow, {"key": "warning", "label": "Warning"})
    return _row_html(
        key=_key(item.key),
        label=item.label,
        status=item.status,
        tone=item.tone,
        facts=(("Severity", item.severity), ("Last seen", item.last_seen)),
        detail=item.summary,
        href=item.href,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        badges=item.badges,
        actions=item.actions,
        features=features,
        policy=policy,
        context=context,
    )


def _section_html(title: str, body: str, subtitle: str) -> str:
    if not body:
        return ""
    return (
        '<section class="pc-infra-section">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(subtitle)}</div>'
        f"</div></div>{body}</section>"
    )


def _slot_html(slots: Sequence[InfrastructureActionSlot | Mapping[str, object]], *, features: Mapping[str, bool] | None) -> str:
    body = ""
    for raw_slot in slots:
        slot = _coerce(raw_slot, InfrastructureActionSlot, {"key": "slot", "label": "Action"})
        body += (
            f'<section class="pc-infra-slot pc-dashboard-tone-{_tone(slot.tone)}" data-infra-slot="{escape(_key(slot.key), quote=True)}">'
            f'<h3>{escape(str(slot.label))}</h3><p>{escape(str(slot.description))}</p>'
            + (f'<div class="pc-infra-slot-body">{slot.body_html}</div>' if slot.body_html else "")
            + _actions_html(slot.actions, features)
            + "</section>"
        )
    return f'<div class="pc-infra-slots">{body}</div>' if body else ""


def render_infrastructure_posture_surface(
    config: InfrastructurePostureSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, InfrastructurePostureSurfaceConfig)
    if not infrastructure_posture_feature_enabled(model, features):
        return ""
    tabs = render_status_tabs(model.tabs, aria_label=f"{model.title} status") if model.tabs else ""
    metrics = "".join(_metric_html(metric) for metric in model.metrics)
    metrics_html = f'<div class="pc-infra-metrics">{metrics}</div>' if metrics else ""
    live = render_live_controls(model.live_refresh) if model.live_refresh else ""
    dns = "".join(_dns_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.dns_records)
    certs = "".join(_cert_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.certificates)
    endpoints = "".join(_endpoint_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.endpoints)
    checks = "".join(_check_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.checks)
    warnings = "".join(_warning_html(row, features=features, policy=privacy_policy, context=privacy_context) for row in model.warnings)
    slots = _slot_html(model.action_slots, features=features)
    actions = _actions_html(model.actions, features)
    has_content = any((tabs, metrics_html, live, dns, certs, endpoints, checks, warnings, slots, actions))
    body = (
        tabs
        + metrics_html
        + live
        + actions
        + _section_html("DNS Records", dns, "Sanitized expected and observed DNS posture")
        + _section_html("Certificates", certs, "Expiry, issuer, and renewal posture")
        + _section_html("Edge Endpoints", endpoints, "Public-safe edge check results")
        + _section_html("Propagation Checks", checks, "Recent provider-neutral diagnostics")
        + _section_html("Warnings", warnings, "Items requiring operator attention")
        + slots
        if has_content
        else f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    )
    return (
        f'<section id="{escape(_key(model.key, "infrastructure-posture"), quote=True)}" class="pc-infra-posture-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div>{_status_html(model.status, model.status_tone)}</div>'
        f"{body}</section>"
    )


__all__ = [
    "INFRASTRUCTURE_POSTURE_FEATURE",
    "infrastructure_posture_feature_enabled",
    "render_infrastructure_posture_surface",
]
