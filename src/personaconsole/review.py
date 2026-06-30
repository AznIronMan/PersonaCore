from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    DashboardAction,
    DashboardFilter,
    DashboardMetric,
    ReviewAgendaItem,
    ReviewBoardRow,
    ReviewQueueCard,
    ReviewQueueSection,
    ReviewSurfaceConfig,
    SurfaceBadge,
)
from .privacy import (
    WITHHELD_PRIVATE_TEXT,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    can_view_raw_private,
    feature_enabled,
    privacy_render_mode,
    render_private_text,
)

REVIEW_FEATURE = "review"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "high": "bad",
    "red": "bad",
    "rose": "bad",
    "warn": "warn",
    "warning": "warn",
    "medium": "warn",
    "pending": "warn",
    "review": "warn",
    "amber": "warn",
    "yellow": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "green": "good",
    "info": "info",
    "blue": "info",
    "cyan": "info",
    "neutral": "neutral",
    "low": "neutral",
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


def review_surface_feature_enabled(
    config: ReviewSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, ReviewSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or REVIEW_FEATURE),
        default=True,
    )


def render_review_surface(
    config: ReviewSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, ReviewSurfaceConfig)
    if not review_surface_feature_enabled(model, features):
        return ""

    rows = [_coerce(row, ReviewBoardRow) for row in model.rows]
    row_html = "".join(_row_html(row, policy=privacy_policy, context=privacy_context) for row in rows)
    if not row_html:
        row_html = (
            '<tr><td colspan="8" class="pc-review-empty">'
            f"{escape(str(model.empty_label or 'No decision rows found.'))}</td></tr>"
        )
    agenda = _agenda_html(model.agenda, model.agenda_title, model.agenda_subtitle)
    queues = _queue_sections_html(
        [_coerce(section, ReviewQueueSection) for section in model.queue_sections],
        policy=privacy_policy,
        context=privacy_context,
    )
    controls = _controls_html(model.filters, model.actions)
    metrics = _metrics_html(model.metrics)
    return f"""
<section id="review" class="pc-dashboard-panel pc-review-surface">
  {_panel_head(model.title, model.subtitle)}
  {controls}
  {metrics}
  <section class="pc-review-board" id="decision-board">
    <div class="pc-dashboard-panel-head">
      <div>
        <div class="pc-dashboard-section-title">{escape(str(model.board_title or "Decision Board"))}</div>
        <div class="pc-dashboard-section-meta">{escape(str(model.board_subtitle or ""))}</div>
      </div>
      <span class="pc-dashboard-status"><span class="pc-dashboard-status-dot"></span>{len(rows)} rows</span>
    </div>
    <div class="pc-review-table-wrap">
      <table class="pc-review-table">
        <thead>
          <tr>
            <th>Open</th>
            <th>Age</th>
            <th>Kind</th>
            <th>Status</th>
            <th>Risk</th>
            <th>Entity</th>
            <th>Actor</th>
            <th>Summary</th>
          </tr>
        </thead>
        <tbody>{row_html}</tbody>
      </table>
    </div>
  </section>
  {agenda}
  {queues}
</section>
"""


def _panel_head(title: str, subtitle: str) -> str:
    return (
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(title or "Review"))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(subtitle or ""))}</div>'
        "</div></div>"
    )


def _controls_html(
    filters: Sequence[DashboardFilter | Mapping[str, object]],
    actions: Sequence[DashboardAction | Mapping[str, object]],
) -> str:
    filter_html = []
    for raw_filter in filters:
        item = _coerce(raw_filter, DashboardFilter)
        if not item.label:
            continue
        active = " is-active" if item.active else ""
        key = f"<small>{escape(str(item.key))}</small>" if item.key else ""
        filter_html.append(
            f'<a class="pc-review-filter{active}" href="{escape(str(item.href or "#"), quote=True)}">'
            f'<span>{escape(str(item.label))}</span>{key}</a>'
        )
    action_html = []
    for raw_action in actions:
        item = _coerce(raw_action, DashboardAction)
        if not item.label or not item.href:
            continue
        action_html.append(
            f'<a class="pc-review-action pc-dashboard-tone-{_tone(item.tone)}" '
            f'href="{escape(str(item.href), quote=True)}">{escape(str(item.label))}</a>'
        )
    if not filter_html and not action_html:
        return ""
    return '<div class="pc-review-controls">' + "".join(filter_html) + "".join(action_html) + "</div>"


def _metrics_html(metrics: Sequence[DashboardMetric | Mapping[str, object]]) -> str:
    cards = []
    for raw_metric in metrics:
        item = _coerce(raw_metric, DashboardMetric)
        if not item.label:
            continue
        body = (
            f'<span>{escape(str(item.label))}</span>'
            f'<strong>{escape(str(item.value))}</strong>'
            + (f'<em>{escape(str(item.detail))}</em>' if item.detail else "")
        )
        tag = "a" if item.href else "div"
        href = f' href="{escape(str(item.href), quote=True)}"' if item.href else ""
        cards.append(f'<{tag} class="pc-review-metric pc-dashboard-tone-{_tone(item.tone)}"{href}>{body}</{tag}>')
    if not cards:
        return ""
    return '<div class="pc-review-metrics">' + "".join(cards) + "</div>"


