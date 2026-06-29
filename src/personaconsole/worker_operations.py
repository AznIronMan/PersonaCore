from __future__ import annotations

from html import escape
from typing import Any, Mapping, Sequence

from .controls import render_status_tabs
from .models import (
    DashboardMetric,
    SurfaceAction,
    WorkerControlActionSlot,
    WorkerDeadLetterRow,
    WorkerDryRunCandidate,
    WorkerOperationsSurfaceConfig,
    WorkerProcessEvent,
    WorkerReadinessRow,
    WorkerRollbackCandidate,
    WorkerRunTelemetryRow,
    WorkerScheduleRow,
)
from .operations import (
    _actions_html,
    _badges_html,
    _coerce,
    _panel_head,
    _private_class,
    _private_text,
    _raw_href,
    _tone,
)
from .privacy import AdminPrivacyContext, OwnerPrivateScopePolicy, feature_enabled

WORKER_OPERATIONS_FEATURE = "worker_operations"


def worker_operations_surface_feature_enabled(
    config: WorkerOperationsSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, WorkerOperationsSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or WORKER_OPERATIONS_FEATURE),
        default=True,
    )


def render_worker_operations_surface(
    config: WorkerOperationsSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, WorkerOperationsSurfaceConfig)
    if not worker_operations_surface_feature_enabled(model, features):
        return ""

    readiness = [_coerce(row, WorkerReadinessRow) for row in model.readiness]
    schedules = [_coerce(row, WorkerScheduleRow) for row in model.schedules]
    runs = [_coerce(row, WorkerRunTelemetryRow) for row in model.runs]
    dead_letters = [_coerce(row, WorkerDeadLetterRow) for row in model.dead_letters]
    rollbacks = [_coerce(row, WorkerRollbackCandidate) for row in model.rollback_candidates]
    dry_runs = [_coerce(row, WorkerDryRunCandidate) for row in model.dry_run_candidates]
    events = [_coerce(row, WorkerProcessEvent) for row in model.process_events]
    slots = [_coerce(slot, WorkerControlActionSlot) for slot in model.action_slots]

    metrics = _metrics_html(model.metrics)
    actions = _actions_html(model.actions, features)
    header_actions = f'<div class="pc-worker-ops-header-actions">{actions}</div>' if actions else ""
    status_tabs = render_status_tabs(model.status_tabs, aria_label=f"{model.title or 'Worker operations'} status")
    slot_html = _action_slots_html(slots, features=features)
    readiness_html = _readiness_section(
        model.readiness_title,
        readiness,
        features=features,
        policy=privacy_policy,
        context=privacy_context,
    )
    feed_html = _process_feed_section(
        model.process_feed_title,
        events,
        features=features,
        policy=privacy_policy,
        context=privacy_context,
    )
    schedules_html = _schedule_section(model.schedules_title, schedules, features=features)
    runs_html = _runs_section(model.runs_title, runs, features=features, policy=privacy_policy, context=privacy_context)
    dead_letters_html = _dead_letters_section(
        model.dead_letters_title,
        dead_letters,
        features=features,
        policy=privacy_policy,
        context=privacy_context,
    )
    rollback_html = _rollback_section(model.rollback_title, rollbacks, features=features)
    dry_run_html = _dry_run_section(
        model.dry_run_title,
        dry_runs,
        features=features,
        policy=privacy_policy,
        context=privacy_context,
    )
    body = (
        metrics
        + status_tabs
        + slot_html
        + readiness_html
        + feed_html
        + schedules_html
        + runs_html
        + dead_letters_html
        + rollback_html
        + dry_run_html
    )
    empty = f'<div class="pc-dashboard-empty pc-worker-ops-empty">{escape(str(model.empty_label))}</div>' if not body else ""
    return f"""
<section id="{escape(str(model.key or 'worker-operations'), quote=True)}" class="pc-worker-ops-surface pc-dashboard-panel pc-workflow-surface" data-pc-worker-operations>
  <div class="pc-dashboard-panel-head pc-worker-ops-head">
    <div class="pc-dashboard-title-group">
      <div class="pc-dashboard-section-title">{escape(str(model.title or 'Worker Operations'))}</div>
      <div class="pc-dashboard-section-meta">{escape(str(model.subtitle or ''))}</div>
    </div>
    {header_actions}
  </div>
  {body}
  {empty}
</section>
"""


