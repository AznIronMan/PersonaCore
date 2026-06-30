from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    AdapterHealthConfig,
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
    DashboardMetricSpec,
    DashboardQueueRow,
    DashboardRouteCard,
)
from .adapter_health import render_adapter_health_panel
from .token_health import render_token_health_panel

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "danger": "bad",
    "error": "bad",
    "red": "bad",
    "rose": "bad",
    "warn": "warn",
    "warning": "warn",
    "amber": "warn",
    "yellow": "warn",
    "good": "good",
    "green": "good",
    "ok": "good",
    "success": "good",
    "info": "info",
    "blue": "info",
    "cyan": "info",
    "neutral": "neutral",
    "slate": "neutral",
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


def _human_count(value: object) -> str:
    try:
        number = int(value or 0)
    except (TypeError, ValueError):
        return str(value or "0")
    sign = "-" if number < 0 else ""
    absolute = abs(number)
    if absolute >= 1_000_000:
        formatted = f"{absolute / 1_000_000:.1f}".rstrip("0").rstrip(".")
        return f"{sign}{formatted}m"
    if absolute >= 1_000:
        formatted = f"{absolute / 1_000:.1f}".rstrip("0").rstrip(".")
        return f"{sign}{formatted}k"
    return f"{number}"


def _clip(value: object, max_length: int) -> str:
    text = str(value if value is not None else "")
    clean_length = max(1, int(max_length or 1))
    if len(text) <= clean_length:
        return text
    if clean_length <= 3:
        return "." * clean_length
    return text[: clean_length - 3].rstrip() + "..."


def format_dashboard_metric_value(
    value: object,
    *,
    value_kind: str = "auto",
    max_length: int = 24,
) -> str:
    """Return a compact value for dashboard metric cards."""

    kind = str(value_kind or "auto").strip().lower()
    if kind == "count":
        return _human_count(value)
    if kind == "text":
        return _clip(value or "-", max_length)
    if kind == "raw":
        return str(value if value is not None else "")
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return _human_count(value)
    return _clip(value or "-", max_length)


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


def render_dashboard_filters(filters: Sequence[DashboardFilter | Mapping[str, object]]) -> str:
    chips: list[str] = []
    for raw_filter in filters:
        item = _coerce(raw_filter, DashboardFilter)
        active = " is-active" if item.active else ""
        swatch = ""
        if item.color:
            swatch = (
                '<span class="pc-dashboard-filter-swatch" aria-hidden="true" '
                f'style="background: {escape(item.color, quote=True)}"></span>'
            )
        chips.append(
            f'<a class="pc-dashboard-filter{active}" href="{escape(item.href or "#", quote=True)}">'
            f"{swatch}<span>{escape(str(item.label))}</span></a>"
        )
    if not chips:
        return ""
    return '<div class="pc-dashboard-filters" aria-label="Dashboard filters">' + "".join(chips) + "</div>"


