from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    PersonaChangeRow,
    PersonaEditorConfig,
    PersonaProfileField,
    PersonaProfileSection,
    PersonaProposalCard,
    PersonaRuleRow,
    PersonaStateField,
    PersonaTraitRow,
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

PERSONA_EDITOR_FEATURE = "persona_editor"

T = TypeVar("T")

_TONE_ALIASES = {
    "approved": "good",
    "applied": "good",
    "archived": "neutral",
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "draft": "info",
    "error": "bad",
    "failed": "bad",
    "good": "good",
    "healthy": "good",
    "held": "warn",
    "info": "info",
    "neutral": "neutral",
    "ok": "good",
    "pending": "warn",
    "pending-review": "warn",
    "proposed": "warn",
    "ready": "good",
    "rejected": "bad",
    "review": "warn",
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
    return f'<span class="pc-persona-editor-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-persona-editor-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object]) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label:
        return ""
    tone = _tone(action.tone)
    body = escape(str(action.label))
    method = str(action.method or "").strip().upper()
    title = _attrs(title=action.title)
    cls = f"pc-persona-editor-action pc-dashboard-tone-{tone}"
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{title}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(action.href, quote=True)}"{_attrs(data_method=method) if method else ""}{title}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]]) -> str:
    body = "".join(_action_html(action) for action in actions)
    return f'<div class="pc-persona-editor-actions">{body}</div>' if body else ""


def persona_editor_feature_enabled(
    config: PersonaEditorConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, PersonaEditorConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or PERSONA_EDITOR_FEATURE), default=True)


def _status_html(status: object, tone: object = "") -> str:
    if not status:
        return ""
    return f'<span class="pc-surface-status pc-dashboard-tone-{_tone(tone or status)}">{escape(str(status))}</span>'


def _text_pair_html(label: str, value: str) -> str:
    if not label and not value:
        return ""
    return f'<span><b>{escape(label)}</b>{escape(value)}</span>'


