from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    CommandIntakeActionSlot,
    CommandCandidateRow,
    CommandConfirmationStep,
    CommandHistoryRow,
    CommandIntakeSurfaceConfig,
    CommandParsedField,
    CommandQueueRow,
    CommandRiskRow,
    DashboardMetric,
    StatusTab,
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

COMMAND_INTAKE_FEATURE = "command_intake"

T = TypeVar("T")

_TONE_ALIASES = {
    "allowed": "good",
    "applied": "good",
    "bad": "bad",
    "blocked": "bad",
    "cancelled": "neutral",
    "complete": "good",
    "completed": "good",
    "confirmed": "good",
    "danger": "bad",
    "denied": "bad",
    "error": "bad",
    "failed": "bad",
    "good": "good",
    "held": "warn",
    "high": "bad",
    "info": "info",
    "low": "good",
    "medium": "warn",
    "missing": "warn",
    "needs-confirmation": "warn",
    "neutral": "neutral",
    "ok": "good",
    "parsed": "good",
    "pending": "warn",
    "preview": "info",
    "queued": "info",
    "ready": "good",
    "rejected": "bad",
    "review": "warn",
    "running": "info",
    "safe": "good",
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
    return f'<span class="pc-command-intake-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-command-intake-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], features: Mapping[str, bool] | None) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label or (action.feature and not feature_enabled(features, action.feature, default=True)):
        return ""
    body = escape(str(action.label))
    method = str(action.method or "").strip().upper()
    cls = f"pc-command-intake-action pc-dashboard-tone-{_tone(action.tone)}"
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{_attrs(title=action.title)}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(action.href, quote=True)}"{_attrs(data_method=method) if method else ""}{_attrs(title=action.title)}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], features: Mapping[str, bool] | None) -> str:
    body = "".join(_action_html(action, features) for action in actions)
    return f'<div class="pc-command-intake-actions">{body}</div>' if body else ""