def render_dashboard_attention(
    attention: DashboardAttention | Mapping[str, object] | None,
    *,
    filters: Sequence[DashboardFilter | Mapping[str, object]] = (),
) -> str:
    model = _coerce(attention or {}, DashboardAttention)
    tone = _tone(model.tone)
    refreshed = f" · {escape(str(model.refreshed_label))}" if model.refreshed_label else ""
    count = (
        f'<span class="pc-dashboard-attention-count">{int(model.count)}</span>'
        if int(model.count or 0) > 0
        else ""
    )
    items = [_coerce(item, DashboardAttentionItem) for item in model.items]
    item_html: list[str] = []
    for item in items:
        item_tone = _tone(item.tone)
        actions = "".join(
            f'<a class="pc-dashboard-action pc-dashboard-tone-{_tone(action.tone)}" '
            f'href="{escape(action.href, quote=True)}">{escape(action.label)}</a>'
            for action in (_coerce(raw_action, DashboardAction) for raw_action in item.actions)
            if action.href and action.label
        )
        body = (
            '<div class="pc-dashboard-attention-top">'
            f"<span>{escape(str(item.label))}</span><strong>{escape(str(item.metric))}</strong></div>"
            f'<div class="pc-dashboard-attention-summary">{escape(str(item.summary))}</div>'
            + (f'<div class="pc-dashboard-attention-detail">{escape(str(item.detail))}</div>' if item.detail else "")
            + (f'<div class="pc-dashboard-actions">{actions}</div>' if actions else "")
        )
        item_html.append(
            _link_or_tag(
                "article",
                item.href,
                f"pc-dashboard-attention-card pc-dashboard-tone-{item_tone}",
                body,
            )
        )
    if not item_html:
        item_html.append(
            '<div class="pc-dashboard-clear">'
            "<div>"
            f'<div class="pc-dashboard-clear-title">{escape(str(model.clear_title))}</div>'
            f'<div class="pc-dashboard-clear-copy">{escape(str(model.clear_summary))}</div>'
            "</div>"
            '<span class="pc-dashboard-tag pc-dashboard-tone-good">clear</span>'
            "</div>"
        )
    return (
        '<section class="pc-dashboard-overview">'
        '<div class="pc-dashboard-overview-head"><div class="pc-dashboard-title-group">'
        f"<h2>{escape(str(model.title))}</h2>"
        f"<p>{escape(str(model.subtitle))}{refreshed}</p>"
        "</div>"
        f'<div class="pc-dashboard-status pc-dashboard-tone-{tone}">'
        '<span class="pc-dashboard-status-dot" aria-hidden="true"></span>'
        f"<span>{escape(str(model.label))}</span>{count}</div></div>"
        f"{render_dashboard_filters(filters)}"
        '<div class="pc-dashboard-attention-grid">'
        + "".join(item_html)
        + "</div></section>"
    )


def render_dashboard_metrics(metrics: Sequence[DashboardMetric | Mapping[str, object]]) -> str:
    cards: list[str] = []
    for raw_metric in metrics:
        item = _coerce(raw_metric, DashboardMetric)
        body = (
            f'<div class="pc-dashboard-stat-label">{escape(str(item.label))}</div>'
            f'<div class="pc-dashboard-stat-value">{escape(str(item.value))}</div>'
            + (f'<div class="pc-dashboard-stat-detail">{escape(str(item.detail))}</div>' if item.detail else "")
        )
        cards.append(_link_or_tag("article", item.href, f"pc-dashboard-stat pc-dashboard-tone-{_tone(item.tone)}", body))
    if not cards:
        return ""
    return '<section class="pc-dashboard-stat-grid">' + "".join(cards) + "</section>"


def dashboard_metrics_from_counts(
    counts: Mapping[str, object],
    specs: Sequence[DashboardMetricSpec | Mapping[str, object]],
) -> list[DashboardMetric]:
    """Build dashboard metrics from a consumer-owned count/status mapping."""

    metrics: list[DashboardMetric] = []
    for raw_spec in specs:
        spec = _coerce(raw_spec, DashboardMetricSpec)
        value = counts.get(spec.key, spec.default)
        metrics.append(
            DashboardMetric(
                spec.label,
                format_dashboard_metric_value(value, value_kind=spec.value_kind, max_length=spec.max_length),
                href=spec.href,
                detail=spec.detail,
                tone=spec.tone,
            )
        )
    return metrics


def render_dashboard_summary_grid(
    metrics: Sequence[DashboardMetric | Mapping[str, object]] | Mapping[str, object],
    specs: Sequence[DashboardMetricSpec | Mapping[str, object]] | None = None,
) -> str:
    """Render a metric summary grid from metric objects or count specs."""

    if specs is not None:
        if not isinstance(metrics, Mapping):
            raise TypeError("metrics must be a mapping when specs are provided")
        return render_dashboard_metrics(dashboard_metrics_from_counts(metrics, specs))
    if isinstance(metrics, Mapping):
        raise TypeError("specs are required when metrics is a mapping")
    return render_dashboard_metrics(metrics)


