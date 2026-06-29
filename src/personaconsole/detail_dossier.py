from __future__ import annotations

from dataclasses import asdict, fields as dataclass_fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    DetailDossierActionSlot,
    DetailDossierAuditRow,
    DetailDossierField,
    DetailDossierHeader,
    DetailDossierMetric,
    DetailDossierRelatedLink,
    DetailDossierSection,
    DetailDossierSourceTable,
    DetailDossierSurfaceConfig,
    DetailDossierTableCell,
    DetailDossierTableColumn,
    DetailDossierTableRow,
    DetailDossierTimelineEvent,
    SurfaceAction,
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

DETAIL_DOSSIER_FEATURE = "detail_dossier"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "high": "bad",
    "warn": "warn",
    "warning": "warn",
    "medium": "warn",
    "pending": "warn",
    "review": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "info": "info",
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


def _coerce(value: T | Mapping[str, object] | None, cls: type[T], defaults: Mapping[str, Any] | None = None) -> T:
    if isinstance(value, cls):
        return value
    data = {**(defaults or {}), **_mapping(value)}
    allowed = {field.name for field in dataclass_fields(cls)}
    data = {key: value for key, value in data.items() if key in allowed}
    return cls(**data)


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _align(value: object) -> str:
    clean = str(value or "").strip().lower()
    return clean if clean in {"left", "center", "right"} else "left"


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
    return "".join(parts)


def detail_dossier_surface_feature_enabled(
    config: DetailDossierSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, DetailDossierSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or DETAIL_DOSSIER_FEATURE),
        default=True,
    )


def render_detail_dossier_surface(
    config: DetailDossierSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, DetailDossierSurfaceConfig)
    if not detail_dossier_surface_feature_enabled(model, features):
        return ""

    header = _coerce(model.header, DetailDossierHeader)
    fields = _fields_html(model.fields, policy=privacy_policy, context=privacy_context, class_name="pc-detail-dossier-fields")
    metrics = _metrics_html(model.metrics)
    sections = _sections_html(model.sections, policy=privacy_policy, context=privacy_context)
    tables = _tables_html(model.source_tables, policy=privacy_policy, context=privacy_context)
    timeline = _timeline_html(model.timeline, policy=privacy_policy, context=privacy_context)
    related = _related_html(model.related_links)
    audit = _audit_html(model.audit_rows, policy=privacy_policy, context=privacy_context)
    action_slots = _action_slots_html(model.action_slots, policy=privacy_policy, context=privacy_context)
    body = fields + metrics + sections + tables + _side_panel_html(related, timeline, audit, action_slots)
    if not body.strip():
        body = f'<p class="pc-detail-dossier-empty">{escape(str(model.empty_label or "No detail data."))}</p>'
    section_id = str(model.key or "detail-dossier")
    return f"""
<section id="{escape(section_id, quote=True)}" class="pc-dashboard-panel pc-detail-dossier-surface" data-pc-detail-dossier>
  {_header_html(header, policy=privacy_policy, context=privacy_context)}
  {body}
</section>
"""


