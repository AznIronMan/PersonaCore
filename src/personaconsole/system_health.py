from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    DashboardMetric,
    StatusTab,
    SurfaceAction,
    SurfaceBadge,
    SystemAuditFilterState,
    SystemAuditRow,
    SystemDatabaseCard,
    SystemHealthCheck,
    SystemHealthGroup,
    SystemHealthSurfaceConfig,
    SystemPaginationState,
    SystemReadinessProbe,
    SystemSecretCoverageRow,
    SystemSecretFilterState,
    SystemSecretInventoryRow,
    SystemTableSummary,
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

SYSTEM_HEALTH_FEATURE = "system_health"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "critical": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "missing": "bad",
    "unhealthy": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
    "held": "warn",
    "lagging": "warn",
    "pending": "warn",
    "stale": "warn",
    "unknown": "neutral",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "info": "info",
    "notice": "info",
    "neutral": "neutral",
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
    return f'<span class="pc-system-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-system-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object]) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label:
        return ""
    cls = f"pc-system-action pc-dashboard-tone-{_tone(action.tone)}"
    body = escape(str(action.label))
    title = _attrs(title=action.title)
    method = str(action.method or "").strip().upper()
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{title}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(action.href, quote=True)}"{_attrs(data_method=method) if method else ""}{title}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]]) -> str:
    body = "".join(_action_html(action) for action in actions)
    return f'<div class="pc-system-actions">{body}</div>' if body else ""


def _filter_chip_html(label: str, value: object) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    return (
        '<span class="pc-system-filter-chip">'
        f'<b>{escape(str(label))}</b><span>{escape(text)}</span></span>'
    )


def _filter_count_html(result_count: object, total_count: object, item_label: str) -> str:
    has_result = result_count not in (None, "")
    has_total = total_count not in (None, "")
    if not has_result and not has_total:
        return ""
    result = str(result_count if has_result else total_count)
    total = str(total_count if has_total else result_count)
    if has_result and has_total:
        text = f"Showing {result} of {total} {item_label}"
    else:
        text = f"{result} {item_label}"
    return f'<strong>{escape(text)}</strong>'


def _audit_filter_summary_html(raw_filters: SystemAuditFilterState | Mapping[str, object] | None) -> str:
    if not raw_filters:
        return ""
    filters = _coerce(raw_filters, SystemAuditFilterState)
    chips = "".join(
        _filter_chip_html(label, value)
        for label, value in (
            ("Search", filters.query),
            ("Actor", filters.actor),
            ("Action", filters.action),
            ("Entity", filters.entity),
            ("Source", filters.source),
            ("Status", filters.status),
            ("From", filters.date_from),
            ("To", filters.date_to),
        )
    )
    count = _filter_count_html(filters.result_count, filters.total_count, "audit events")
    summary = f'<p>{escape(str(filters.summary))}</p>' if filters.summary else ""
    clear = (
        f'<a class="pc-system-action" href="{escape(str(filters.clear_href), quote=True)}">Clear</a>'
        if filters.clear_href
        else ""
    )
    if not any((chips, count, summary, clear)):
        return ""
    return (
        '<div class="pc-system-filter-summary" data-system-filter="audit">'
        f'<div>{count}{summary}<div class="pc-system-filter-chips">{chips}</div></div>{clear}</div>'
    )


def _secret_filter_summary_html(raw_filters: SystemSecretFilterState | Mapping[str, object] | None) -> str:
    if not raw_filters:
        return ""
    filters = _coerce(raw_filters, SystemSecretFilterState)
    chips = "".join(
        _filter_chip_html(label, value)
        for label, value in (
            ("Search", filters.query),
            ("Section", filters.section),
            ("Source", filters.source),
            ("Status", filters.status),
            ("Import", filters.import_status),
            ("Present", filters.present),
            ("Active", filters.active),
        )
    )
    count = _filter_count_html(filters.result_count, filters.total_count, "secret rows")
    summary = f'<p>{escape(str(filters.summary))}</p>' if filters.summary else ""
    clear = (
        f'<a class="pc-system-action" href="{escape(str(filters.clear_href), quote=True)}">Clear</a>'
        if filters.clear_href
        else ""
    )
    if not any((chips, count, summary, clear)):
        return ""
    return (
        '<div class="pc-system-filter-summary" data-system-filter="secrets">'
        f'<div>{count}{summary}<div class="pc-system-filter-chips">{chips}</div></div>{clear}</div>'
    )