def _profile_field_html(
    raw_field: PersonaProfileField | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    field = _coerce(raw_field, PersonaProfileField, {"key": "field", "label": "Field"})
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
    href = _raw_href(field.href, privacy_scope=field.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=field.privacy_scope, policy=policy, context=context)
    body = (
        '<div class="pc-persona-editor-field-head">'
        f'<strong>{escape(str(field.label))}</strong>{_status_html(field.status, field.tone)}</div>'
        f'<div class="pc-persona-editor-value">{escape(value)}</div>'
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(field.badges)
        + _actions_html(field.actions)
    )
    cls = f"pc-persona-editor-field pc-dashboard-tone-{_tone(field.tone or field.status)}{private}"
    if href and not field.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _profile_section_html(
    raw_section: PersonaProfileSection | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    section = _coerce(raw_section, PersonaProfileSection, {"key": "profile", "title": "Profile"})
    fields_html = "".join(_profile_field_html(field, policy=policy, context=context) for field in section.fields)
    if not fields_html:
        fields_html = '<div class="pc-dashboard-empty">No profile fields configured.</div>'
    return (
        f'<section class="pc-persona-editor-section pc-dashboard-panel pc-dashboard-tone-{_tone(section.tone or section.status)}" data-persona-section="{escape(_key(section.key), quote=True)}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(section.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(section.description))}</div>'
        f'</div><div class="pc-persona-editor-section-meta">{_status_html(section.status, section.tone)}{_badges_html(section.badges)}{_actions_html(section.actions)}</div></div>'
        f'<div class="pc-persona-editor-field-grid">{fields_html}</div></section>'
    )


def _trait_html(
    raw_trait: PersonaTraitRow | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    trait = _coerce(raw_trait, PersonaTraitRow, {"key": "trait", "label": "Trait"})
    summary = _private_text(trait.summary or trait.detail, privacy_scope=trait.privacy_scope, safe_alternate=trait.safe_alternate, policy=policy, context=context)
    href = _raw_href(trait.href, privacy_scope=trait.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=trait.privacy_scope, policy=policy, context=context)
    meta = (
        _text_pair_html("Value", str(trait.value))
        + _text_pair_html("Intensity", str(trait.intensity))
        + _text_pair_html("Status", str(trait.status))
    )
    body = (
        '<div class="pc-persona-editor-row-main">'
        f'<div class="pc-persona-editor-row-title"><strong>{escape(str(trait.label))}</strong>{_status_html(trait.status, trait.tone)}</div>'
        + (f'<p>{escape(summary)}</p>' if summary else "")
        + (f'<div class="pc-persona-editor-row-meta">{meta}</div>' if meta else "")
        + _badges_html(trait.badges)
        + "</div>"
        + _actions_html(trait.actions)
    )
    cls = f"pc-persona-editor-row pc-persona-editor-trait pc-dashboard-tone-{_tone(trait.tone or trait.status)}{private}"
    if href and not trait.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _rule_html(
    raw_rule: PersonaRuleRow | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    rule = _coerce(raw_rule, PersonaRuleRow, {"key": "rule", "label": "Rule"})
    rule_text = _private_text(rule.rule or rule.summary, privacy_scope=rule.privacy_scope, safe_alternate=rule.safe_alternate, policy=policy, context=context)
    href = _raw_href(rule.href, privacy_scope=rule.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=rule.privacy_scope, policy=policy, context=context)
    meta = (
        _text_pair_html("Category", str(rule.category))
        + _text_pair_html("Priority", str(rule.priority))
        + _text_pair_html("Status", str(rule.status))
    )
    body = (
        '<div class="pc-persona-editor-row-main">'
        f'<div class="pc-persona-editor-row-title"><strong>{escape(str(rule.label))}</strong>{_status_html(rule.status, rule.tone)}</div>'
        + (f'<p>{escape(rule_text)}</p>' if rule_text else "")
        + (f'<div class="pc-persona-editor-row-meta">{meta}</div>' if meta else "")
        + _badges_html(rule.badges)
        + "</div>"
        + _actions_html(rule.actions)
    )
    cls = f"pc-persona-editor-row pc-persona-editor-rule pc-dashboard-tone-{_tone(rule.tone or rule.status)}{private}"
    if href and not rule.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _state_value(field: PersonaStateField, *, pending: bool = False) -> str:
    if pending:
        if field.secret:
            return str(field.pending_display_value or ("pending update" if field.pending_value not in ("", None) else ""))
        return str(field.pending_display_value or field.pending_value or "")
    if field.secret:
        if field.display_value:
            return str(field.display_value)
        return "configured" if bool(field.value) else "not configured"
    if isinstance(field.value, bool):
        return "on" if field.value else "off"
    return str(field.display_value or field.value or "")


def _state_field_html(
    raw_field: PersonaStateField | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    field = _coerce(raw_field, PersonaStateField, {"key": "state", "label": "State"})
    value = _state_value(field)
    pending = _state_value(field, pending=True)
    if field.privacy_scope and not field.secret:
        value = _private_text(value, privacy_scope=field.privacy_scope, safe_alternate=field.safe_alternate, policy=policy, context=context)
        pending = _private_text(pending, privacy_scope=field.privacy_scope, safe_alternate=field.safe_alternate, policy=policy, context=context)
    detail = _private_text(field.detail, privacy_scope=field.privacy_scope, safe_alternate="", policy=policy, context=context)
    private = _private_class(privacy_scope=field.privacy_scope, policy=policy, context=context)
    changed = '<span class="pc-persona-editor-changed">changed</span>' if field.changed else ""
    pending_html = f'<span class="pc-persona-editor-pending"><b>Pending</b>{escape(pending)}</span>' if pending else ""
    return (
        f'<article class="pc-persona-editor-field pc-persona-editor-state pc-dashboard-tone-{_tone(field.tone or field.status)}{private}">'
        '<div class="pc-persona-editor-field-head">'
        f'<strong>{escape(str(field.label))}</strong>{_status_html(field.status, field.tone)}</div>'
        f'<div class="pc-persona-editor-value">{escape(value)}</div>'
        f'<div class="pc-persona-editor-row-meta"><span><b>Type</b>{escape(str(field.field_type))}</span>{changed}{pending_html}</div>'
        + (f'<p>{escape(detail)}</p>' if detail else "")
        + _badges_html(field.badges)
        + _actions_html(field.actions)
        + "</article>"
    )


def _change_html(
    raw_change: PersonaChangeRow | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    change = _coerce(raw_change, PersonaChangeRow, {"key": "change", "label": "Change"})
    before = _private_text(change.before, privacy_scope=change.privacy_scope, safe_alternate=change.safe_alternate, policy=policy, context=context)
    after = _private_text(change.after, privacy_scope=change.privacy_scope, safe_alternate=change.safe_alternate, policy=policy, context=context)
    private = _private_class(privacy_scope=change.privacy_scope, policy=policy, context=context)
    meta = (
        (f'<span>{escape(str(change.actor))}</span>' if change.actor else "")
        + (f'<time>{escape(str(change.timestamp))}</time>' if change.timestamp else "")
        + _badges_html(change.badges)
    )
    return (
        f'<article class="pc-persona-editor-change pc-dashboard-tone-{_tone(change.tone or change.status)}{private}">'
        '<div class="pc-persona-editor-row-title">'
        f'<strong>{escape(str(change.label))}</strong>{_status_html(change.status, change.tone)}</div>'
        f'<div class="pc-persona-editor-diff"><del>{escape(before)}</del><ins>{escape(after)}</ins></div>'
        + (f'<div class="pc-persona-editor-row-meta">{meta}</div>' if meta else "")
        + "</article>"
    )


def _proposal_html(
    raw_proposal: PersonaProposalCard | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    proposal = _coerce(raw_proposal, PersonaProposalCard, {"key": "proposal", "title": "Proposal"})
    summary = _private_text(proposal.summary, privacy_scope=proposal.privacy_scope, safe_alternate=proposal.safe_alternate, policy=policy, context=context)
    href = _raw_href(proposal.href, privacy_scope=proposal.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=proposal.privacy_scope, policy=policy, context=context)
    changes = "".join(_change_html(change, policy=policy, context=context) for change in proposal.changes)
    meta = (
        _text_pair_html("Source", str(proposal.source))
        + _text_pair_html("Target", str(proposal.target))
        + _text_pair_html("By", str(proposal.proposed_by))
        + _text_pair_html("Updated", str(proposal.updated))
    )
    body = (
        '<div class="pc-persona-editor-card-head">'
        f'<strong>{escape(str(proposal.title))}</strong>{_status_html(proposal.status, proposal.tone)}</div>'
        + (f'<p>{escape(summary)}</p>' if summary else "")
        + (f'<div class="pc-persona-editor-row-meta">{meta}</div>' if meta else "")
        + _badges_html(proposal.badges)
        + (f'<div class="pc-persona-editor-change-list">{changes}</div>' if changes else "")
        + _actions_html(proposal.actions)
    )
    cls = f"pc-persona-editor-card pc-persona-editor-proposal pc-dashboard-tone-{_tone(proposal.tone or proposal.status)}{private}"
    if href and not proposal.actions:
        return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>'
    return f'<article class="{cls}">{body}</article>'


def _section(title: str, body: str, class_name: str = "") -> str:
    if not body:
        return ""
    extra = f" {class_name}" if class_name else ""
    return f'<section class="pc-persona-editor-section{extra}"><div class="pc-dashboard-section-title">{escape(title)}</div>{body}</section>'


def render_persona_editor(
    config: PersonaEditorConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, PersonaEditorConfig)
    if not persona_editor_feature_enabled(model, features):
        return ""
    tabs = render_status_tabs(tuple(_coerce(tab, StatusTab, {"label": "Tab"}) for tab in model.tabs), aria_label="Persona editor filters") if model.tabs else ""
    profile = "".join(_profile_section_html(section, policy=privacy_policy, context=privacy_context) for section in model.profile_sections)
    traits = "".join(_trait_html(trait, policy=privacy_policy, context=privacy_context) for trait in model.traits)
    rules = "".join(_rule_html(rule, policy=privacy_policy, context=privacy_context) for rule in model.rules)
    state = "".join(_state_field_html(field, policy=privacy_policy, context=privacy_context) for field in model.state_fields)
    proposals = "".join(_proposal_html(proposal, policy=privacy_policy, context=privacy_context) for proposal in model.proposals)
    history = "".join(_change_html(change, policy=privacy_policy, context=privacy_context) for change in model.history)
    body = "".join(
        part
        for part in [
            tabs,
            profile,
            _section("Traits", f'<div class="pc-persona-editor-list">{traits}</div>' if traits else ""),
            _section("Rules", f'<div class="pc-persona-editor-list">{rules}</div>' if rules else ""),
            _section("Mutable State", f'<div class="pc-persona-editor-field-grid">{state}</div>' if state else ""),
            _section("Proposals", f'<div class="pc-persona-editor-card-grid">{proposals}</div>' if proposals else ""),
            _section("Change History", f'<div class="pc-persona-editor-change-list">{history}</div>' if history else ""),
        ]
    )
    if not body:
        body = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    return (
        f'<section id="{escape(_key(model.key, "persona-editor"), quote=True)}" class="pc-persona-editor-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div>{_actions_html(model.actions)}</div>{body}</section>'
    )