def _header_html(
    header: DetailDossierHeader,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    title = _private_text(header.title, privacy_scope=header.privacy_scope, safe_alternate=header.safe_alternate, policy=policy, context=context)
    subtitle = _private_text(header.subtitle, privacy_scope=header.privacy_scope, safe_alternate=header.safe_alternate, policy=policy, context=context)
    href = _raw_href(header.href, privacy_scope=header.privacy_scope, policy=policy, context=context)
    title_html = escape(str(title or "Detail"))
    if href:
        title_html = f'<a href="{escape(str(href), quote=True)}">{title_html}</a>'
    eyebrow = escape(str(header.eyebrow or header.entity_type or "Detail"))
    status = ""
    if header.status:
        status = f'<span class="pc-detail-dossier-status pc-dashboard-tone-{_tone(header.tone)}">{escape(str(header.status))}</span>'
    avatar = _avatar_html(header)
    badges = _badges_html(header.badges)
    actions = _actions_html(header.actions, class_name="pc-detail-dossier-action")
    action_html = f'<div class="pc-detail-dossier-actions">{actions}</div>' if actions else ""
    return f"""
  <div class="pc-detail-dossier-head pc-dashboard-panel-head">
    {avatar}
    <div class="pc-detail-dossier-title-group">
      <div class="pc-detail-dossier-eyebrow">{eyebrow}</div>
      <div class="pc-dashboard-section-title pc-detail-dossier-title">{title_html}</div>
      <div class="pc-dashboard-section-meta pc-detail-dossier-subtitle">{escape(str(subtitle or ""))}</div>
      {badges}
    </div>
    <div class="pc-detail-dossier-head-aside">{status}{action_html}</div>
  </div>
"""


def _avatar_html(header: DetailDossierHeader) -> str:
    alt = escape(str(header.avatar_alt or header.title or "Entity"), quote=True)
    if header.avatar_url:
        return f'<img class="pc-detail-dossier-avatar" src="{escape(str(header.avatar_url), quote=True)}" alt="{alt}">'
    initials = str(header.initials or "").strip()[:3].upper()
    if not initials:
        words = [part for part in str(header.title or "D").replace("_", " ").split() if part]
        initials = "".join(word[0] for word in words[:2]).upper() or "D"
    return f'<div class="pc-detail-dossier-avatar pc-detail-dossier-avatar-fallback" aria-hidden="true">{escape(initials)}</div>'


def _fields_html(
    fields: Sequence[DetailDossierField | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
    class_name: str,
) -> str:
    body = "".join(_field_html(field, policy=policy, context=context) for field in fields)
    return f'<dl class="{class_name}">{body}</dl>' if body else ""


def _field_html(
    raw_field: DetailDossierField | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    field = _coerce(raw_field, DetailDossierField)
    label = str(field.label or field.key.replace("_", " ").title())
    value = _private_text(field.value, privacy_scope=field.privacy_scope, safe_alternate=field.safe_alternate, policy=policy, context=context)
    href = _raw_href(field.href, privacy_scope=field.privacy_scope, policy=policy, context=context)
    classes = [
        "pc-detail-dossier-field",
        f"pc-dashboard-tone-{_tone(field.tone)}",
    ]
    if field.mono:
        classes.append("pc-detail-dossier-mono")
    if field.numeric:
        classes.append("pc-detail-dossier-numeric")
    if field.muted:
        classes.append("pc-detail-dossier-muted")
    if field.wide:
        classes.append("pc-detail-dossier-field-wide")
    classes.append(_private_class(privacy_scope=field.privacy_scope, policy=policy, context=context))
    value_html = escape(str(value or ""))
    if href and value_html:
        value_html = f'<a href="{escape(str(href), quote=True)}">{value_html}</a>'
    elif not value_html:
        value_html = '<span class="pc-detail-dossier-empty-value">-</span>'
    detail = f'<small>{escape(str(field.detail))}</small>' if field.detail else ""
    badges = _badges_html(field.badges)
    return (
        f'<div class="{" ".join(part for part in classes if part)}"{_attrs(title=field.title)}>'
        f"<dt>{escape(label)}</dt><dd>{value_html}{detail}{badges}</dd></div>"
    )


def _metrics_html(metrics: Sequence[DetailDossierMetric | Mapping[str, object]]) -> str:
    cards = []
    for raw_metric in metrics:
        metric = _coerce(raw_metric, DetailDossierMetric)
        if not metric.label:
            continue
        body = (
            f'<span>{escape(str(metric.label))}</span>'
            f'<strong>{escape(str(metric.value))}</strong>'
            + (f'<em>{escape(str(metric.detail))}</em>' if metric.detail else "")
        )
        cls = f"pc-dashboard-stat pc-detail-dossier-metric pc-dashboard-tone-{_tone(metric.tone)}"
        cards.append(f'<a class="{cls}" href="{escape(str(metric.href), quote=True)}">{body}</a>' if metric.href else f'<div class="{cls}">{body}</div>')
    return f'<div class="pc-dashboard-stat-grid pc-detail-dossier-metrics">{"".join(cards)}</div>' if cards else ""


def _sections_html(
    sections: Sequence[DetailDossierSection | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    body = "".join(_section_html(section, policy=policy, context=context) for section in sections)
    return f'<div class="pc-detail-dossier-sections">{body}</div>' if body else ""


def _section_html(
    raw_section: DetailDossierSection | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    section = _coerce(raw_section, DetailDossierSection)
    fields = _fields_html(section.fields, policy=policy, context=context, class_name="pc-detail-dossier-section-fields")
    body_text = _private_text(
        section.body,
        privacy_scope=section.body_privacy_scope,
        safe_alternate=section.body_safe_alternate,
        policy=policy,
        context=context,
    )
    body = f'<p class="pc-detail-dossier-body">{escape(str(body_text))}</p>' if body_text else ""
    body += str(section.body_html or "")
    table = _table_html(_coerce(section.table, DetailDossierSourceTable) if section.table else None, policy=policy, context=context)
    badges = _badges_html(section.badges)
    actions = _actions_html(section.actions, class_name="pc-detail-dossier-section-action")
    action_html = f'<div class="pc-detail-dossier-section-actions">{actions}</div>' if actions else ""
    if not any((fields, body, table, badges, action_html)):
        return ""
    return f"""
    <section class="pc-detail-dossier-section pc-dashboard-tone-{_tone(section.tone)}" id="{escape(str(section.key), quote=True)}">
      <div class="pc-detail-dossier-section-head">
        <div>
          <h3>{escape(str(section.title or section.key.replace("_", " ").title()))}</h3>
          <p>{escape(str(section.subtitle or ""))}</p>
        </div>
        {action_html}
      </div>
      {badges}
      {body}
      {fields}
      {table}
    </section>
"""


def _tables_html(
    tables: Sequence[DetailDossierSourceTable | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    body = "".join(_table_html(_coerce(table, DetailDossierSourceTable), policy=policy, context=context) for table in tables)
    return f'<div class="pc-detail-dossier-source-tables">{body}</div>' if body else ""


def _table_html(
    table: DetailDossierSourceTable | None,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if table is None:
        return ""
    columns = _columns(table)
    rows = [_coerce(row, DetailDossierTableRow) for row in table.rows]
    head = ""
    for column in columns:
        classes = ["pc-detail-dossier-th", f"pc-detail-dossier-align-{_align(column.align)}"]
        if column.hidden_mobile:
            classes.append("is-mobile-hidden")
        head += f'<th class="{" ".join(classes)}" scope="col"{_attrs(title=column.title)}>{escape(str(column.label or column.key))}</th>'
    if _has_row_actions(rows):
        head += '<th class="pc-detail-dossier-th pc-detail-dossier-actions-col" scope="col">Actions</th>'
    body = _table_rows_html(columns, rows, table, policy=policy, context=context)
    actions = _actions_html(table.actions, class_name="pc-detail-dossier-table-action")
    action_html = f'<div class="pc-detail-dossier-table-actions">{actions}</div>' if actions else ""
    return f"""
    <section class="pc-detail-dossier-table-panel" id="{escape(str(table.key), quote=True)}">
      <div class="pc-detail-dossier-section-head">
        <div>
          <h3>{escape(str(table.title or table.key.replace("_", " ").title()))}</h3>
          <p>{escape(str(table.subtitle or ""))}</p>
        </div>
        {action_html}
      </div>
      <div class="pc-detail-dossier-table-wrap">
        <table class="pc-detail-dossier-table">
          <thead><tr>{head}</tr></thead>
          <tbody>{body}</tbody>
        </table>
      </div>
    </section>
"""


def _columns(table: DetailDossierSourceTable) -> list[DetailDossierTableColumn]:
    columns: list[DetailDossierTableColumn] = []
    seen: set[str] = set()
    for raw_column in table.columns:
        column = DetailDossierTableColumn(raw_column, str(raw_column).replace("_", " ").title()) if isinstance(raw_column, str) else _coerce(raw_column, DetailDossierTableColumn)
        key = str(column.key or "").strip()
        if key and key not in seen:
            seen.add(key)
            columns.append(column)
    if columns:
        return columns
    for raw_row in table.rows:
        row = _coerce(raw_row, DetailDossierTableRow)
        for raw_cell in row.cells:
            cell = _coerce(raw_cell, DetailDossierTableCell)
            key = str(cell.key or "").strip()
            if key and key not in seen:
                seen.add(key)
                columns.append(DetailDossierTableColumn(key, cell.label or key.replace("_", " ").title()))
    return columns


def _table_rows_html(
    columns: Sequence[DetailDossierTableColumn],
    rows: Sequence[DetailDossierTableRow],
    table: DetailDossierSourceTable,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        colspan = max(1, len(columns) + (1 if _has_row_actions(rows) else 0))
        return f'<tr><td colspan="{colspan}" class="pc-detail-dossier-empty">{escape(str(table.empty_label or "No source rows."))}</td></tr>'
    return "".join(_table_row_html(columns, row, policy=policy, context=context) for row in rows)


def _table_row_html(
    columns: Sequence[DetailDossierTableColumn],
    row: DetailDossierTableRow,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    cells_by_key = {cell.key: cell for cell in (_coerce(raw_cell, DetailDossierTableCell) for raw_cell in row.cells) if cell.key}
    body = []
    for column in columns:
        cell = cells_by_key.get(column.key, DetailDossierTableCell(column.key))
        body.append(_table_cell_html(column, cell, policy=policy, context=context))
    actions = _actions_html(row.actions, class_name="pc-detail-dossier-row-action")
    if actions:
        body.append(f'<td class="pc-detail-dossier-cell pc-detail-dossier-row-actions">{actions}</td>')
    return f'<tr class="pc-detail-dossier-row pc-dashboard-tone-{_tone(row.tone)}"{_attrs(data_key=str(row.key or ""), title=row.title)}>{"".join(body)}</tr>'


def _table_cell_html(
    column: DetailDossierTableColumn,
    cell: DetailDossierTableCell,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    text = _private_text(cell.value, privacy_scope=cell.privacy_scope, safe_alternate=cell.safe_alternate, policy=policy, context=context)
    href = _raw_href(cell.href, privacy_scope=cell.privacy_scope, policy=policy, context=context)
    classes = [
        "pc-detail-dossier-cell",
        f"pc-dashboard-tone-{_tone(cell.tone)}",
        f"pc-detail-dossier-align-{_align(column.align)}",
    ]
    if cell.mono:
        classes.append("pc-detail-dossier-mono")
    if cell.numeric:
        classes.append("pc-detail-dossier-numeric")
    if cell.muted:
        classes.append("pc-detail-dossier-muted")
    if column.hidden_mobile:
        classes.append("is-mobile-hidden")
    classes.append(_private_class(privacy_scope=cell.privacy_scope, policy=policy, context=context))
    value = escape(str(text or ""))
    if href and value:
        value = f'<a href="{escape(str(href), quote=True)}">{value}</a>'
    elif not value:
        value = '<span class="pc-detail-dossier-empty-value">-</span>'
    detail = f'<small>{escape(str(cell.detail))}</small>' if cell.detail else ""
    return f'<td class="{" ".join(part for part in classes if part)}"><span>{value}</span>{detail}</td>'


def _side_panel_html(related: str, timeline: str, audit: str, action_slots: str) -> str:
    body = related + timeline + audit + action_slots
    return f'<div class="pc-detail-dossier-side">{body}</div>' if body else ""


def _timeline_html(
    events: Sequence[DetailDossierTimelineEvent | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    items = []
    for raw_event in events:
        event = _coerce(raw_event, DetailDossierTimelineEvent)
        summary = _private_text(event.summary, privacy_scope=event.privacy_scope, safe_alternate=event.safe_alternate, policy=policy, context=context)
        detail = _private_text(event.detail, privacy_scope=event.privacy_scope, safe_alternate=event.safe_alternate, policy=policy, context=context)
        href = _raw_href(event.href, privacy_scope=event.privacy_scope, policy=policy, context=context)
        title = escape(str(event.title))
        if href:
            title = f'<a href="{escape(str(href), quote=True)}">{title}</a>'
        badges = _badges_html(event.badges)
        items.append(
            f'<li class="pc-detail-dossier-timeline-event pc-dashboard-tone-{_tone(event.tone)}">'
            f'<div><strong>{title}</strong><span>{escape(str(event.when or ""))}</span></div>'
            f'<p>{escape(str(summary or ""))}</p>'
            f'{f"<small>{escape(str(detail))}</small>" if detail else ""}'
            f'{f"<em>{escape(str(event.actor))}</em>" if event.actor else ""}{badges}</li>'
        )
    return '<section class="pc-detail-dossier-side-panel"><h3>Timeline</h3><ol class="pc-detail-dossier-timeline">' + "".join(items) + "</ol></section>" if items else ""


def _related_html(links: Sequence[DetailDossierRelatedLink | Mapping[str, object]]) -> str:
    items = []
    for raw_link in links:
        link = _coerce(raw_link, DetailDossierRelatedLink)
        if not link.label:
            continue
        label = escape(str(link.label))
        body = f'<a href="{escape(str(link.href), quote=True)}">{label}</a>' if link.href else f"<span>{label}</span>"
        badges = _badges_html(link.badges)
        items.append(f'<li class="pc-dashboard-tone-{_tone(link.tone)}">{body}<small>{escape(str(link.summary or ""))}</small>{badges}</li>')
    return '<section class="pc-detail-dossier-side-panel"><h3>Related</h3><ul class="pc-detail-dossier-related">' + "".join(items) + "</ul></section>" if items else ""


def _audit_html(
    rows: Sequence[DetailDossierAuditRow | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    items = []
    for raw_row in rows:
        row = _coerce(raw_row, DetailDossierAuditRow)
        value = _private_text(row.value, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
        items.append(
            f'<div class="pc-detail-dossier-audit-row pc-dashboard-tone-{_tone(row.tone)}">'
            f'<dt>{escape(str(row.label or row.key))}</dt><dd>{escape(str(value or ""))}'
            f'{f"<small>{escape(str(row.actor))}</small>" if row.actor else ""}'
            f'{f"<time>{escape(str(row.when))}</time>" if row.when else ""}</dd></div>'
        )
    return '<section class="pc-detail-dossier-side-panel"><h3>Audit</h3><dl class="pc-detail-dossier-audit">' + "".join(items) + "</dl></section>" if items else ""


def _action_slots_html(
    slots: Sequence[DetailDossierActionSlot | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    items = []
    for raw_slot in slots:
        slot = _coerce(raw_slot, DetailDossierActionSlot)
        body_text = _private_text(slot.body, privacy_scope=slot.privacy_scope, safe_alternate=slot.safe_alternate, policy=policy, context=context)
        body = f'<p>{escape(str(body_text))}</p>' if body_text else ""
        body += str(slot.body_html or "")
        actions = _actions_html(slot.actions, class_name="pc-detail-dossier-slot-action")
        action_html = f'<div class="pc-detail-dossier-slot-actions">{actions}</div>' if actions else ""
        items.append(
            f'<section class="pc-detail-dossier-action-slot pc-dashboard-tone-{_tone(slot.tone)}" id="{escape(str(slot.key), quote=True)}">'
            f'<h3>{escape(str(slot.label))}</h3><small>{escape(str(slot.description or ""))}</small>{body}{action_html}</section>'
        )
    return "".join(items)


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], *, class_name: str) -> str:
    body = []
    for raw_action in actions:
        action = _coerce(raw_action, SurfaceAction)
        if not action.label:
            continue
        tone = _tone(action.tone)
        cls = f"{class_name} pc-dashboard-tone-{tone}"
        method = str(action.method or "").strip().lower()
        method_attr = _attrs(data_method=method) if method and method != "get" else ""
        title = _attrs(title=action.title)
        if action.disabled or not action.href:
            body.append(f'<span class="{cls} is-disabled"{title}>{escape(str(action.label))}</span>')
        else:
            body.append(f'<a class="{cls}" href="{escape(str(action.href), quote=True)}"{method_attr}{title}>{escape(str(action.label))}</a>')
    return "".join(body)


def _badge_html(raw_badge: SurfaceBadge | Mapping[str, object] | str) -> str:
    badge = SurfaceBadge(str(raw_badge)) if isinstance(raw_badge, str) else _coerce(raw_badge, SurfaceBadge)
    if not badge.label:
        return ""
    return f'<span class="pc-surface-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-surface-badges pc-detail-dossier-badges">{body}</div>' if body else ""


def _has_row_actions(rows: Sequence[DetailDossierTableRow]) -> bool:
    return any(row.actions for row in rows)


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
        return "is-private"
    mode = privacy_render_mode(
        policy,
        context,
        privacy_scope,
        has_safe_alternate=False,
    )
    return "is-private" if mode.value != "raw" else ""