def _pagination_html(raw_pagination: SystemPaginationState | Mapping[str, object] | None, default_label: str) -> str:
    if not raw_pagination:
        return ""
    pagination = _coerce(raw_pagination, SystemPaginationState)
    page_bits = []
    if pagination.page not in (None, ""):
        if pagination.page_count not in (None, ""):
            page_bits.append(f"Page {pagination.page} of {pagination.page_count}")
        else:
            page_bits.append(f"Page {pagination.page}")
    if pagination.total not in (None, ""):
        page_bits.append(f"{pagination.total} total")
    if pagination.limit not in (None, ""):
        page_bits.append(f"{pagination.limit} per page")
    label = str(pagination.label or default_label)
    summary = " · ".join(str(bit) for bit in page_bits if str(bit).strip())
    if not any((summary, pagination.previous_href, pagination.next_href)):
        return ""
    previous = (
        f'<a class="pc-system-action" href="{escape(str(pagination.previous_href), quote=True)}">Previous</a>'
        if pagination.previous_href
        else '<span class="pc-system-action is-disabled" aria-disabled="true">Previous</span>'
    )
    next_link = (
        f'<a class="pc-system-action" href="{escape(str(pagination.next_href), quote=True)}">Next</a>'
        if pagination.next_href
        else '<span class="pc-system-action is-disabled" aria-disabled="true">Next</span>'
    )
    return (
        f'<nav class="pc-system-pagination" aria-label="{escape(label, quote=True)}">'
        f'<span>{escape(summary)}</span><div class="pc-system-actions">{previous}{next_link}</div></nav>'
    )


def system_health_surface_feature_enabled(
    config: SystemHealthSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, SystemHealthSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or SYSTEM_HEALTH_FEATURE), default=True)


def _metric_html(raw_metric: DashboardMetric | Mapping[str, object]) -> str:
    metric = _coerce(raw_metric, DashboardMetric, {"label": "Metric", "value": ""})
    body = (
        f'<span class="pc-system-metric-label">{escape(str(metric.label))}</span>'
        f'<strong>{escape(str(metric.value))}</strong>'
        f'<small>{escape(str(metric.detail))}</small>'
    )
    cls = f"pc-system-metric pc-dashboard-tone-{_tone(metric.tone)}"
    if metric.href:
        return f'<a class="{cls}" href="{escape(str(metric.href), quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _metrics_html(metrics: Sequence[DashboardMetric | Mapping[str, object]]) -> str:
    body = "".join(_metric_html(metric) for metric in metrics)
    return f'<div class="pc-system-metrics">{body}</div>' if body else ""


def _check_html(raw_check: SystemHealthCheck | Mapping[str, object]) -> str:
    check = _coerce(raw_check, SystemHealthCheck, {"key": "check"})
    tone = _tone(check.tone or check.status)
    flags = "".join(
        part
        for part in [
            '<span class="pc-system-required">required</span>' if check.required else "",
            '<span class="pc-system-blocked">blocked</span>' if check.blocked else "",
            f'<time>{escape(str(check.updated))}</time>' if check.updated else "",
        ]
    )
    body = (
        '<div class="pc-system-row-main">'
        f'<div class="pc-system-row-title"><strong>{escape(str(check.label or check.key))}</strong>'
        f'<span class="pc-surface-status pc-dashboard-tone-{tone}">{escape(str(check.status or "unknown"))}</span></div>'
        f'<p>{escape(str(check.summary or check.detail))}</p>'
        f'<div class="pc-system-row-meta">{flags}{_badges_html(check.badges)}</div>'
        '</div>'
        f'<div class="pc-system-row-value">{escape(str(check.value))}</div>'
        f'{_actions_html(check.actions)}'
    )
    if check.href:
        return f'<a class="pc-system-row pc-system-check pc-dashboard-tone-{tone}" href="{escape(check.href, quote=True)}">{body}</a>'
    return f'<article class="pc-system-row pc-system-check pc-dashboard-tone-{tone}">{body}</article>'