def _action_slot_html(
    raw_slot: CommandIntakeActionSlot | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    slot = _coerce(raw_slot, CommandIntakeActionSlot, {"key": "action-slot", "label": "Action"})
    if not slot.label:
        return ""
    body_text = _private_text(
        slot.body,
        privacy_scope=slot.privacy_scope,
        safe_alternate=slot.safe_alternate,
        policy=policy,
        context=context,
    )
    body = f'<p>{escape(str(body_text))}</p>' if body_text else ""
    body += str(slot.body_html or "")
    badges = _badges_html(slot.badges)
    actions = _actions_html(slot.actions, features)
    action_html = f'<div class="pc-command-intake-slot-actions">{actions}</div>' if actions else ""
    private = _private_class(privacy_scope=slot.privacy_scope, policy=policy, context=context)
    slot_key = _key(slot.key or slot.label, "command-intake-slot")
    description = escape(str(slot.description or ""))
    return (
        f'<section id="{escape(slot_key, quote=True)}" data-command-slot="{escape(slot_key, quote=True)}" '
        f'class="pc-command-intake-action-slot pc-dashboard-panel pc-dashboard-tone-{_tone(slot.tone)}{private}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(slot.label))}</div>'
        + (f'<div class="pc-dashboard-section-meta">{description}</div>' if description else "")
        + f'</div>{badges}</div>'
        f'<div class="pc-command-intake-slot-body">{body}</div>{action_html}</section>'
    )


def _action_slots_html(
    slots: Sequence[CommandIntakeActionSlot | Mapping[str, object]],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    body = "".join(
        _action_slot_html(slot, features=features, policy=policy, context=context)
        for slot in slots
    )
    return f'<div class="pc-command-intake-action-slots">{body}</div>' if body else ""


def command_intake_feature_enabled(
    config: CommandIntakeSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, CommandIntakeSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or COMMAND_INTAKE_FEATURE), default=True)


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
    cls = f"pc-command-intake-metric pc-dashboard-tone-{_tone(metric.tone)}"
    if metric.href:
        return f'<a class="{cls}" href="{escape(str(metric.href), quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _facts_html(pairs: Sequence[tuple[str, object]]) -> str:
    parts = [
        f'<span><b>{escape(label)}</b>{escape(str(value))}</span>'
        for label, value in pairs
        if value not in ("", None)
    ]
    return f'<div class="pc-command-intake-facts">{"".join(parts)}</div>' if parts else ""


def _field_html(
    raw_field: CommandParsedField | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    field = _coerce(raw_field, CommandParsedField, {"key": "field", "label": "Field"})
    value = _private_text(
        field.value,
        privacy_scope=field.privacy_scope,
        safe_alternate=field.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        field.detail,
        privacy_scope=field.privacy_scope,
        safe_alternate="",
        policy=policy,
        context=context,
    )
    private = _private_class(privacy_scope=field.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-command-intake-row-title">'
        f'<strong>{escape(str(field.label))}</strong>{_status_html(field.status, field.tone)}</div>'
        f'<div class="pc-command-intake-value">{escape(value)}</div>'
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(field.badges)
    )
    return f'<article class="pc-command-intake-field pc-dashboard-tone-{_tone(field.tone or field.status)}{private}" data-command-field="{escape(_key(field.key), quote=True)}">{body}</article>'


def _candidate_html(
    raw_row: CommandCandidateRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, CommandCandidateRow, {"key": "candidate", "label": "Candidate"})
    summary = _private_text(
        row.summary,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        row.detail,
        privacy_scope=row.privacy_scope,
        safe_alternate="",
        policy=policy,
        context=context,
    )
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-command-intake-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}</div>'
        + _facts_html((("Kind", row.kind), ("Score", row.score)))
        + (f'<p>{escape(summary)}</p>' if summary else "")
        + (f'<small>{escape(detail)}</small>' if detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-command-intake-row pc-dashboard-tone-{_tone(row.tone or row.status)}{private}"
    if href and not row.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _risk_html(
    raw_row: CommandRiskRow | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, CommandRiskRow, {"key": "risk", "label": "Risk"})
    summary = _private_text(
        row.summary,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        row.detail,
        privacy_scope=row.privacy_scope,
        safe_alternate="",
        policy=policy,
        context=context,
    )
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    tone = _tone(row.tone or row.severity or row.status)
    body = (
        '<div class="pc-command-intake-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.severity or row.status, tone)}</div>'
        + (f'<p>{escape(summary)}</p>' if summary else "")
        + (f'<small>{escape(detail)}</small>' if detail else "")
        + _badges_html(row.badges)
    )
    return f'<article class="pc-command-intake-row pc-command-intake-risk pc-dashboard-tone-{tone}{private}">{body}</article>'


def _confirmation_html(
    raw_step: CommandConfirmationStep | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
) -> str:
    step = _coerce(raw_step, CommandConfirmationStep, {"key": "step", "label": "Step"})
    tone = _tone(step.tone or step.status)
    required = "required" if step.required else "optional"
    completed = "complete" if step.completed else "open"
    body = (
        '<div class="pc-command-intake-row-title">'
        f'<strong>{escape(str(step.label))}</strong>{_status_html(step.status, tone)}</div>'
        + _facts_html((("Scope", required), ("State", completed)))
        + (f'<p>{escape(str(step.detail))}</p>' if step.detail else "")
        + _badges_html(step.badges)
        + _actions_html(step.actions, features)
    )
    cls = f"pc-command-intake-row pc-command-intake-confirmation pc-dashboard-tone-{tone}"
    if step.href and not step.actions:
        return f'<a class="{cls}" href="{escape(step.href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _queue_html(
    raw_row: CommandQueueRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, CommandQueueRow, {"key": "queued", "label": "Queued command"})
    command = _private_text(
        row.command,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        row.detail,
        privacy_scope=row.privacy_scope,
        safe_alternate="",
        policy=policy,
        context=context,
    )
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-command-intake-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}</div>'
        f'<code>{escape(command)}</code>'
        + _facts_html((("Actor", row.actor), ("Target", row.target), ("Queued", row.timestamp)))
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-command-intake-row pc-command-intake-queue-row pc-dashboard-tone-{_tone(row.tone or row.status)}{private}"
    if href and not row.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _history_html(
    raw_row: CommandHistoryRow | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    row = _coerce(raw_row, CommandHistoryRow, {"key": "history", "label": "History"})
    command = _private_text(
        row.command,
        privacy_scope=row.privacy_scope,
        safe_alternate=row.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        row.detail,
        privacy_scope=row.privacy_scope,
        safe_alternate="",
        policy=policy,
        context=context,
    )
    href = _raw_href(row.href, privacy_scope=row.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=row.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-command-intake-row-title">'
        f'<strong>{escape(str(row.label))}</strong>{_status_html(row.result, row.tone or row.result)}</div>'
        f'<code>{escape(command)}</code>'
        + _facts_html((("Actor", row.actor), ("Target", row.target), ("When", row.timestamp), ("Duration", row.duration)))
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(row.badges)
        + _actions_html(row.actions, features)
    )
    cls = f"pc-command-intake-row pc-command-intake-history-row pc-dashboard-tone-{_tone(row.tone or row.result)}{private}"
    if href and not row.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _section_html(title: str, body: str, *, subtitle: str = "", empty: str = "") -> str:
    if not body and not empty:
        return ""
    content = body or f'<p class="pc-dashboard-empty">{escape(empty)}</p>'
    return (
        '<section class="pc-command-intake-section pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        + (f'<div class="pc-dashboard-section-meta">{escape(subtitle)}</div>' if subtitle else "")
        + f'</div></div><div class="pc-command-intake-list">{content}</div></section>'
    )


def render_command_intake_surface(
    config: CommandIntakeSurfaceConfig | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    model = _coerce(config, CommandIntakeSurfaceConfig)
    if not command_intake_feature_enabled(model, features):
        return ""

    title = escape(str(model.title or "Command Intake"))
    subtitle = escape(str(model.subtitle or ""))
    key = _key(model.key, "command-intake")
    actions = _actions_html(model.actions, features)
    tabs = render_status_tabs(model.tabs) if model.tabs else ""
    metrics = "".join(_metric_html(metric) for metric in model.metrics)
    metrics_html = f'<div class="pc-command-intake-metrics">{metrics}</div>' if metrics else ""
    action_slots = _action_slots_html(
        model.action_slots,
        features=features,
        policy=privacy_policy,
        context=privacy_context,
    )

    prompt = _private_text(
        model.input_value,
        privacy_scope=model.input_privacy_scope,
        safe_alternate=model.input_safe_alternate,
        policy=privacy_policy,
        context=privacy_context,
    )
    input_private = _private_class(
        privacy_scope=model.input_privacy_scope,
        policy=privacy_policy,
        context=privacy_context,
    )
    form_html = ""
    if model.show_form:
        method = str(model.form_method or "post").strip().lower()
        form_method = "get" if method == "get" else "post"
        queue_method = str(model.queue_method or "").strip().upper()
        queue_action = ""
        if model.queue_label:
            if model.queue_href:
                queue_action = (
                    f'<a class="pc-command-intake-action pc-dashboard-tone-good" href="{escape(model.queue_href, quote=True)}"'
                    f'{_attrs(data_method=queue_method) if queue_method else ""}>{escape(model.queue_label)}</a>'
                )
            else:
                queue_action = f'<span class="pc-command-intake-action pc-dashboard-tone-neutral is-disabled" aria-disabled="true">{escape(model.queue_label)}</span>'
        form_actions = (
            '<div class="pc-command-intake-form-actions">'
            f'<button type="submit" class="pc-command-intake-submit">{escape(str(model.submit_label or "Preview"))}</button>'
            f'{queue_action}</div>'
        )
        form_html = (
            f'<form class="pc-command-intake-form pc-dashboard-panel{input_private}" method="{escape(form_method)}"'
            f'{_attrs(action=model.form_action)} data-pc-command-intake>'
            '<div class="pc-dashboard-panel-head"><div>'
            f'<label class="pc-dashboard-section-title" for="pc-command-input-{escape(key, quote=True)}">{escape(str(model.input_label or "Command"))}</label>'
            f'<div class="pc-dashboard-section-meta">{escape(str(model.input_placeholder or ""))}</div>'
            '</div></div>'
            f'<textarea id="pc-command-input-{escape(key, quote=True)}" name="{escape(str(model.input_name or "command"), quote=True)}" rows="5" placeholder="{escape(str(model.input_placeholder or ""), quote=True)}">{escape(prompt)}</textarea>'
            f'{form_actions}</form>'
        )

    parsed = "".join(
        _field_html(field, policy=privacy_policy, context=privacy_context)
        for field in model.parsed_fields
    )
    candidate_rows = "".join(
        _candidate_html(row, features=features, policy=privacy_policy, context=privacy_context)
        for row in model.candidates
    )
    risk_rows = "".join(
        _risk_html(row, policy=privacy_policy, context=privacy_context)
        for row in model.risks
    )
    confirmations = "".join(_confirmation_html(step, features=features) for step in model.confirmations)
    queue = "".join(
        _queue_html(row, features=features, policy=privacy_policy, context=privacy_context)
        for row in model.queue
    )
    history = "".join(
        _history_html(row, features=features, policy=privacy_policy, context=privacy_context)
        for row in model.history
    )

    has_content = any((parsed, candidate_rows, risk_rows, confirmations, queue, history, metrics_html, tabs, actions, action_slots))
    empty = "" if has_content else f'<p class="pc-dashboard-empty">{escape(str(model.empty_label))}</p>'

    body = (
        f'<section id="{escape(key, quote=True)}" class="pc-command-intake-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{title}</div>'
        + (f'<div class="pc-dashboard-section-meta">{subtitle}</div>' if subtitle else "")
        + f'</div>{actions}</div>'
        f'{tabs}{metrics_html}{form_html}{action_slots}{empty}'
        + _section_html("Parsed Preview", parsed, subtitle="Consumer-supplied command interpretation")
        + _section_html("Candidates", candidate_rows, subtitle="Possible targets or records")
        + _section_html("Risks", risk_rows, subtitle="Consumer-owned policy and safety checks")
        + _section_html("Confirmations", confirmations, subtitle="Required operator gates")
        + _section_html("Queue", queue, subtitle="Runtime-owned queued commands")
        + _section_html("History", history, subtitle="Recent sanitized command outcomes")
        + "</section>"
    )
    return body


__all__ = [
    "COMMAND_INTAKE_FEATURE",
    "command_intake_feature_enabled",
    "render_command_intake_surface",
]
