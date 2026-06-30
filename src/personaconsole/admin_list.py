from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    AdminListCell,
    AdminListColumn,
    AdminListFilterField,
    AdminListPagination,
    AdminListRow,
    AdminListSurfaceConfig,
    DashboardFilter,
    DashboardMetric,
    SettingsOption,
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

ADMIN_LIST_FEATURE = "admin_list"

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

_INPUT_TYPES = {
    "date",
    "datetime-local",
    "email",
    "month",
    "number",
    "search",
    "tel",
    "text",
    "time",
    "url",
    "week",
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


def _align(value: object) -> str:
    clean = str(value or "").strip().lower()
    return clean if clean in {"left", "center", "right"} else "left"


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
    return "".join(parts)


def admin_list_surface_feature_enabled(
    config: AdminListSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, AdminListSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or ADMIN_LIST_FEATURE),
        default=True,
    )


def render_admin_list_surface(
    config: AdminListSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, AdminListSurfaceConfig)
    if not admin_list_surface_feature_enabled(model, features):
        return ""

    columns = _columns(model)
    rows = [_coerce(row, AdminListRow) for row in model.rows]
    actions = _actions_html(model.actions, class_name="pc-admin-list-action")
    header_actions = f'<div class="pc-admin-list-actions">{actions}</div>' if actions else ""
    tabs = render_status_tabs(model.status_tabs, aria_label=f"{model.title or 'Admin list'} status")
    filters = _filters_html(model.filters)
    filter_form = _filter_form_html(model)
    metrics = _metrics_html(model.metrics)
    table = _table_html(columns, rows, model, policy=privacy_policy, context=privacy_context)
    cards = _mobile_cards_html(columns, rows, model, policy=privacy_policy, context=privacy_context)
    pagination = _pagination_html(model.pagination, row_label=model.row_label)
    section_id = str(model.key or "admin-list")
    label = escape(str(model.table_label or model.title or "Admin list"))
    return f"""
<section id="{escape(section_id, quote=True)}" class="pc-dashboard-panel pc-admin-list-surface" data-pc-admin-list>
  <div class="pc-dashboard-panel-head pc-admin-list-head">
    <div class="pc-dashboard-title-group">
      <div class="pc-dashboard-section-title">{escape(str(model.title or "Admin List"))}</div>
      <div class="pc-dashboard-section-meta">{escape(str(model.subtitle or ""))}</div>
    </div>
    {header_actions}
  </div>
  {tabs}
  {filters}
  {filter_form}
  {metrics}
  <div class="pc-admin-list-table-wrap">
    <table class="pc-admin-list-table" aria-label="{label}">
      {_thead_html(columns, has_actions=_has_row_actions(rows))}
      <tbody>{table}</tbody>
    </table>
  </div>
  {cards}
  {pagination}
</section>
"""


def _columns(config: AdminListSurfaceConfig) -> list[AdminListColumn]:
    columns: list[AdminListColumn] = []
    seen: set[str] = set()
    for raw_column in config.columns:
        if isinstance(raw_column, str):
            column = AdminListColumn(raw_column, raw_column.replace("_", " ").title())
        else:
            column = _coerce(raw_column, AdminListColumn)
        key = str(column.key or "").strip()
        if not key or key in seen:
            continue
        seen.add(key)
        columns.append(column)
    if columns:
        return columns
    for raw_row in config.rows:
        row = _coerce(raw_row, AdminListRow)
        for raw_cell in row.cells:
            cell = _coerce(raw_cell, AdminListCell)
            key = str(cell.key or "").strip()
            if key and key not in seen:
                seen.add(key)
                columns.append(AdminListColumn(key, cell.label or key.replace("_", " ").title()))
    return columns


def _thead_html(columns: Sequence[AdminListColumn], *, has_actions: bool) -> str:
    if not columns:
        return "<thead><tr><th>Row</th></tr></thead>"
    cells = []
    for column in columns:
        direction = str(column.direction or "").strip().lower()
        if direction not in {"asc", "desc"}:
            direction = ""
        classes = ["pc-admin-list-th", f"pc-admin-list-align-{_align(column.align)}"]
        if column.sortable:
            classes.append("is-sortable")
        if column.active:
            classes.append("is-active")
        if column.hidden_mobile:
            classes.append("is-mobile-hidden")
        body = escape(str(column.label or column.key))
        if column.sortable and column.href:
            direction_label = f'<span class="pc-admin-list-sort">{escape(direction or "sort")}</span>'
            body = (
                f'<a href="{escape(str(column.href), quote=True)}"{_attrs(title=column.title)}>'
                f"<span>{body}</span>{direction_label}</a>"
            )
        elif column.title:
            body = f'<span{_attrs(title=column.title)}>{body}</span>'
        cells.append(f'<th class="{" ".join(classes)}" scope="col">{body}</th>')
    if has_actions:
        cells.append('<th class="pc-admin-list-th pc-admin-list-actions-col" scope="col">Actions</th>')
    return "<thead><tr>" + "".join(cells) + "</tr></thead>"