def _health_group_html(raw_group: SystemHealthGroup | Mapping[str, object]) -> str:
    group = _coerce(raw_group, SystemHealthGroup, {"key": "health", "title": "Health"})
    checks = "".join(_check_html(check) for check in group.checks)
    if not checks:
        checks = '<div class="pc-dashboard-empty">No checks in this group.</div>'
    tone = _tone(group.tone or group.status)
    status = f'<span class="pc-surface-status pc-dashboard-tone-{tone}">{escape(str(group.status))}</span>' if group.status else ""
    return (
        f'<section class="pc-system-group pc-dashboard-panel pc-dashboard-tone-{tone}" data-system-group="{escape(_key(group.key), quote=True)}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(group.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(group.description))}</div>'
        f'</div><div class="pc-system-group-meta">{status}{_badges_html(group.badges)}{_actions_html(group.actions)}</div></div>'
        f'<div class="pc-system-list">{checks}</div></section>'
    )


def _database_card_html(raw_card: SystemDatabaseCard | Mapping[str, object]) -> str:
    card = _coerce(raw_card, SystemDatabaseCard, {"key": "database"})
    tone = _tone(card.tone or card.status)
    pairs = [
        ("Database", card.database),
        ("User", card.user),
        ("Host", card.host),
        ("Schema", card.schema_version),
        ("Tables", card.tables),
        ("Records", card.records),
        ("Latency", card.latency),
    ]
    details = "".join(f'<span><b>{escape(label)}</b>{escape(str(value))}</span>' for label, value in pairs if value != "")
    body = (
        '<div class="pc-system-card-head">'
        f'<strong>{escape(str(card.label))}</strong>'
        f'<span class="pc-surface-status pc-dashboard-tone-{tone}">{escape(str(card.status))}</span></div>'
        f'<p>{escape(str(card.summary))}</p>'
        f'<div class="pc-system-card-grid">{details}</div>{_badges_html(card.badges)}{_actions_html(card.actions)}'
    )
    cls = f"pc-system-card pc-system-database pc-dashboard-tone-{tone}"
    if card.href:
        return f'<a class="{cls}" href="{escape(card.href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _database_cards_html(cards: Sequence[SystemDatabaseCard | Mapping[str, object]]) -> str:
    body = "".join(_database_card_html(card) for card in cards)
    return f'<section class="pc-system-section"><div class="pc-dashboard-section-title">Database</div><div class="pc-system-card-grid-wrap">{body}</div></section>' if body else ""


def _table_html(rows: Sequence[SystemTableSummary | Mapping[str, object]]) -> str:
    if not rows:
        return ""
    body = ""
    for raw_row in rows:
        row = _coerce(raw_row, SystemTableSummary, {"name": "table"})
        tone = _tone(row.tone or row.status)
        name = f'<a href="{escape(row.href, quote=True)}">{escape(str(row.name))}</a>' if row.href else escape(str(row.name))
        body += (
            f'<tr class="pc-dashboard-tone-{tone}"><td>{name}</td><td>{escape(str(row.status))}</td>'
            f'<td>{escape(str(row.schema))}</td><td>{escape(str(row.rows))}</td>'
            f'<td>{escape(str(row.owner))}</td><td>{escape(str(row.updated))}</td>'
            f'<td>{escape(str(row.detail))}{_badges_html(row.badges)}</td></tr>'
        )
    return (
        '<section class="pc-system-section"><div class="pc-dashboard-section-title">Schema And Tables</div>'
        '<div class="pc-system-table-wrap"><table class="pc-system-table">'
        '<thead><tr><th>Name</th><th>Status</th><th>Schema</th><th>Rows</th><th>Owner</th><th>Updated</th><th>Detail</th></tr></thead>'
        f'<tbody>{body}</tbody></table></div></section>'
    )