def render_dashboard_route_cards(routes: Sequence[DashboardRouteCard | Mapping[str, object]], *, title: str = "Operator work") -> str:
    cards: list[str] = []
    for raw_route in routes:
        item = _coerce(raw_route, DashboardRouteCard)
        body = (
            '<div class="pc-dashboard-route-top">'
            f"<strong>{escape(str(item.label))}</strong>"
            + (f"<span>{escape(str(item.metric))}</span>" if item.metric != "" else "")
            + "</div>"
            + (f'<div class="pc-dashboard-route-summary">{escape(str(item.summary))}</div>' if item.summary else "")
            + (f'<div class="pc-dashboard-attention-detail">{escape(str(item.detail))}</div>' if item.detail else "")
        )
        cards.append(
            _link_or_tag(
                "article",
                item.href,
                f"pc-dashboard-route pc-dashboard-tone-{_tone(item.tone)}",
                body,
            )
        )
    if not cards:
        return ""
    return (
        '<section class="pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        '<div class="pc-dashboard-section-meta">Frequent operator destinations</div>'
        "</div></div>"
        '<div class="pc-dashboard-route-grid">'
        + "".join(cards)
        + "</div></section>"
    )


def render_dashboard_health_strip(health: DashboardHealthStrip | Mapping[str, object] | None) -> str:
    if not health:
        return ""
    model = _coerce(health, DashboardHealthStrip)
    metrics = [_coerce(metric, DashboardHealthMetric) for metric in model.metrics]
    metric_html = "".join(
        '<div class="pc-dashboard-health-chip pc-dashboard-tone-'
        + _tone(metric.tone)
        + '">'
        + f"<span>{escape(str(metric.label))}</span><strong>{escape(str(metric.value))}</strong>"
        + (f"<em>{escape(str(metric.detail))}</em>" if metric.detail else "")
        + "</div>"
        for metric in metrics
    )
    body = (
        '<div class="pc-dashboard-health-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.label))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.meta))}</div>'
        "</div>"
        f'<span class="pc-dashboard-tag pc-dashboard-tone-{_tone(model.tone)}">{escape(_tone(model.tone))}</span>'
        "</div>"
        + (f'<div class="pc-dashboard-health-grid">{metric_html}</div>' if metric_html else "")
    )
    return _link_or_tag("section", model.href, f"pc-dashboard-health pc-dashboard-tone-{_tone(model.tone)}", body)


def render_dashboard_adapter_cards(adapters: Sequence[DashboardAdapterCard | Mapping[str, object]]) -> str:
    if not adapters:
        return ""
    return render_adapter_health_panel(AdapterHealthConfig(enabled=True, cards=adapters))


def render_dashboard_flow(flow: DashboardFlow | Mapping[str, object] | None) -> str:
    if not flow:
        return ""
    model = _coerce(flow, DashboardFlow)
    buckets = [_coerce(bucket, DashboardFlowBucket) for bucket in model.buckets]
    if not buckets:
        return ""
    bucket_html = []
    for bucket in buckets:
        segments = "".join(
            f'<span class="pc-dashboard-flow-segment pc-dashboard-tone-{_tone(segment.tone)}" '
            f'style="width: {_percent(segment.percent)}%"></span>'
            for segment in (_coerce(raw_segment, DashboardFlowSegment) for raw_segment in bucket.segments)
        )
        body = (
            (f'<span class="pc-dashboard-flow-segments">{segments}</span>' if segments else "")
            + f'<span class="pc-dashboard-flow-bar pc-dashboard-flow-in" style="height: {_percent(bucket.inbound_percent)}%"></span>'
            + f'<span class="pc-dashboard-flow-bar pc-dashboard-flow-out" style="height: {_percent(bucket.outbound_percent)}%"></span>'
        )
        bucket_html.append(
            _link_or_tag(
                "span",
                bucket.href,
                "pc-dashboard-flow-bucket",
                body,
                title=bucket.title or bucket.label,
            )
        )
    return (
        '<section class="pc-dashboard-visual">'
        '<div class="pc-dashboard-visual-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.meta))}</div>'
        "</div>"
        '<div class="pc-dashboard-flow-totals">'
        f"<span>{escape(str(model.inbound_total))} in</span>"
        f"<span>{escape(str(model.outbound_total))} out</span>"
        "</div></div>"
        '<div class="pc-dashboard-flow-bars">'
        + "".join(bucket_html)
        + "</div></section>"
    )


