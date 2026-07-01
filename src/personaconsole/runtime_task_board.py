from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    AdminListPagination,
    DashboardFilter,
    DashboardMetric,
    RuntimeTaskActionSlot,
    RuntimeTaskBoardSurfaceConfig,
    RuntimeTaskHistoryRow,
    RuntimeTaskLinkedRecord,
    RuntimeTaskRow,
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

RUNTIME_TASK_BOARD_FEATURE = "runtime_task_board"

T = TypeVar("T")

_TONE_ALIASES = {
    "accepted": "good",
    "active": "info",
    "bad": "bad",
    "blocked": "bad",
    "closed": "good",
    "critical": "bad",
    "danger": "bad",
    "done": "good",
    "error": "bad",
    "failed": "bad",
    "good": "good",
    "high": "bad",
    "info": "info",
    "low": "neutral",
    "medium": "warn",
    "neutral": "neutral",
    "open": "info",
    "pending": "warn",
    "ready": "good",
    "review": "warn",
    "running": "info",
    "stale": "warn",
    "todo": "info",
    "triage": "warn",
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
    return f'<span class="pc-runtime-task-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-runtime-task-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], features: Mapping[str, bool] | None) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label or (action.feature and not feature_enabled(features, action.feature, default=True)):
        return ""
    method = str(action.method or "").strip().upper()
    cls = f"pc-runtime-task-action pc-dashboard-tone-{_tone(action.tone)}"
    body = escape(str(action.label))
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{_attrs(title=action.title)}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(str(action.href), quote=True)}"{_attrs(data_method=method) if method else ""}{_attrs(title=action.title)}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], features: Mapping[str, bool] | None) -> str:
    body = "".join(_action_html(action, features) for action in actions)
    return f'<div class="pc-runtime-task-actions">{body}</div>' if body else ""


def runtime_task_board_feature_enabled(
    config: RuntimeTaskBoardSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, RuntimeTaskBoardSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or RUNTIME_TASK_BOARD_FEATURE), default=True)


def _status_html(status: object, tone: object = "") -> str:
    if not status:
        return ""
    return f'<span class="pc-surface-status pc-dashboard-tone-{_tone(tone or status)}">{escape(str(status))}</span>'


def _filters_html(filters: Sequence[DashboardFilter | Mapping[str, object]]) -> str:
    parts = []
    for raw_filter in filters:
        item = _coerce(raw_filter, DashboardFilter)
        if not item.label:
            continue
        active = " is-active" if item.active else ""
        key = f"<small>{escape(str(item.key))}</small>" if item.key else ""
        parts.append(
            f'<a class="pc-runtime-task-filter{active}" href="{escape(str(item.href or "#"), quote=True)}">'
            f'<span>{escape(str(item.label))}</span>{key}</a>'
        )
    return f'<div class="pc-runtime-task-filters">{"".join(parts)}</div>' if parts else ""


def _metrics_html(metrics: Sequence[DashboardMetric | Mapping[str, object]]) -> str:
    cards = []
    for raw_metric in metrics:
        item = _coerce(raw_metric, DashboardMetric, {"label": "Metric", "value": ""})
        body = (
            f'<span>{escape(str(item.label))}</span>'
            f'<strong>{escape(str(item.value))}</strong>'
            f'<small>{escape(str(item.detail))}</small>'
        )
        cls = f"pc-runtime-task-metric pc-dashboard-tone-{_tone(item.tone)}"
        if item.href:
            cards.append(f'<a class="{cls}" href="{escape(str(item.href), quote=True)}">{body}</a>')
        else:
            cards.append(f'<article class="{cls}">{body}</article>')
    return f'<div class="pc-runtime-task-metrics">{"".join(cards)}</div>' if cards else ""