def _secret_metric_value(row: SystemSecretCoverageRow, field_name: str) -> object:
    value = getattr(row, field_name)
    if field_name == "configured" and value == "":
        return row.present
    return value


def _secret_group_key(row: SystemSecretCoverageRow) -> str:
    section = str(row.section or "").strip()
    source = str(row.source or "").strip()
    if section and source:
        return f"{section} / {source}"
    return section or source or "Coverage"


def _secret_coverage_card_html(raw_row: SystemSecretCoverageRow | Mapping[str, object]) -> str:
    row = _coerce(raw_row, SystemSecretCoverageRow, {"key": "secret", "label": "Secret coverage"})
    tone = _tone(row.tone or row.status)
    metrics = "".join(
        f'<span><b>{label}</b>{escape(str(value))}</span>'
        for label, value in (
            ("Configured", _secret_metric_value(row, "configured")),
            ("Missing", row.missing),
            ("Required", row.required),
            ("Optional", row.optional),
        )
        if value != ""
    )
    meta = "".join(
        f'<span><b>{label}</b>{escape(str(value))}</span>'
        for label, value in (
            ("Section", row.section),
            ("Source", row.source),
            ("Import", row.import_status),
            ("Checked", row.last_checked),
        )
        if value != ""
    )
    meta_html = f'<div class="pc-system-card-grid pc-system-card-meta">{meta}</div>' if meta else ""
    no_reveal = (
        f'<small class="pc-system-no-reveal">{escape(str(row.no_reveal_label))}</small>'
        if row.no_reveal_label
        else ""
    )
    body = (
        '<div class="pc-system-card-head">'
        f'<strong>{escape(str(row.label))}</strong>'
        f'<span class="pc-surface-status pc-dashboard-tone-{tone}">{escape(str(row.status))}</span></div>'
        f'<p>{escape(str(row.summary))}</p><div class="pc-system-card-grid">{metrics}</div>{meta_html}{no_reveal}'
        f'{_badges_html(row.badges)}{_actions_html(row.actions)}'
    )
    cls = f"pc-system-card pc-system-secret pc-dashboard-tone-{tone}"
    return f'<a class="{cls}" href="{escape(row.href, quote=True)}">{body}</a>' if row.href else f'<article class="{cls}">{body}</article>'


def _secret_html(rows: Sequence[SystemSecretCoverageRow | Mapping[str, object]]) -> str:
    if not rows:
        return ""
    groups: dict[str, list[str]] = {}
    for raw_row in rows:
        row = _coerce(raw_row, SystemSecretCoverageRow, {"key": "secret", "label": "Secret coverage"})
        groups.setdefault(_secret_group_key(row), []).append(_secret_coverage_card_html(row))
    grouped = ""
    for group_label, cards in groups.items():
        title = "" if group_label == "Coverage" and len(groups) == 1 else f'<div class="pc-system-group-label">{escape(group_label)}</div>'
        grouped += f'<div class="pc-system-secret-group">{title}<div class="pc-system-card-grid-wrap">{"".join(cards)}</div></div>'
    return f'<section class="pc-system-section"><div class="pc-dashboard-section-title">Secret Coverage</div>{grouped}</section>'


def _state_label(value: object, *, true_label: str, false_label: str) -> str:
    if isinstance(value, bool):
        return true_label if value else false_label
    raw = str(value or "").strip()
    if raw.lower() in {"true", "yes", "1"}:
        return true_label
    if raw.lower() in {"false", "no", "0"}:
        return false_label
    return raw


def _secret_inventory_summary(row: SystemSecretInventoryRow) -> str:
    parts = [str(part).strip() for part in (row.summary, row.import_status, row.last_checked) if str(part or "").strip()]
    return " · ".join(parts)


