from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import AdapterHealthConfig, DashboardAdapterCard, DashboardSparkBucket
from .privacy import feature_enabled

T = TypeVar("T")

ADAPTER_HEALTH_FEATURE = "adapter_health"

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "red": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
    "lagging": "warn",
    "amber": "warn",
    "yellow": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
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


def _percent(value: object) -> int:
    try:
        number = float(value or 0)
    except (TypeError, ValueError):
        return 0
    return int(max(0, min(100, round(number))))


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


def adapter_health_feature_enabled(
    config: AdapterHealthConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, AdapterHealthConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or ADAPTER_HEALTH_FEATURE),
        default=True,
    )


def _render_sparkline(buckets: Sequence[DashboardSparkBucket | Mapping[str, object]]) -> str:
    spans = []
    for raw_bucket in buckets:
        bucket = _coerce(raw_bucket, DashboardSparkBucket)
        attrs = _attrs(title=bucket.title or bucket.label)
        body = (
            f'<span class="pc-dashboard-spark pc-dashboard-tone-{_tone(bucket.tone)}" '
            f'style="height: {_percent(bucket.percent)}%"{attrs}></span>'
        )
        if bucket.href:
            body = f'<a href="{escape(bucket.href, quote=True)}" aria-label="{escape(bucket.label, quote=True)}">{body}</a>'
        spans.append(body)
    if not spans:
        return ""
    return '<div class="pc-dashboard-sparkline">' + "".join(spans) + "</div>"


def _card_html(raw_adapter: DashboardAdapterCard | Mapping[str, object]) -> str:
    adapter = _coerce(raw_adapter, DashboardAdapterCard)
    counts = []
    for raw_count in adapter.counts:
        if isinstance(raw_count, Mapping):
            label = str(raw_count.get("label") or "")
            tone = _tone(raw_count.get("tone"))
        else:
            label = str(raw_count)
            tone = "neutral"
        if label:
            counts.append(f'<span class="pc-dashboard-count pc-dashboard-tone-{tone}">{escape(label)}</span>')
    body = (
        '<div class="pc-dashboard-adapter-title-row">'
        f'<strong>{escape(str(adapter.label))}</strong>'
        f'<span class="pc-dashboard-adapter-status">{escape(str(adapter.status))}</span></div>'
        + (f'<div class="pc-dashboard-section-meta">{escape(str(adapter.route))}</div>' if adapter.route else "")
        + (f'<div class="pc-dashboard-adapter-policy">{escape(str(adapter.policy))}</div>' if adapter.policy else "")
        + '<div class="pc-dashboard-adapter-times">'
        f"<div><span>In</span><strong>{escape(str(adapter.last_in or 'never'))}</strong></div>"
        f"<div><span>Out</span><strong>{escape(str(adapter.last_out or 'never'))}</strong></div>"
        "</div>"
        + (f'<div class="pc-dashboard-counts">{"".join(counts)}</div>' if counts else "")
        + _render_sparkline(adapter.sparkline)
        + (f'<div class="pc-dashboard-attention-detail">{escape(str(adapter.detail))}</div>' if adapter.detail else "")
        + (f'<div class="pc-dashboard-action-hint">{escape(str(adapter.action_hint))}</div>' if adapter.action_hint else "")
    )
    return _link_or_tag("article", adapter.href, f"pc-dashboard-adapter pc-dashboard-tone-{_tone(adapter.tone)}", body)


def _config_from_input(
    value: AdapterHealthConfig | Sequence[DashboardAdapterCard | Mapping[str, object]] | Mapping[str, object],
) -> AdapterHealthConfig:
    if isinstance(value, AdapterHealthConfig):
        return value
    if isinstance(value, Mapping):
        return _coerce(value, AdapterHealthConfig)
    return AdapterHealthConfig(enabled=True, cards=value)


def render_adapter_health_panel(
    config: AdapterHealthConfig | Sequence[DashboardAdapterCard | Mapping[str, object]] | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
) -> str:
    if config is None:
        return ""
    model = _config_from_input(config)
    if not adapter_health_feature_enabled(model, features):
        return ""
    cards = [_card_html(card) for card in model.cards]
    body = (
        '<div class="pc-dashboard-adapter-grid">' + "".join(cards) + "</div>"
        if cards
        else f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    )
    return (
        '<section id="adapter-health" class="pc-adapter-health pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        "</div></div>"
        f"{body}</section>"
    )