def _row_html(
    row: ReviewBoardRow,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    summary = _private_text(
        row.summary,
        privacy_scope=row.summary_privacy_scope,
        safe_alternate=row.summary_safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(row.href, privacy_scope=row.summary_privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.summary_privacy_scope, policy=policy, context=context)
    open_cell = (
        f'<a class="pc-review-open" href="{escape(href, quote=True)}">{escape(str(row.open_label or "Open"))}</a>'
        if href
        else f'<span class="pc-review-muted">{escape(str(row.open_label or "Open"))}</span>'
    )
    return f"""
        <tr class="pc-dashboard-tone-{_tone(row.risk)}{private}">
          <td>{open_cell}</td>
          <td class="pc-review-nowrap">{escape(str(row.age))}</td>
          <td>{_pill(row.kind, row.risk)}</td>
          <td>{_pill(row.status, row.status)}</td>
          <td>{_pill(row.risk, row.risk)}</td>
          <td class="pc-review-entity">{escape(str(row.entity))}{_badges_html(row.badges)}</td>
          <td>{escape(str(row.actor))}</td>
          <td class="pc-review-summary">{escape(summary)}</td>
        </tr>
"""


def _agenda_html(
    agenda: Sequence[ReviewAgendaItem | Mapping[str, object]],
    title: str,
    subtitle: str,
) -> str:
    cards = []
    for raw_item in agenda:
        item = _coerce(raw_item, ReviewAgendaItem)
        if not item.label:
            continue
        body = (
            '<div class="pc-review-card-head">'
            f'<strong>{escape(str(item.label))}</strong>'
            f'<span>{escape(str(item.category))}</span></div>'
            f'<div class="pc-review-card-value">{escape(str(item.value))}</div>'
            + (f'<p>{escape(str(item.summary))}</p>' if item.summary else "")
        )
        tag = "a" if item.href else "article"
        href = f' href="{escape(str(item.href), quote=True)}"' if item.href else ""
        cards.append(f'<{tag} class="pc-review-card pc-dashboard-tone-{_tone(item.tone)}"{href}>{body}</{tag}>')
    if not cards:
        return ""
    return (
        '<section class="pc-review-agenda">'
        f"{_panel_head(title or 'Review Agenda', subtitle or 'Direct routes')}"
        '<div class="pc-review-card-grid">'
        + "".join(cards)
        + "</div></section>"
    )


def _queue_sections_html(
    sections: Sequence[ReviewQueueSection],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    rendered = []
    for section in sections:
        cards = [
            _queue_card_html(_coerce(card, ReviewQueueCard), policy=policy, context=context)
            for card in section.cards
        ]
        body = "".join(cards) if cards else f'<div class="pc-dashboard-empty">{escape(str(section.empty_label))}</div>'
        rendered.append(
            '<section class="pc-review-queue-section">'
            f"{_panel_head(section.title, section.subtitle)}"
            f'<div class="pc-review-queue-grid">{body}</div></section>'
        )
    if not rendered:
        return ""
    return '<div class="pc-review-queues">' + "".join(rendered) + "</div>"


def _queue_card_html(
    card: ReviewQueueCard,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    summary = _private_text(
        card.summary,
        privacy_scope=card.summary_privacy_scope,
        safe_alternate=card.summary_safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(card.href, privacy_scope=card.summary_privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=card.summary_privacy_scope, policy=policy, context=context)
    title = (
        f'<a href="{escape(href, quote=True)}">{escape(str(card.label))}</a>'
        if href
        else f"<strong>{escape(str(card.label))}</strong>"
    )
    meta = "".join(_meta_pair_html(pair) for pair in card.meta)
    return (
        f'<article class="pc-review-queue-card pc-dashboard-tone-{_tone(card.tone or card.status)}{private}">'
        '<div class="pc-review-card-head">'
        f"{title}<span>{escape(str(card.category))}</span></div>"
        f'<div class="pc-review-card-status">{escape(str(card.status))}</div>'
        + (f'<p>{escape(summary)}</p>' if summary else "")
        + (f'<dl>{meta}</dl>' if meta else "")
        + _badges_html(card.badges)
        + "</article>"
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
    return " is-private" if str(mode.value) != "raw" else ""


def _pill(label: object, tone: object) -> str:
    if not str(label or "").strip():
        return '<span class="pc-review-muted">&mdash;</span>'
    return f'<span class="pc-review-pill pc-dashboard-tone-{_tone(tone)}">{escape(str(label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = []
    for raw_badge in badges:
        badge = SurfaceBadge(str(raw_badge)) if isinstance(raw_badge, str) else _coerce(raw_badge, SurfaceBadge)
        if badge.label:
            body.append(f'<span class="pc-review-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>')
    return f'<span class="pc-review-badges">{"".join(body)}</span>' if body else ""


def _meta_pair_html(pair: tuple[str, str] | Mapping[str, object]) -> str:
    if isinstance(pair, Mapping):
        label = str(pair.get("label") or pair.get("key") or "")
        value = str(pair.get("value") or "")
    else:
        try:
            label, value = pair
        except Exception:
            return ""
    if not label and not value:
        return ""
    return f"<div><dt>{escape(str(label))}</dt><dd>{escape(str(value))}</dd></div>"