def _secret_rows_html(
    rows: Sequence[SystemSecretInventoryRow | Mapping[str, object]],
    *,
    filters: SystemSecretFilterState | Mapping[str, object] | None,
    pagination: SystemPaginationState | Mapping[str, object] | None,
) -> str:
    if not rows and not filters and not pagination:
        return ""
    body = ""
    cards = ""
    for raw_row in rows:
        row = _coerce(raw_row, SystemSecretInventoryRow, {"key": "secret"})
        tone = _tone(row.tone or row.status)
        label = row.label or row.key
        name = f'<a href="{escape(row.href, quote=True)}">{escape(str(label))}</a>' if row.href else escape(str(label))
        present = _state_label(row.present, true_label="present", false_label="missing")
        active = _state_label(row.active, true_label="active", false_label="inactive")
        summary = _secret_inventory_summary(row)
        body += (
            f'<tr class="pc-dashboard-tone-{tone}"><td>{name}</td><td>{escape(str(row.section))}</td>'
            f'<td>{escape(str(row.source))}</td><td>{escape(str(row.status))}</td><td>{escape(str(row.value_kind))}</td>'
            f'<td>{escape(present)}</td><td>{escape(active)}</td><td>{escape(str(row.import_status))}</td>'
            f'<td>{escape(str(row.last_checked))}</td><td>{escape(summary)}{_badges_html(row.badges)}{_actions_html(row.actions)}</td></tr>'
        )
        cards += (
            f'<article class="pc-system-compact-card pc-dashboard-tone-{tone}">'
            f'<div class="pc-system-card-head"><strong>{name}</strong><span class="pc-surface-status pc-dashboard-tone-{tone}">{escape(str(row.status))}</span></div>'
            '<dl>'
            f'<div><dt>Section</dt><dd>{escape(str(row.section))}</dd></div>'
            f'<div><dt>Source</dt><dd>{escape(str(row.source))}</dd></div>'
            f'<div><dt>Kind</dt><dd>{escape(str(row.value_kind))}</dd></div>'
            f'<div><dt>Present</dt><dd>{escape(present)}</dd></div>'
            f'<div><dt>Active</dt><dd>{escape(active)}</dd></div>'
            f'<div><dt>Checked</dt><dd>{escape(str(row.last_checked))}</dd></div>'
            '</dl>'
            f'<p>{escape(summary)}</p>{_badges_html(row.badges)}{_actions_html(row.actions)}'
            '</article>'
        )
    if not body:
        body = '<tr><td colspan="10">No secret rows matched.</td></tr>'
    table = (
        '<div class="pc-system-table-wrap is-compactable"><table class="pc-system-table">'
        '<thead><tr><th>Secret</th><th>Section</th><th>Source</th><th>Status</th><th>Kind</th><th>Present</th><th>Active</th><th>Import</th><th>Checked</th><th>Summary</th></tr></thead>'
        f'<tbody>{body}</tbody></table></div>'
    )
    cards_html = f'<div class="pc-system-mobile-cards">{cards}</div>' if cards else ""
    return (
        '<section class="pc-system-section"><div class="pc-dashboard-section-title">Secret Rows</div>'
        f'{_secret_filter_summary_html(filters)}{table}{cards_html}{_pagination_html(pagination, "Secret rows pagination")}</section>'
    )


def _readiness_html(rows: Sequence[SystemReadinessProbe | Mapping[str, object]]) -> str:
    if not rows:
        return ""
    body = ""
    for raw_row in rows:
        row = _coerce(raw_row, SystemReadinessProbe, {"key": "probe", "label": "Probe"})
        tone = _tone(row.tone or row.status)
        required = '<span class="pc-system-required">required</span>' if row.required else '<span>optional</span>'
        body += (
            f'<article class="pc-system-row pc-system-probe pc-dashboard-tone-{tone}">'
            '<div class="pc-system-row-main">'
            f'<div class="pc-system-row-title"><strong>{escape(str(row.label))}</strong><span class="pc-surface-status pc-dashboard-tone-{tone}">{escape(str(row.status))}</span></div>'
            f'<p>{escape(str(row.summary or row.detail))}</p><div class="pc-system-row-meta">{required}<time>{escape(str(row.checked_at))}</time>{_badges_html(row.badges)}</div></div>'
            f'{_actions_html(row.actions)}</article>'
        )
    return f'<section class="pc-system-section"><div class="pc-dashboard-section-title">Readiness</div><div class="pc-system-list">{body}</div></section>'