def _table_html(
    columns: Sequence[AdminListColumn],
    rows: Sequence[AdminListRow],
    config: AdminListSurfaceConfig,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        colspan = max(1, len(columns) + (1 if _has_row_actions(rows) else 0))
        return (
            f'<tr><td colspan="{colspan}" class="pc-admin-list-empty">'
            f"{escape(str(config.empty_label or 'No rows found.'))}</td></tr>"
        )
    return "".join(_row_html(columns, row, policy=policy, context=context) for row in rows)


def _row_html(
    columns: Sequence[AdminListColumn],
    row: AdminListRow,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    cells_by_key = _cells_by_key(row)
    row_classes = ["pc-admin-list-row", f"pc-dashboard-tone-{_tone(row.tone)}"]
    body = []
    for column in columns:
        cell = cells_by_key.get(column.key, AdminListCell(column.key))
        body.append(_cell_html(cell, column, policy=policy, context=context))
    actions = _actions_html(row.actions, class_name="pc-admin-list-row-action")
    if actions:
        body.append(f'<td class="pc-admin-list-cell pc-admin-list-row-actions">{actions}</td>')
    return (
        f'<tr class="{" ".join(row_classes)}"{_attrs(data_key=str(row.key or ""), title=row.title)}>'
        + "".join(body)
        + "</tr>"
    )


def _cell_html(
    cell: AdminListCell,
    column: AdminListColumn,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    text = _private_text(
        cell.value,
        privacy_scope=cell.privacy_scope,
        safe_alternate=cell.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(cell.href, privacy_scope=cell.privacy_scope, policy=policy, context=context)
    classes = [
        "pc-admin-list-cell",
        f"pc-dashboard-tone-{_tone(cell.tone)}",
        f"pc-admin-list-align-{_align(column.align)}",
    ]
    if cell.mono:
        classes.append("pc-admin-list-mono")
    if cell.nowrap or cell.numeric:
        classes.append("pc-admin-list-nowrap")
    if cell.numeric:
        classes.append("pc-admin-list-numeric")
    if cell.muted:
        classes.append("pc-admin-list-muted")
    if column.hidden_mobile:
        classes.append("is-mobile-hidden")
    classes.append(_private_class(privacy_scope=cell.privacy_scope, policy=policy, context=context).strip())
    label = f'<span class="pc-admin-list-cell-label">{escape(str(cell.label or column.label or column.key))}</span>'
    value = escape(str(text or ""))
    if href and value:
        value = f'<a class="pc-admin-list-cell-link" href="{escape(str(href), quote=True)}">{value}</a>'
    elif value:
        value = f'<span class="pc-admin-list-cell-value">{value}</span>'
    else:
        value = '<span class="pc-admin-list-empty-value">-</span>'
    detail = f'<span class="pc-admin-list-cell-detail">{escape(str(cell.detail))}</span>' if cell.detail else ""
    badges = _badges_html(cell.badges)
    return f'<td class="{" ".join(part for part in classes if part)}"{_attrs(title=cell.title)}>{label}{value}{detail}{badges}</td>'


def _cells_by_key(row: AdminListRow) -> dict[str, AdminListCell]:
    result: dict[str, AdminListCell] = {}
    for raw_cell in row.cells:
        cell = _coerce(raw_cell, AdminListCell)
        key = str(cell.key or "").strip()
        if key:
            result[key] = cell
    return result


def _filters_html(filters: Sequence[DashboardFilter | Mapping[str, object]]) -> str:
    items = []
    for raw_filter in filters:
        item = _coerce(raw_filter, DashboardFilter)
        if not item.label:
            continue
        active = " is-active" if item.active else ""
        color = f'<span class="pc-dashboard-filter-swatch" style="background:{escape(str(item.color), quote=True)}"></span>' if item.color else ""
        key = f"<small>{escape(str(item.key))}</small>" if item.key else ""
        href = escape(str(item.href or "#"), quote=True)
        items.append(f'<a class="pc-dashboard-filter pc-admin-list-filter{active}" href="{href}">{color}<span>{escape(str(item.label))}</span>{key}</a>')
    return '<div class="pc-dashboard-filters pc-admin-list-filters">' + "".join(items) + "</div>" if items else ""


def _filter_form_html(config: AdminListSurfaceConfig) -> str:
    fields_html = "".join(_filter_field_html(field) for field in config.filter_fields)
    if not fields_html:
        return ""
    action = escape(str(config.filter_action or ""), quote=True)
    method = str(config.filter_method or "get").strip().lower()
    method = method if method in {"get", "post"} else "get"
    reset = ""
    if config.reset_href:
        reset = f'<a class="pc-admin-list-button pc-admin-list-button-muted" href="{escape(str(config.reset_href), quote=True)}">Reset</a>'
    return f"""
  <form class="pc-admin-list-filter-form" action="{action}" method="{method}">
    {fields_html}
    <button class="pc-admin-list-button" type="submit">{escape(str(config.filter_submit_label or "Filter"))}</button>
    {reset}
  </form>
"""


def _filter_field_html(raw_field: AdminListFilterField | Mapping[str, object]) -> str:
    field = _coerce(raw_field, AdminListFilterField)
    if not field.name:
        return ""
    name = escape(str(field.name), quote=True)
    kind = str(field.kind or "text").strip().lower()
    if field.hidden or kind == "hidden":
        return f'<input type="hidden" name="{name}" value="{escape(str(field.value), quote=True)}">'
    label = escape(str(field.label or field.name.replace("_", " ").title()))
    value = str(field.value or "")
    if kind == "select":
        options = "".join(_option_html(option, selected_value=value) for option in field.options)
        return f'<label class="pc-admin-list-field"><span>{label}</span><select name="{name}">{options}</select></label>'
    if kind == "checkbox":
        checked = " checked" if _truthy(field.value) else ""
        return (
            f'<label class="pc-admin-list-field pc-admin-list-check">'
            f'<input type="checkbox" name="{name}" value="1"{checked}><span>{label}</span></label>'
        )
    input_type = kind if kind in _INPUT_TYPES else "text"
    placeholder = escape(str(field.placeholder or ""), quote=True)
    return (
        f'<label class="pc-admin-list-field"><span>{label}</span>'
        f'<input type="{input_type}" name="{name}" value="{escape(value, quote=True)}" placeholder="{placeholder}"></label>'
    )


def _option_html(raw_option: SettingsOption | Mapping[str, object] | str, *, selected_value: str) -> str:
    if isinstance(raw_option, str):
        option = SettingsOption(raw_option, raw_option)
    else:
        option = _coerce(raw_option, SettingsOption)
    key = str(option.key)
    selected = " selected" if option.selected or key == selected_value else ""
    disabled = " disabled" if option.disabled else ""
    title = _attrs(title=option.description)
    return f'<option value="{escape(key, quote=True)}"{selected}{disabled}{title}>{escape(str(option.label or key))}</option>'


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
        cls = f"pc-dashboard-stat pc-admin-list-metric pc-dashboard-tone-{_tone(item.tone)}"
        cards.append(f'<a class="{cls}" href="{escape(str(item.href), quote=True)}">{body}</a>' if item.href else f'<div class="{cls}">{body}</div>')
    return '<div class="pc-dashboard-stat-grid pc-admin-list-metrics">' + "".join(cards) + "</div>" if cards else ""


def _mobile_cards_html(
    columns: Sequence[AdminListColumn],
    rows: Sequence[AdminListRow],
    config: AdminListSurfaceConfig,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        return ""
    items = []
    for row in rows:
        cells_by_key = _cells_by_key(row)
        cells = [cells_by_key.get(column.key, AdminListCell(column.key)) for column in columns]
        primary = _pick_cell(cells, config.mobile_card_primary_key, fallback_index=0)
        secondary = _pick_cell(cells, config.mobile_card_secondary_key, fallback_index=1)
        summary = _private_text(
            row.summary,
            privacy_scope=row.summary_privacy_scope,
            safe_alternate=row.summary_safe_alternate,
            policy=policy,
            context=context,
        )
        badges = _badges_html(row.badges)
        actions = _actions_html(row.actions, class_name="pc-admin-list-row-action")
        details = "".join(
            _mobile_detail_html(column, cells_by_key.get(column.key, AdminListCell(column.key)), policy=policy, context=context)
            for column in columns
        )
        primary_html = _mobile_value_html(primary, policy=policy, context=context, class_name="pc-admin-list-card-title")
        secondary_html = _mobile_value_html(secondary, policy=policy, context=context, class_name="pc-admin-list-card-meta")
        summary_html = f'<p>{escape(summary)}</p>' if summary else ""
        actions_html = f'<div class="pc-admin-list-card-actions">{actions}</div>' if actions else ""
        items.append(
            f'<article class="pc-admin-list-card pc-dashboard-tone-{_tone(row.tone)}"{_attrs(data_key=str(row.key or ""), title=row.title)}>'
            f'<div class="pc-admin-list-card-head">{primary_html}{secondary_html}</div>{badges}{summary_html}'
            f'<dl class="pc-admin-list-card-details">{details}</dl>{actions_html}</article>'
        )
    aria = escape(str(config.card_label or config.table_label or config.title or "Admin list cards"), quote=True)
    return f'<div class="pc-admin-list-cards" aria-label="{aria}">{"".join(items)}</div>'


def _mobile_detail_html(
    column: AdminListColumn,
    cell: AdminListCell,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    text = _private_text(cell.value, privacy_scope=cell.privacy_scope, safe_alternate=cell.safe_alternate, policy=policy, context=context)
    if not text and not cell.badges:
        return ""
    value = escape(str(text or ""))
    badges = _badges_html(cell.badges)
    return (
        f'<div><dt>{escape(str(cell.label or column.label or column.key))}</dt>'
        f'<dd>{value}{badges}</dd></div>'
    )


def _pick_cell(cells: Sequence[AdminListCell], key: str, *, fallback_index: int) -> AdminListCell:
    if key:
        for cell in cells:
            if cell.key == key:
                return cell
    if len(cells) > fallback_index:
        return cells[fallback_index]
    if cells:
        return cells[0]
    return AdminListCell("row")


def _mobile_value_html(
    cell: AdminListCell,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
    class_name: str,
) -> str:
    text = _private_text(cell.value, privacy_scope=cell.privacy_scope, safe_alternate=cell.safe_alternate, policy=policy, context=context)
    href = _raw_href(cell.href, privacy_scope=cell.privacy_scope, policy=policy, context=context)
    value = escape(str(text or ""))
    if not value:
        return ""
    if href:
        return f'<a class="{class_name}" href="{escape(str(href), quote=True)}">{value}</a>'
    return f'<span class="{class_name}">{value}</span>'


def _pagination_html(raw_pagination: AdminListPagination | Mapping[str, object] | None, *, row_label: str) -> str:
    if not raw_pagination:
        return ""
    pagination = _coerce(raw_pagination, AdminListPagination)
    summary = str(pagination.summary or "").strip()
    if not summary:
        count = str(pagination.count or "").strip()
        page = str(pagination.page or "").strip()
        page_count = str(pagination.page_count or "").strip()
        if count:
            label = str(row_label or "row")
            summary = f"{count} {label}{'' if count == '1' else 's'}"
        if page and page_count:
            summary = (summary + " · " if summary else "") + f"Page {page} of {page_count}"
    prev_class = "pc-admin-list-page-link" + ("" if pagination.previous_href else " is-disabled")
    next_class = "pc-admin-list-page-link" + ("" if pagination.next_href else " is-disabled")
    prev = _page_link(pagination.previous_label or "Previous", pagination.previous_href, prev_class)
    next_link = _page_link(pagination.next_label or "Next", pagination.next_href, next_class)
    return (
        '<nav class="pc-admin-list-pagination" aria-label="Pagination">'
        f'<span>{escape(summary)}</span><div>{prev}{next_link}</div></nav>'
    )


def _page_link(label: str, href: str, class_name: str) -> str:
    if href:
        return f'<a class="{class_name}" href="{escape(str(href), quote=True)}">{escape(str(label))}</a>'
    return f'<span class="{class_name}" aria-disabled="true">{escape(str(label))}</span>'


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
    return f'<div class="pc-surface-badges pc-admin-list-badges">{body}</div>' if body else ""


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


def _has_row_actions(rows: Sequence[AdminListRow]) -> bool:
    return any(bool(row.actions) for row in rows)


def _truthy(value: object) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "checked"}