def render_dashboard_queue(rows: Sequence[DashboardQueueRow | Mapping[str, object]], *, title: str = "Queue summary") -> str:
    queue = [_coerce(row, DashboardQueueRow) for row in rows]
    if not queue:
        return ""
    total = sum(max(0, int(row.count or 0)) for row in queue)
    row_html = []
    for row in queue:
        row_total = row.total if row.total is not None else total
        pct = (int(row.count or 0) / row_total * 100) if row_total else 0
        body = (
            '<div class="pc-dashboard-queue-row-head">'
            f"<span>{escape(str(row.label))}</span><strong>{int(row.count or 0)}</strong></div>"
            '<div class="pc-dashboard-queue-track">'
            f'<span class="pc-dashboard-queue-fill pc-dashboard-tone-{_tone(row.tone)}" style="width: {_percent(pct)}%"></span>'
            "</div>"
        )
        row_html.append(_link_or_tag("div", row.href, "pc-dashboard-queue-row", body))
    return (
        '<section class="pc-dashboard-visual">'
        '<div class="pc-dashboard-visual-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        '<div class="pc-dashboard-section-meta">Current status by state</div>'
        "</div></div>"
        '<div class="pc-dashboard-queue-stack">'
        + "".join(row_html)
        + "</div></section>"
    )


def render_dashboard_activity(items: Sequence[DashboardActivityItem | Mapping[str, object]], *, title: str = "Activity timeline") -> str:
    rows = [_coerce(item, DashboardActivityItem) for item in items]
    if not rows:
        return (
            '<section class="pc-dashboard-panel">'
            f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
            '<div class="pc-dashboard-empty">No recent activity found.</div>'
            "</section>"
        )
    row_html = []
    for item in rows:
        body = (
            '<span class="pc-dashboard-activity-dot" aria-hidden="true"></span>'
            '<div class="pc-dashboard-activity-main">'
            '<div class="pc-dashboard-activity-title-row">'
            f'<span class="pc-dashboard-activity-label">{escape(str(item.label))}</span>'
            f"<strong>{escape(str(item.title))}</strong>"
            f"<time>{escape(str(item.timestamp))}</time></div>"
            + (f'<div class="pc-dashboard-activity-summary">{escape(str(item.summary))}</div>' if item.summary else "")
            + (f'<div class="pc-dashboard-activity-meta">{escape(str(item.meta))}</div>' if item.meta else "")
            + "</div>"
        )
        row_html.append(_link_or_tag("article", item.href, f"pc-dashboard-activity-item pc-dashboard-tone-{_tone(item.tone)}", body))
    return (
        '<section class="pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        f'<div class="pc-dashboard-section-meta">{len(rows)} shown</div>'
        "</div></div>"
        '<div class="pc-dashboard-activity-list">'
        + "".join(row_html)
        + "</div></section>"
    )


def render_dashboard_sections(data: DashboardData | Mapping[str, object]) -> str:
    model = _coerce(data, DashboardData)
    sections = [
        render_dashboard_attention(model.attention, filters=model.filters) if model.attention else "",
        render_dashboard_metrics(model.metrics),
        render_dashboard_route_cards(model.routes),
        render_dashboard_health_strip(model.health),
        render_token_health_panel(model.token_health, features=model.features),
        render_dashboard_adapter_cards(model.adapters),
        render_dashboard_flow(model.flow),
        render_dashboard_queue(model.queue),
        render_dashboard_activity(model.activity) if model.activity else "",
    ]
    return "\n".join(section for section in sections if section)