def _audit_html(
    rows: Sequence[SystemAuditRow | Mapping[str, object]],
    *,
    filters: SystemAuditFilterState | Mapping[str, object] | None,
    pagination: SystemPaginationState | Mapping[str, object] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows and not filters and not pagination:
        return ""
    body = ""
    cards = ""
    for raw_row in rows:
        row = _coerce(raw_row, SystemAuditRow, {"key": "audit", "label": "Audit"})
        tone = _tone(row.tone or row.status)
        summary = _private_text(row.summary or row.detail, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
        href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        label = f'<a href="{escape(href, quote=True)}">{escape(str(row.label))}</a>' if href else escape(str(row.label))
        body += (
            f'<tr class="pc-dashboard-tone-{tone}{private}"><td>{label}</td><td>{escape(str(row.action))}</td>'
            f'<td>{escape(str(row.actor))}</td><td>{escape(str(row.entity))}</td><td>{escape(str(row.source))}</td>'
            f'<td>{escape(str(row.status))}</td><td>{escape(str(row.timestamp))}</td>'
            f'<td>{escape(summary)}{_badges_html(row.badges)}{_actions_html(row.actions)}</td></tr>'
        )
        cards += (
            f'<article class="pc-system-compact-card pc-dashboard-tone-{tone}{private}">'
            f'<div class="pc-system-card-head"><strong>{label}</strong><span class="pc-surface-status pc-dashboard-tone-{tone}">{escape(str(row.status))}</span></div>'
            '<dl>'
            f'<div><dt>Action</dt><dd>{escape(str(row.action))}</dd></div>'
            f'<div><dt>Actor</dt><dd>{escape(str(row.actor))}</dd></div>'
            f'<div><dt>Entity</dt><dd>{escape(str(row.entity))}</dd></div>'
            f'<div><dt>Source</dt><dd>{escape(str(row.source))}</dd></div>'
            f'<div><dt>Time</dt><dd>{escape(str(row.timestamp))}</dd></div>'
            '</dl>'
            f'<p>{escape(summary)}</p>{_badges_html(row.badges)}{_actions_html(row.actions)}'
            '</article>'
        )
    if not body:
        body = '<tr><td colspan="8">No audit rows matched.</td></tr>'
    cards_html = f'<div class="pc-system-mobile-cards">{cards}</div>' if cards else ""
    return (
        '<section class="pc-system-section"><div class="pc-dashboard-section-title">Audit Events</div>'
        f'{_audit_filter_summary_html(filters)}'
        '<div class="pc-system-table-wrap is-compactable"><table class="pc-system-table">'
        '<thead><tr><th>Event</th><th>Action</th><th>Actor</th><th>Entity</th><th>Source</th><th>Status</th><th>Time</th><th>Summary</th></tr></thead>'
        f'<tbody>{body}</tbody></table></div>{cards_html}{_pagination_html(pagination, "Audit events pagination")}</section>'
    )


def render_system_health_surface(
    config: SystemHealthSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, SystemHealthSurfaceConfig)
    if not system_health_surface_feature_enabled(model, features):
        return ""
    tabs = render_status_tabs(tuple(_coerce(tab, StatusTab, {"label": "Tab"}) for tab in model.tabs), aria_label="System posture filters") if model.tabs else ""
    groups = "".join(_health_group_html(group) for group in model.health_groups)
    body = "".join(
        part
        for part in [
            tabs,
            _metrics_html(model.metrics),
            groups,
            _database_cards_html(model.databases),
            _table_html(model.tables),
            _secret_html(model.secret_coverage),
            _secret_rows_html(model.secret_rows, filters=model.secret_filters, pagination=model.secret_pagination),
            _readiness_html(model.readiness),
            _audit_html(model.audit_rows, filters=model.audit_filters, pagination=model.audit_pagination, policy=privacy_policy, context=privacy_context),
        ]
    )
    if not body:
        body = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    return (
        f'<section id="{escape(_key(model.key, "system-health"), quote=True)}" class="pc-system-health-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div>{_actions_html(model.actions)}</div>{body}</section>'
    )
