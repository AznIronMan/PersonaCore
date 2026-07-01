from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    PublicProfileField,
    PublicProfileHistoryRow,
    PublicProfileMediaItem,
    PublicProfilePreview,
    PublicProfileReadinessCheck,
    PublicProfileSection,
    PublicProfileSurfaceConfig,
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

PUBLIC_PROFILE_FEATURE = "public_profile"

T = TypeVar("T")

_TONE_ALIASES = {
    "approved": "good",
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "draft": "info",
    "error": "bad",
    "failed": "bad",
    "good": "good",
    "healthy": "good",
    "hidden": "neutral",
    "info": "info",
    "invalid": "bad",
    "live": "good",
    "missing": "bad",
    "neutral": "neutral",
    "ok": "good",
    "pending": "warn",
    "published": "good",
    "ready": "good",
    "stale": "warn",
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


def _coerce(value: T | Mapping[str, object] | None, cls: type[T], defaults: Mapping[str, Any] | None = None) -> T:
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


def _is_private_redacted(
    *,
    privacy_scope: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> bool:
    return bool(_private_class(privacy_scope=privacy_scope, policy=policy, context=context))


def _badge_html(raw_badge: SurfaceBadge | Mapping[str, object] | str) -> str:
    badge = SurfaceBadge(str(raw_badge)) if isinstance(raw_badge, str) else _coerce(raw_badge, SurfaceBadge)
    if not badge.label:
        return ""
    return f'<span class="pc-public-profile-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-public-profile-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object]) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label:
        return ""
    body = escape(str(action.label))
    method = str(action.method or "").strip().upper()
    cls = f"pc-public-profile-action pc-dashboard-tone-{_tone(action.tone)}"
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="{cls} is-disabled"{_attrs(title=action.title)}{disabled}>{body}</span>'
    return f'<a class="{cls}" href="{escape(str(action.href), quote=True)}"{_attrs(data_method=method) if method else ""}{_attrs(title=action.title)}>{body}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]]) -> str:
    body = "".join(_action_html(action) for action in actions)
    return f'<div class="pc-public-profile-actions">{body}</div>' if body else ""


def public_profile_feature_enabled(
    config: PublicProfileSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, PublicProfileSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or PUBLIC_PROFILE_FEATURE), default=True)


def _status_html(status: object, tone: object = "") -> str:
    if not status:
        return ""
    return f'<span class="pc-surface-status pc-dashboard-tone-{_tone(tone or status)}">{escape(str(status))}</span>'


def _input_type(value: str) -> str:
    kind = _key(value, "text")
    return kind if kind in {"color", "date", "email", "number", "tel", "text", "url"} else "text"


def _field_html(
    raw_field: PublicProfileField | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    field = _coerce(raw_field, PublicProfileField, {"key": "field", "label": "Field"})
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
    redacted = _is_private_redacted(privacy_scope=field.privacy_scope, policy=policy, context=context)
    disabled = field.disabled or redacted
    name = field.input_name or field.key
    input_attrs = _attrs(
        name=name,
        placeholder=field.placeholder,
        required=field.required,
        disabled=disabled,
        readonly=field.readonly,
        aria_required="true" if field.required else "",
    )
    if field.multiline:
        rows = max(1, min(int(field.rows or 3), 20))
        control = f'<textarea class="pc-public-profile-input" rows="{rows}"{input_attrs}>{escape(value)}</textarea>'
    else:
        control = (
            f'<input class="pc-public-profile-input" type="{_input_type(field.input_type)}" '
            f'value="{escape(value, quote=True)}"{input_attrs}>'
        )
    return (
        f'<label class="pc-public-profile-field pc-dashboard-tone-{_tone(field.tone or field.status)}{" is-private" if redacted else ""}">'
        '<span class="pc-public-profile-field-head">'
        f'<strong>{escape(str(field.label))}</strong>{_status_html(field.status, field.tone)}</span>'
        f"{control}"
        + (f'<small>{escape(detail)}</small>' if detail else "")
        + _badges_html(field.badges)
        + _actions_html(field.actions)
        + "</label>"
    )


def _section_html(
    raw_section: PublicProfileSection | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    section = _coerce(raw_section, PublicProfileSection, {"key": "section", "title": "Profile Section"})
    fields = "".join(_field_html(field, policy=policy, context=context) for field in section.fields)
    if not fields:
        fields = '<div class="pc-dashboard-empty">No public profile fields configured.</div>'
    return (
        f'<section class="pc-public-profile-section pc-dashboard-tone-{_tone(section.tone or section.status)}" data-public-profile-section="{escape(_key(section.key), quote=True)}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(section.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(section.description))}</div>'
        f'</div>{_status_html(section.status, section.tone)}</div>'
        + _badges_html(section.badges)
        + f'<div class="pc-public-profile-fields">{fields}</div>'
        + _actions_html(section.actions)
        + "</section>"
    )


def _preview_html(
    raw_preview: PublicProfilePreview | Mapping[str, object] | None,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not raw_preview:
        return ""
    preview = _coerce(raw_preview, PublicProfilePreview)
    body = _private_text(
        preview.body,
        privacy_scope=preview.privacy_scope,
        safe_alternate=preview.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(preview.href, privacy_scope=preview.privacy_scope, policy=policy, context=context)
    image = _raw_href(preview.image_url, privacy_scope=preview.privacy_scope, policy=policy, context=context)
    image_html = f'<img src="{escape(image, quote=True)}" alt="">' if image else ""
    return (
        '<section class="pc-public-profile-preview pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(preview.title or "Profile preview"))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(preview.subtitle))}</div>'
        f'</div>{_status_html(preview.status, preview.tone)}</div>'
        f'{image_html}<p>{escape(body)}</p>'
        + _badges_html(preview.badges)
        + _actions_html(preview.actions)
        + (f'<a class="pc-public-profile-preview-link" href="{escape(href, quote=True)}">Open preview</a>' if href else "")
        + "</section>"
    )


def _readiness_html(rows: Sequence[PublicProfileReadinessCheck | Mapping[str, object]]) -> str:
    body = ""
    for raw_row in rows:
        row = _coerce(raw_row, PublicProfileReadinessCheck, {"key": "check", "label": "Readiness check"})
        required = '<span class="pc-public-profile-badge pc-dashboard-tone-warn">required</span>' if row.required else ""
        href = f'<a class="pc-public-profile-row-link" href="{escape(str(row.href), quote=True)}">Open</a>' if row.href else ""
        body += (
            f'<article class="pc-public-profile-row pc-dashboard-tone-{_tone(row.tone or row.status)}">'
            '<div class="pc-public-profile-row-main">'
            '<div class="pc-public-profile-row-title">'
            f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}{required}</div>'
            + (f'<p>{escape(str(row.detail))}</p>' if row.detail else "")
            + _badges_html(row.badges)
            + "</div>"
            + href
            + _actions_html(row.actions)
            + "</article>"
        )
    return f'<section class="pc-public-profile-readiness"><div class="pc-dashboard-section-title">Readiness</div>{body}</section>' if body else ""


def _media_html(
    rows: Sequence[PublicProfileMediaItem | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    body = ""
    for raw_row in rows:
        row = _coerce(raw_row, PublicProfileMediaItem, {"key": "media", "label": "Media"})
        detail = _private_text(row.detail, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
        url = _raw_href(row.url, privacy_scope=row.privacy_scope, policy=policy, context=context)
        thumb = f'<img src="{escape(url, quote=True)}" alt="">' if url and _key(row.kind, "image") == "image" else ""
        body += (
            f'<article class="pc-public-profile-media pc-dashboard-tone-{_tone(row.tone or row.status)}">'
            f'{thumb}<div><strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}'
            f'<p>{escape(detail)}</p>{_badges_html(row.badges)}{_actions_html(row.actions)}</div></article>'
        )
    return f'<section class="pc-public-profile-media-list"><div class="pc-dashboard-section-title">Media References</div>{body}</section>' if body else ""


def _history_html(
    rows: Sequence[PublicProfileHistoryRow | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    body = ""
    for raw_row in rows:
        row = _coerce(raw_row, PublicProfileHistoryRow, {"key": "history", "label": "History"})
        summary = _private_text(row.summary, privacy_scope=row.privacy_scope, safe_alternate=row.safe_alternate, policy=policy, context=context)
        body += (
            f'<article class="pc-public-profile-row pc-dashboard-tone-{_tone(row.tone or row.status)}">'
            '<div class="pc-public-profile-row-main">'
            f'<strong>{escape(str(row.label))}</strong>{_status_html(row.status, row.tone)}'
            f'<p>{escape(summary)}</p><small>{escape(str(row.actor))} {escape(str(row.timestamp))}</small>'
            f'{_badges_html(row.badges)}</div>{_actions_html(row.actions)}</article>'
        )
    return f'<section class="pc-public-profile-history"><div class="pc-dashboard-section-title">Change History</div>{body}</section>' if body else ""


def render_public_profile_surface(
    config: PublicProfileSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, PublicProfileSurfaceConfig)
    if not public_profile_feature_enabled(model, features):
        return ""
    preview = _preview_html(model.preview, policy=privacy_policy, context=privacy_context)
    sections = "".join(_section_html(section, policy=privacy_policy, context=privacy_context) for section in model.sections)
    readiness = _readiness_html(model.readiness)
    media = _media_html(model.media, policy=privacy_policy, context=privacy_context)
    history = _history_html(model.history, policy=privacy_policy, context=privacy_context)
    form_method = str(model.form_method or "post").strip().lower()
    editor = ""
    if sections:
        editor = (
            f'<form class="pc-public-profile-editor" method="{escape(form_method, quote=True)}" action="{escape(str(model.form_action), quote=True)}">'
            f"{sections}"
            f'<div class="pc-public-profile-submit"><button type="submit">{escape(str(model.submit_label))}</button></div>'
            "</form>"
            if model.form_action
            else f'<div class="pc-public-profile-editor">{sections}</div>'
        )
    body = preview + readiness + editor + media + history
    if not body:
        body = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    return (
        f'<section id="{escape(_key(model.key, "public-profile"), quote=True)}" class="pc-public-profile-surface pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div>{_status_html(model.status, model.status_tone)}{_actions_html(model.actions)}</div>'
        f"{body}</section>"
    )