def _task_title_summary(
    row: RuntimeTaskRow,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> tuple[str, str, str, str]:
    safe = row.safe_alternate or "Private task summarized for operators."
    title = _private_text(row.title, privacy_scope=row.privacy_scope, safe_alternate=safe, policy=policy, context=context)
    summary = _private_text(row.summary, privacy_scope=row.privacy_scope, safe_alternate=safe, policy=policy, context=context)
    detail = _private_text(row.detail, privacy_scope=row.privacy_scope, safe_alternate=safe, policy=policy, context=context)
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    return title, summary, detail, href


def _task_table_html(
    rows: Sequence[RuntimeTaskRow],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
    empty_label: str,
) -> str:
    if not rows:
        return f'<tr><td colspan="7" class="pc-runtime-task-empty">{escape(empty_label)}</td></tr>'
    body = ""
    for row in rows:
        title, summary, _detail, href = _task_title_summary(row, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        open_cell = f'<a href="{escape(href, quote=True)}">Open</a>' if href else '<span>Open</span>'
        body += (
            f'<tr class="pc-dashboard-tone-{_tone(row.tone or row.status)}{private}">'
            f'<td class="pc-runtime-task-open">{open_cell}</td>'
            f'<td><strong>{escape(title)}</strong><p>{escape(summary)}</p>{_badges_html(row.badges)}</td>'
            f'<td>{_status_html(row.status, row.tone)}</td>'
            f'<td>{escape(str(row.priority))}</td>'
            f'<td>{escape(str(row.owner))}</td>'
            f'<td>{escape(str(row.due_at))}</td>'
            f'<td>{escape(str(row.updated_at))}{_actions_html(row.actions, features)}</td>'
            "</tr>"
        )
    return body


def _task_cards_html(
    rows: Sequence[RuntimeTaskRow],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    cards = []
    for row in rows:
        title, summary, _detail, href = _task_title_summary(row, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        open_link = f'<a href="{escape(href, quote=True)}">Open</a>' if href else ""
        cards.append(
            f'<article class="pc-runtime-task-card pc-dashboard-tone-{_tone(row.tone or row.status)}{private}">'
            '<div class="pc-runtime-task-card-head">'
            f'<strong>{escape(title)}</strong>{_status_html(row.status, row.tone)}</div>'
            f'<p>{escape(summary)}</p>'
            '<div class="pc-runtime-task-facts">'
            f'<span><b>Priority</b>{escape(str(row.priority))}</span>'
            f'<span><b>Owner</b>{escape(str(row.owner))}</span>'
            f'<span><b>Due</b>{escape(str(row.due_at))}</span>'
            f'<span><b>Updated</b>{escape(str(row.updated_at))}</span></div>'
            f'{_badges_html(row.badges)}{_actions_html(row.actions, features)}{open_link}</article>'
        )
    return f'<div class="pc-runtime-task-cards">{"".join(cards)}</div>' if cards else ""


def _linked_record_html(
    raw_record: RuntimeTaskLinkedRecord | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    record = _coerce(raw_record, RuntimeTaskLinkedRecord, {"key": "record", "label": "Linked record"})
    detail = _private_text(record.detail, privacy_scope=record.privacy_scope, safe_alternate=record.safe_alternate, policy=policy, context=context)
    href = _raw_href(record.href, privacy_scope=record.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=record.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-runtime-task-linked-head">'
        f'<strong>{escape(str(record.label))}</strong>{_status_html(record.status, record.tone)}</div>'
        f'<small>{escape(str(record.kind))}</small>'
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(record.badges)
    )
    cls = f"pc-runtime-task-linked pc-dashboard-tone-{_tone(record.tone or record.status)}{private}"
    if href:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _history_html(
    raw_row: RuntimeTaskHistoryRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, RuntimeTaskHistoryRow, {"key": "history", "label": "History"})
    summary = _private_text(row.summary, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    open_link = f'<a href="{escape(href, quote=True)}">Open</a>' if href else ""
    return (
        f'<article class="pc-runtime-task-history-row pc-dashboard-tone-{_tone(row.tone or row.status)}{private}">'
        '<div class="pc-runtime-task-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}</div>'
        f'<p>{escape(summary)}</p><small>{escape(str(row.actor))} {escape(str(row.timestamp))}</small>'
        f'{_badges_html(row.badges)}{_actions_html(row.actions, features)}{open_link}</article>'
    )


def _detail_html(
    raw_task: RuntimeTaskRow | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not raw_task:
        return ""
    task = _coerce(raw_task, RuntimeTaskRow, {"key": "selected", "title": "Selected task"})
    title, summary, detail, href = _task_title_summary(task, policy=policy, context=context)
    records = "".join(_linked_record_html(row, policy=policy, context=context) for row in task.linked_records)
    history = "".join(_history_html(row, features=features, policy=policy, context=context) for row in task.history)
    private = _private_class(privacy_scope=task.privacy_scope, policy=policy, context=context)
    open_link = f'<a class="pc-runtime-task-action" href="{escape(href, quote=True)}">Open source</a>' if href else ""
    return (
        f'<section class="pc-runtime-task-detail pc-dashboard-tone-{_tone(task.tone or task.status)}{private}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(task.detail_title or title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(summary)}</div></div>{_status_html(task.status, task.tone)}</div>'
        f'<p>{escape(detail)}</p><div class="pc-runtime-task-facts">'
        f'<span><b>Priority</b>{escape(str(task.priority))}</span>'
        f'<span><b>Severity</b>{escape(str(task.severity))}</span>'
        f'<span><b>Owner</b>{escape(str(task.owner))}</span>'
        f'<span><b>Due</b>{escape(str(task.due_at))}</span>'
        f'<span><b>Updated</b>{escape(str(task.updated_at))}</span></div>'
        f'{_badges_html(task.badges)}{_actions_html(task.actions, features)}{open_link}'
        + (f'<div class="pc-runtime-task-linked-list"><div class="pc-dashboard-section-title">Linked Records</div>{records}</div>' if records else "")
        + (f'<div class="pc-runtime-task-history"><div class="pc-dashboard-section-title">History</div>{history}</div>' if history else "")
        + "</section>"
    )


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
            summary = f"{count} {row_label}{'' if count == '1' else 's'}"
        if page and page_count:
            summary = (summary + " · " if summary else "") + f"Page {page} of {page_count}"
    prev_cls = " is-disabled" if not pagination.previous_href else ""
    next_cls = " is-disabled" if not pagination.next_href else ""
    prev = (
        f'<a class="pc-runtime-task-page-link{prev_cls}" href="{escape(str(pagination.previous_href), quote=True)}">{escape(str(pagination.previous_label or "Previous"))}</a>'
        if pagination.previous_href
        else f'<span class="pc-runtime-task-page-link{prev_cls}" aria-disabled="true">{escape(str(pagination.previous_label or "Previous"))}</span>'
    )
    next_link = (
        f'<a class="pc-runtime-task-page-link{next_cls}" href="{escape(str(pagination.next_href), quote=True)}">{escape(str(pagination.next_label or "Next"))}</a>'
        if pagination.next_href
        else f'<span class="pc-runtime-task-page-link{next_cls}" aria-disabled="true">{escape(str(pagination.next_label or "Next"))}</span>'
    )
    return f'<div class="pc-runtime-task-pagination"><span>{summary}</span><div>{prev}{next_link}</div></div>'


def _action_slots_html(slots: Sequence[RuntimeTaskActionSlot | Mapping[str, object]], *, features: Mapping[str, bool] | None) -> str:
    body = ""
    for raw_slot in slots:
        slot = _coerce(raw_slot, RuntimeTaskActionSlot, {"key": "action-slot", "label": "Action"})
        body += (
            f'<section class="pc-runtime-task-slot pc-dashboard-tone-{_tone(slot.tone)}" data-task-slot="{escape(_key(slot.key), quote=True)}">'
            f'<h3>{escape(str(slot.label))}</h3>'
            f'<p>{escape(str(slot.description))}</p>'
            + (f'<div class="pc-runtime-task-slot-body">{slot.body_html}</div>' if slot.body_html else "")
            + _actions_html(slot.actions, features)
            + "</section>"
        )
    return f'<div class="pc-runtime-task-slots">{body}</div>' if body else ""


def render_runtime_task_board_surface(
    config: RuntimeTaskBoardSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, RuntimeTaskBoardSurfaceConfig)
    if not runtime_task_board_feature_enabled(model, features):
        return ""
    rows = [_coerce(row, RuntimeTaskRow, {"key": "task", "title": "Task"}) for row in model.tasks]
    tabs = render_status_tabs(model.tabs, aria_label=f"{model.title} status") if model.tabs else ""
    filters = _filters_html(model.filters)
    metrics = _metrics_html(model.metrics)
    live = render_live_controls(model.live_refresh) if model.live_refresh else ""
    table = (
        '<div class="pc-runtime-task-table-wrap"><table class="pc-runtime-task-table"><thead><tr>'
        '<th>Open</th><th>Task</th><th>Status</th><th>Priority</th><th>Owner</th><th>Due</th><th>Updated</th>'
        '</tr></thead><tbody>'
        + _task_table_html(rows, features=features, policy=privacy_policy, context=privacy_context, empty_label=model.empty_label)
        + "</tbody></table></div>"
    )
    cards = _task_cards_html(rows, features=features, policy=privacy_policy, context=privacy_context)
    detail = _detail_html(model.selected_task, features=features, policy=privacy_policy, context=privacy_context)
    pagination = _pagination_html(model.pagination, row_label=model.row_label)
    slots = _action_slots_html(model.action_slots, features=features)
    actions = _actions_html(model.actions, features)
    return (
        f'<section id="{escape(_key(model.key, "runtime-task-board"), quote=True)}" class="pc-runtime-task-board-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div>{_status_html(model.status, model.status_tone)}</div>'
        f"{tabs}{filters}{metrics}{live}{actions}{table}{cards}{pagination}{detail}{slots}</section>"
    )


__all__ = [
    "RUNTIME_TASK_BOARD_FEATURE",
    "render_runtime_task_board_surface",
    "runtime_task_board_feature_enabled",
]