def _metrics_html(metrics: Sequence[DashboardMetric | Mapping[str, object]]) -> str:
    cards = []
    for raw_metric in metrics:
        metric = _coerce(raw_metric, DashboardMetric)
        if not metric.label:
            continue
        body = (
            f'<span class="pc-dashboard-stat-label">{escape(str(metric.label))}</span>'
            f'<strong class="pc-dashboard-stat-value">{escape(str(metric.value))}</strong>'
            + (f'<small class="pc-dashboard-stat-detail">{escape(str(metric.detail))}</small>' if metric.detail else "")
        )
        cls = f"pc-dashboard-stat pc-worker-ops-metric pc-dashboard-tone-{_tone(metric.tone)}"
        href = str(metric.href or "")
        cards.append(f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>' if href else f'<div class="{cls}">{body}</div>')
    return f'<div class="pc-dashboard-stat-grid pc-worker-ops-metrics">{"".join(cards)}</div>' if cards else ""


def _action_slots_html(slots: Sequence[WorkerControlActionSlot], *, features: Mapping[str, bool] | None) -> str:
    cards = []
    for slot in slots:
        if not slot.label:
            continue
        actions = _actions_html(slot.actions, features)
        body = (
            f'<h3>{escape(str(slot.label))}</h3>'
            + (f'<p>{escape(str(slot.description))}</p>' if slot.description else "")
            + (f'<div class="pc-worker-ops-slot-body">{slot.body_html}</div>' if slot.body_html else "")
            + (f'<div class="pc-worker-ops-slot-actions">{actions}</div>' if actions else "")
        )
        cards.append(
            f'<article id="{escape(str(slot.key or slot.label), quote=True)}" class="pc-worker-ops-action-slot pc-dashboard-tone-{_tone(slot.tone)}">{body}</article>'
        )
    return f'<div class="pc-worker-ops-action-slots">{ "".join(cards) }</div>' if cards else ""


def _readiness_section(
    title: str,
    rows: Sequence[WorkerReadinessRow],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        return ""
    cards = []
    for row in rows:
        href = _row_href(row.href, row.privacy_scope, policy=policy, context=context)
        summary = _row_private_text(row.summary, row.privacy_scope, row.safe_alternate, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        actions = _row_actions(row.actions, row.privacy_scope, features=features, policy=policy, context=context)
        enabled = "enabled" if row.enabled else "disabled"
        meta = _meta_items(
            [
                ("State", row.control_state),
                ("Schedule", row.schedule_status),
                ("Next", row.next_run),
                ("Last", row.last_run),
                ("Failures", row.failures),
                ("Controls", row.pending_controls),
                ("Mode", enabled),
            ]
        )
        status = row.status or row.control_state or enabled
        title_html = _link_or_text(row.label, href)
        cards.append(
            f"""
<article class="pc-worker-readiness-card pc-dashboard-tone-{_tone(row.tone or status)}{private}">
  <div class="pc-workflow-card-head">
    <strong>{title_html}</strong>
    <span class="pc-surface-status pc-dashboard-tone-{_tone(row.tone or status)}">{escape(str(status))}</span>
  </div>
  {f'<p>{escape(summary)}</p>' if summary else ''}
  {_badges_html(row.badges)}
  {meta}
  {_actions_wrap(actions)}
</article>
"""
        )
    return _section(title, f'<div class="pc-worker-readiness-grid">{"".join(cards)}</div>')


def _process_feed_section(
    title: str,
    rows: Sequence[WorkerProcessEvent],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        return ""
    events = []
    for row in rows:
        href = _row_href(row.href, row.privacy_scope, policy=policy, context=context)
        summary = _row_private_text(row.summary, row.privacy_scope, row.safe_alternate, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        actions = _row_actions(row.actions, row.privacy_scope, features=features, policy=policy, context=context)
        events.append(
            f"""
<article class="pc-worker-process-event pc-dashboard-tone-{_tone(row.tone or row.status)}{private}">
  <span class="pc-dashboard-activity-dot" aria-hidden="true"></span>
  <div class="pc-worker-process-main">
    <div class="pc-worker-process-title">
      {_link_or_text(row.worker or row.key, href)}
      <span class="pc-surface-status pc-dashboard-tone-{_tone(row.tone or row.status)}">{escape(str(row.status or row.kind))}</span>
      {f'<time>{escape(str(row.timestamp))}</time>' if row.timestamp else ''}
    </div>
    <p>{escape(summary)}</p>
    {_meta_items([('Kind', row.kind)])}
    {_badges_html(row.badges)}
    {_actions_wrap(actions)}
  </div>
</article>
"""
        )
    return _section(title, f'<div class="pc-worker-process-feed">{"".join(events)}</div>')


def _schedule_section(title: str, rows: Sequence[WorkerScheduleRow], *, features: Mapping[str, bool] | None) -> str:
    if not rows:
        return ""
    body = "".join(
        "<tr>"
        f"<td>{_link_or_text(row.label or row.worker or row.key, row.href)}</td>"
        f'<td><span class="pc-surface-status pc-dashboard-tone-{_tone(row.tone or row.status)}">{escape(str(row.status or ("enabled" if row.enabled else "disabled")))}</span></td>'
        f"<td>{escape(str(row.cadence))}</td>"
        f"<td>{escape(str(row.next_run))}</td>"
        f"<td>{escape(str(row.last_run))}</td>"
        f"<td>{escape(str(row.detail))}{_badges_html(row.badges)}</td>"
        f"<td>{_actions_html(row.actions, features)}</td>"
        "</tr>"
        for row in rows
    )
    return _table_section(title, ("Worker", "Status", "Cadence", "Next", "Last", "Detail", "Actions"), body)


def _runs_section(
    title: str,
    rows: Sequence[WorkerRunTelemetryRow],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        return ""
    body = []
    for row in rows:
        href = _row_href(row.href, row.privacy_scope, policy=policy, context=context)
        output = _row_private_text(row.error or row.output, row.privacy_scope, row.safe_alternate, policy=policy, context=context)
        actions = _row_actions(row.actions, row.privacy_scope, features=features, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        body.append(
            f'<tr class="pc-dashboard-tone-{_tone(row.tone or row.status)}{private}">'
            f"<td>{escape(str(row.timestamp))}</td>"
            f"<td>{_link_or_text(row.worker or row.key, href)}</td>"
            f'<td><span class="pc-surface-status pc-dashboard-tone-{_tone(row.tone or row.status)}">{escape(str(row.status))}</span></td>'
            f"<td>{escape(str(row.run_kind))}</td>"
            f"<td>{escape(str(row.control_state))}</td>"
            f"<td>{escape(str(row.duration))}</td>"
            f"<td>{escape(str(row.attempts))}</td>"
            f"<td>{escape(str(output))}{_badges_html(row.badges)}</td>"
            f"<td>{actions}</td>"
            "</tr>"
        )
    return _table_section(title, ("Time", "Worker", "Status", "Kind", "Control", "Duration", "Attempts", "Output", "Actions"), "".join(body))


def _dead_letters_section(
    title: str,
    rows: Sequence[WorkerDeadLetterRow],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        return ""
    body = []
    for row in rows:
        href = _row_href(row.href, row.privacy_scope, policy=policy, context=context)
        reason = _row_private_text(row.reason, row.privacy_scope, row.safe_alternate, policy=policy, context=context)
        actions = _row_actions(row.actions, row.privacy_scope, features=features, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        body.append(
            f'<tr class="pc-dashboard-tone-{_tone(row.tone or row.status)}{private}">'
            f"<td>{escape(str(row.timestamp))}</td>"
            f"<td>{_link_or_text(row.worker or row.key, href)}</td>"
            f'<td><span class="pc-surface-status pc-dashboard-tone-{_tone(row.tone or row.status)}">{escape(str(row.status))}</span></td>'
            f"<td>{escape(str(row.source))}</td>"
            f"<td>{escape(reason)}{_badges_html(row.badges)}</td>"
            f"<td>{escape(str(row.retries))}</td>"
            f"<td>{escape(str(row.last_retry))}</td>"
            f"<td>{actions}</td>"
            "</tr>"
        )
    return _table_section(title, ("Time", "Worker", "Status", "Source", "Reason", "Retries", "Last Retry", "Actions"), "".join(body))


def _rollback_section(title: str, rows: Sequence[WorkerRollbackCandidate], *, features: Mapping[str, bool] | None) -> str:
    if not rows:
        return ""
    body = "".join(
        "<tr>"
        f"<td>{escape(str(row.timestamp))}</td>"
        f"<td>{_link_or_text(row.worker or row.key, row.href)}</td>"
        f"<td>{escape(str(row.current_state))}</td>"
        f"<td>{escape(str(row.rollback_state))}</td>"
        f"<td>{escape(str(row.prior_state))}</td>"
        f"<td>{escape(str(row.actor))}</td>"
        f"<td>{escape(str(row.audit_id))}</td>"
        f"<td>{escape(str(row.reason))}{_badges_html(row.badges)}</td>"
        f"<td>{_actions_html(row.actions, features)}</td>"
        "</tr>"
        for row in rows
    )
    return _table_section(title, ("Time", "Worker", "Current", "Rollback", "Prior", "Actor", "Audit", "Reason", "Actions"), body)


def _dry_run_section(
    title: str,
    rows: Sequence[WorkerDryRunCandidate],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not rows:
        return ""
    body = []
    for row in rows:
        href = _row_href(row.href, row.privacy_scope, policy=policy, context=context)
        summary = _row_private_text(row.summary, row.privacy_scope, row.safe_alternate, policy=policy, context=context)
        actions = _row_actions(row.actions, row.privacy_scope, features=features, policy=policy, context=context)
        private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
        body.append(
            f'<tr class="pc-dashboard-tone-{_tone(row.tone or row.status or row.decision)}{private}">'
            f"<td>{escape(str(row.timestamp))}</td>"
            f"<td>{_link_or_text(row.worker or row.key, href)}</td>"
            f"<td>{escape(str(row.proposal_type))}</td>"
            f"<td>{escape(str(row.source_kind))}</td>"
            f'<td><span class="pc-surface-status pc-dashboard-tone-{_tone(row.tone or row.status or row.decision)}">{escape(str(row.status or row.decision))}</span></td>'
            f"<td>{escape(summary)}{_badges_html(row.badges)}</td>"
            f"<td>{actions}</td>"
            "</tr>"
        )
    return _table_section(title, ("Time", "Worker", "Proposal", "Source", "Status", "Summary", "Actions"), "".join(body))


def _section(title: str, body: str) -> str:
    if not body:
        return ""
    return f'<div class="pc-workflow-subsection pc-worker-ops-section">{_panel_head(title, "")}{body}</div>'


def _table_section(title: str, headers: Sequence[str], body: str) -> str:
    head = "".join(f"<th>{escape(str(header))}</th>" for header in headers)
    return _section(
        title,
        f"""
<div class="pc-worker-ops-table-wrap">
  <table class="pc-worker-ops-table">
    <thead><tr>{head}</tr></thead>
    <tbody>{body}</tbody>
  </table>
</div>
""",
    )


def _meta_items(items: Sequence[tuple[str, object]]) -> str:
    body = "".join(
        f'<span><b>{escape(str(label))}</b> {escape(str(value))}</span>'
        for label, value in items
        if str(value if value is not None else "").strip()
    )
    return f'<div class="pc-worker-ops-meta">{body}</div>' if body else ""


def _link_or_text(label: object, href: str) -> str:
    text = escape(str(label or "worker"))
    if href:
        return f'<a href="{escape(str(href), quote=True)}">{text}</a>'
    return f"<span>{text}</span>"


def _row_private_text(
    value: object,
    privacy_scope: str,
    safe_alternate: str,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    return _private_text(
        value,
        privacy_scope=privacy_scope,
        safe_alternate=safe_alternate,
        policy=policy,
        context=context,
    )


def _row_href(
    href: str,
    privacy_scope: str,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    return _raw_href(str(href or ""), privacy_scope=privacy_scope, policy=policy, context=context)


def _row_actions(
    actions: Sequence[SurfaceAction | Mapping[str, object]],
    privacy_scope: str,
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if privacy_scope and not _raw_href("/__pc_private_probe__", privacy_scope=privacy_scope, policy=policy, context=context):
        return ""
    return _actions_html(actions, features)


def _actions_wrap(actions: str) -> str:
    return f'<div class="pc-worker-ops-actions">{actions}</div>' if actions else ""
