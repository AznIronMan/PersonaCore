from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
import json
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    BrandAssets,
    FlashBanner,
    PersonaConsoleConfig,
    SettingsChange,
    SettingsEditorConfig,
    SettingsField,
    SettingsGroup,
    SettingsOption,
    SettingsValidationMessage,
    SurfaceAction,
    SurfaceBadge,
)
from .privacy import feature_enabled

SETTINGS_EDITOR_FEATURE = "settings_editor"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "critical": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "invalid": "bad",
    "warn": "warn",
    "warning": "warn",
    "changed": "warn",
    "dirty": "warn",
    "pending": "warn",
    "restart": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "saved": "good",
    "success": "good",
    "info": "info",
    "notice": "info",
    "neutral": "neutral",
    "unknown": "neutral",
    "": "neutral",
}

_FIELD_KINDS = {
    "text",
    "textarea",
    "select",
    "boolean",
    "number",
    "secret",
    "readonly",
    "json",
    "code",
    "url",
}


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _mapped_text(data: Mapping[str, Any], key: str, default: str = "") -> str:
    if key in data:
        return str(data.get(key) or "")
    return default


def _coerce(value: T | Mapping[str, object] | str, cls: type[T], defaults: Mapping[str, Any] | None = None) -> T:
    if isinstance(value, cls):
        return value
    if cls is SettingsValidationMessage and isinstance(value, str):
        return cls(value)  # type: ignore[return-value]
    if cls is SettingsOption and isinstance(value, str):
        return cls(value, value)  # type: ignore[return-value]
    data = {**(defaults or {}), **_mapping(value)}
    allowed = {field.name for field in fields(cls)}
    data = {key: value for key, value in data.items() if key in allowed}
    return cls(**data)


def _brand_model(value: BrandAssets | PersonaConsoleConfig | Mapping[str, object] | None) -> BrandAssets:
    if isinstance(value, PersonaConsoleConfig):
        raw_assets = _mapping(value.brand_assets)
        return BrandAssets(
            name=str(raw_assets.get("name") or value.brand_name or ""),
            admin_title=str(raw_assets.get("admin_title") or ""),
            admin_subtitle=_mapped_text(raw_assets, "admin_subtitle", "admin"),
            small_logo_url=str(raw_assets.get("small_logo_url") or value.icon_url or ""),
            large_logo_url=str(raw_assets.get("large_logo_url") or ""),
            wordmark_url=str(raw_assets.get("wordmark_url") or ""),
            lockup_url=str(raw_assets.get("lockup_url") or ""),
            favicon_url=str(raw_assets.get("favicon_url") or ""),
            signature_text=str(raw_assets.get("signature_text") or ""),
            alt_text=str(raw_assets.get("alt_text") or raw_assets.get("name") or value.brand_name or ""),
            home_url=str(raw_assets.get("home_url") or value.home_url or "/"),
        )
    if isinstance(value, Mapping) and ("brand_assets" in value or "brand_name" in value or "icon_url" in value):
        raw_assets = _mapping(value.get("brand_assets"))
        brand_name = str(value.get("brand_name") or "")
        return BrandAssets(
            name=str(raw_assets.get("name") or brand_name),
            admin_title=str(raw_assets.get("admin_title") or value.get("admin_title") or ""),
            admin_subtitle=_mapped_text(raw_assets, "admin_subtitle", _mapped_text(value, "admin_subtitle", "admin")),
            small_logo_url=str(raw_assets.get("small_logo_url") or value.get("icon_url") or ""),
            large_logo_url=str(raw_assets.get("large_logo_url") or value.get("large_logo_url") or ""),
            wordmark_url=str(raw_assets.get("wordmark_url") or value.get("wordmark_url") or ""),
            lockup_url=str(raw_assets.get("lockup_url") or value.get("lockup_url") or ""),
            favicon_url=str(raw_assets.get("favicon_url") or ""),
            signature_text=str(raw_assets.get("signature_text") or ""),
            alt_text=str(raw_assets.get("alt_text") or raw_assets.get("name") or brand_name),
            home_url=str(raw_assets.get("home_url") or value.get("home_url") or "/"),
        )
    return _coerce(value, BrandAssets, {"home_url": "/"})


def build_admin_brand_settings_group(
    brand: BrandAssets | PersonaConsoleConfig | Mapping[str, object] | None = None,
    *,
    key: str = "admin-branding",
    title: str = "Admin Branding",
    description: str = "Runtime-owned admin shell name, icon, wordmark, and home link.",
) -> SettingsGroup:
    """Build a reusable settings group for optional admin shell brand assets."""

    model = _brand_model(brand)
    return SettingsGroup(
        key,
        title,
        description,
        fields=(
            SettingsField(
                "brand-name",
                "Brand title",
                "brand_name",
                "text",
                model.admin_title or model.name,
                autocomplete="organization",
                help_text="Bold text in the admin header when no title image or full lockup image is set.",
            ),
            SettingsField(
                "admin-subtitle",
                "Brand subtitle",
                "admin_subtitle",
                "text",
                model.admin_subtitle,
                placeholder="admin",
                help_text="Small text under the brand title. Leave blank when you do not want subtext.",
            ),
            SettingsField(
                "admin-icon-url",
                "Admin icon URL",
                "small_logo_url",
                "url",
                model.small_logo_url,
                placeholder="/static/example-icon.svg",
                help_text="Shown in the admin header when set. Leave blank for name-only branding.",
                autocomplete="url",
            ),
            SettingsField(
                "admin-wordmark-url",
                "Brand title image URL",
                "wordmark_url",
                "url",
                model.wordmark_url,
                placeholder="/static/example-wordmark.svg",
                help_text="Optional image shown instead of the bold title while keeping the subtitle.",
                autocomplete="url",
            ),
            SettingsField(
                "admin-lockup-url",
                "Full lockup image URL",
                "lockup_url",
                "url",
                model.lockup_url,
                placeholder="/static/example-lockup.svg",
                help_text="Optional image that replaces both the bold title and subtitle in the header.",
                autocomplete="url",
            ),
            SettingsField(
                "brand-home-url",
                "Brand home URL",
                "home_url",
                "url",
                model.home_url,
                placeholder="/",
                help_text="Target for the admin header brand link.",
                autocomplete="url",
            ),
        ),
    )


def build_admin_brand_settings_editor(
    brand: BrandAssets | PersonaConsoleConfig | Mapping[str, object] | None = None,
    *,
    form_action: str = "",
    form_method: str = "post",
    key: str = "admin-brand-settings",
    title: str = "Admin Branding",
    subtitle: str = "Update the shared admin shell branding for this runtime.",
    save_label: str = "Save branding",
    reset_href: str = "",
    groups: Sequence[SettingsGroup | Mapping[str, object]] = (),
    actions: Sequence[SurfaceAction | Mapping[str, object]] = (),
    messages: Sequence[SettingsValidationMessage | Mapping[str, object] | str] = (),
    banners: Sequence[FlashBanner | Mapping[str, object]] = (),
) -> SettingsEditorConfig:
    """Build a settings editor focused on PersonaConsole admin branding."""

    configured_groups = tuple(groups) or (build_admin_brand_settings_group(brand),)
    return SettingsEditorConfig(
        enabled=True,
        key=key,
        title=title,
        subtitle=subtitle,
        form_action=form_action,
        form_method=form_method,
        groups=configured_groups,
        messages=messages,
        banners=banners,
        actions=actions,
        save_label=save_label,
        reset_href=reset_href,
    )


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _kind(value: object) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    return raw if raw in _FIELD_KINDS else "text"


def _key(value: object, default: str = "field") -> str:
    raw = str(value or default or "").strip().lower().replace("_", "-")
    safe = "".join(char for char in raw if char.isalnum() or char == "-")
    return safe or default


def _attrs(**attrs: object) -> str:
    parts: list[str] = []
    for name, value in attrs.items():
        if value is True:
            parts.append(f" {name.replace('_', '-')}")
        elif value not in (None, False, ""):
            parts.append(f' {name.replace("_", "-")}="{escape(str(value), quote=True)}"')
    return "".join(parts)


def _field_name(field: SettingsField) -> str:
    return str(field.name or field.key or "").strip()


def _is_secret(field: SettingsField) -> bool:
    return bool(field.secret or field.redacted or _kind(field.kind) == "secret")


def _has_pending(field: SettingsField) -> bool:
    return field.pending_value is not None or bool(field.pending_display_value)


def _value_for_edit(field: SettingsField) -> Any:
    if _is_secret(field):
        return ""
    if field.pending_value is not None:
        return field.pending_value
    return field.value


def _display(value: Any) -> str:
    if isinstance(value, (dict, list, tuple)):
        return json.dumps(value, indent=2, sort_keys=True)
    if isinstance(value, bool):
        return "true" if value else "false"
    if value is None:
        return ""
    return str(value)


def _display_value(field: SettingsField, *, pending: bool = False) -> str:
    if _is_secret(field):
        explicit = field.pending_display_value if pending else field.display_value
        if explicit:
            return str(explicit)
        return "********" if (field.value or field.pending_value or field.changed) else "not configured"
    if pending and field.pending_display_value:
        return str(field.pending_display_value)
    if pending and field.pending_value is not None:
        return _display(field.pending_value)
    if field.display_value:
        return str(field.display_value)
    return _display(field.value)


def _bool(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "on", "enabled"}


def _badge_html(raw_badge: SurfaceBadge | Mapping[str, object] | str) -> str:
    badge = SurfaceBadge(str(raw_badge)) if isinstance(raw_badge, str) else _coerce(raw_badge, SurfaceBadge)
    if not badge.label:
        return ""
    return f'<span class="pc-settings-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-settings-badges">{body}</div>' if body else ""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], *, form: bool = False) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label:
        return ""
    tone = _tone(action.tone)
    cls = f"pc-settings-action pc-dashboard-tone-{tone}"
    body = escape(str(action.label))
    title = _attrs(title=action.title)
    method = str(action.method or "").strip().upper()
    if action.disabled:
        return f'<span class="{cls} is-disabled"{title} aria-disabled="true">{body}</span>'
    if form and method in {"POST", "GET"} and action.href:
        return (
            f'<button type="submit" class="{cls}" formaction="{escape(action.href, quote=True)}"'
            f' formmethod="{method.lower()}"{title}>{body}</button>'
        )
    if action.href:
        return (
            f'<a class="{cls}" href="{escape(action.href, quote=True)}"'
            f'{_attrs(data_method=method) if method else ""}{title}>{body}</a>'
        )
    return f'<span class="{cls}"{title}>{body}</span>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], *, form: bool = False) -> str:
    body = "".join(_action_html(action, form=form) for action in actions)
    return f'<div class="pc-settings-actions">{body}</div>' if body else ""


def _message_html(raw_message: SettingsValidationMessage | Mapping[str, object] | str) -> str:
    message = _coerce(raw_message, SettingsValidationMessage)
    if not message.message:
        return ""
    title = f'<strong>{escape(str(message.title))}</strong>' if message.title else ""
    return (
        f'<div class="pc-settings-message pc-dashboard-tone-{_tone(message.tone)}"'
        f'{_attrs(data_field_key=message.field_key)}>{title}<span>{escape(str(message.message))}</span></div>'
    )


def _messages_html(messages: Sequence[SettingsValidationMessage | Mapping[str, object] | str]) -> str:
    body = "".join(_message_html(message) for message in messages)
    return f'<div class="pc-settings-messages">{body}</div>' if body else ""


def _banner_html(raw_banner: FlashBanner | Mapping[str, object]) -> str:
    banner = _coerce(raw_banner, FlashBanner)
    if not banner.message:
        return ""
    title = f'<strong>{escape(str(banner.title))}</strong>' if banner.title else ""
    action = (
        f'<a class="pc-settings-banner-action" href="{escape(str(banner.action_href), quote=True)}">'
        f'{escape(str(banner.action_label))}</a>'
        if banner.action_label and banner.action_href
        else ""
    )
    dismiss = (
        f'<button type="button" class="pc-settings-banner-dismiss" data-pc-settings-dismiss>'
        f'{escape(str(banner.dismiss_label))}</button>'
        if banner.dismissible
        else ""
    )
    return (
        f'<div class="pc-settings-banner pc-dashboard-tone-{_tone(banner.tone)}">'
        f'<span>{title}{escape(str(banner.message))}</span>{action}{dismiss}</div>'
    )


def _banners_html(banners: Sequence[FlashBanner | Mapping[str, object]]) -> str:
    body = "".join(_banner_html(banner) for banner in banners)
    return f'<div class="pc-settings-banners">{body}</div>' if body else ""


def settings_editor_feature_enabled(
    config: SettingsEditorConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, SettingsEditorConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or SETTINGS_EDITOR_FEATURE), default=True)


def _option_html(raw_option: SettingsOption | Mapping[str, object] | str, selected_value: str) -> str:
    option = _coerce(raw_option, SettingsOption)
    key = str(option.key)
    label = str(option.label or option.key)
    selected = bool(option.selected or key == selected_value)
    return (
        f'<option value="{escape(key, quote=True)}"'
        f'{_attrs(selected=selected, disabled=option.disabled)}>{escape(label)}</option>'
    )


def _field_control_html(field: SettingsField, field_id: str) -> str:
    kind = _kind(field.kind)
    name = _field_name(field)
    disabled = bool(field.disabled or field.readonly)
    required = bool(field.required)
    value = _value_for_edit(field)
    value_text = _display(value)
    original = "" if _is_secret(field) else _display(field.value)
    common = _attrs(
        id=field_id,
        name=name,
        disabled=disabled,
        required=required,
        data_original_value=original,
        data_secret="true" if _is_secret(field) else "",
    )
    if kind in {"readonly", "json", "code"} or field.readonly:
        language = _key(field.code_language or ("json" if kind == "json" else "text"), "text")
        return (
            f'<pre class="pc-settings-readonly pc-settings-code-{language}"'
            f'{_attrs(data_original_value=original)}>{escape(_display_value(field, pending=_has_pending(field)))}</pre>'
        )
    if kind == "textarea":
        rows = max(2, int(field.rows or 4))
        return (
            f'<textarea{common}{_attrs(rows=rows, placeholder=field.placeholder, autocomplete=field.autocomplete)}>'
            f'{escape(value_text)}</textarea>'
        )
    if kind == "select":
        options = "".join(_option_html(option, value_text) for option in field.options)
        return f'<select{common}>{options}</select>'
    if kind == "boolean":
        checked = _bool(value)
        return (
            f'<label class="pc-settings-toggle"><input type="checkbox"{common}'
            f'{_attrs(value="true", checked=checked)}><span>{escape(field.placeholder or "Enabled")}</span></label>'
        )
    if _is_secret(field):
        input_type = "password"
    elif kind in {"number", "url"}:
        input_type = kind
    else:
        input_type = "text"
    placeholder = field.placeholder or ("Leave blank to keep current value" if _is_secret(field) else "")
    return (
        f'<input type="{input_type}"{common}'
        f'{_attrs(value="" if _is_secret(field) else value_text, placeholder=placeholder, autocomplete=field.autocomplete, inputmode=field.input_mode, min=field.min_value, max=field.max_value, step=field.step)}>'
    )


def _field_html(raw_field: SettingsField | Mapping[str, object]) -> str:
    field = _coerce(raw_field, SettingsField, {"key": "setting"})
    key = _key(field.key, "setting")
    label = str(field.label or field.key)
    field_id = f"pc-settings-{key}"
    changed = bool(field.changed)
    restart_required = bool(field.restart_required)
    classes = [
        "pc-settings-field",
        f"pc-settings-kind-{_kind(field.kind)}",
        f"pc-dashboard-tone-{_tone(field.tone or field.status)}",
    ]
    if changed:
        classes.append("is-changed")
    if restart_required:
        classes.append("is-restart-required")
    if field.disabled:
        classes.append("is-disabled")
    if field.readonly:
        classes.append("is-readonly")
    if _is_secret(field):
        classes.append("is-secret")
    status = f'<span class="pc-settings-field-status">{escape(str(field.status))}</span>' if field.status else ""
    required = '<span class="pc-settings-required">required</span>' if field.required else ""
    restart = '<span class="pc-settings-restart">restart required</span>' if restart_required else ""
    changed_pill = '<span class="pc-settings-changed">changed</span>' if changed else ""
    help_text = f'<div class="pc-settings-help">{escape(str(field.help_text))}</div>' if field.help_text else ""
    preview = (
        f'<div class="pc-settings-value-preview">{escape(_display_value(field))}</div>'
        if _is_secret(field) or field.display_value
        else ""
    )
    return (
        f'<article class="{" ".join(classes)}" data-pc-settings-field data-field-key="{escape(key, quote=True)}">'
        '<div class="pc-settings-field-head">'
        f'<label for="{escape(field_id, quote=True)}">{escape(label)}</label>'
        f'<div class="pc-settings-field-flags">{status}{required}{changed_pill}{restart}</div>'
        '</div>'
        f'<div class="pc-settings-control">{_field_control_html(field, field_id)}</div>'
        f'{preview}{help_text}{_messages_html(field.messages)}{_badges_html(field.badges)}{_actions_html(field.actions)}'
        '</article>'
    )


def _group_html(raw_group: SettingsGroup | Mapping[str, object]) -> str:
    group = _coerce(raw_group, SettingsGroup, {"key": "settings", "title": "Settings"})
    key = _key(group.key, "settings")
    fields_html = "".join(_field_html(field) for field in group.fields)
    if not fields_html:
        fields_html = '<div class="pc-dashboard-empty">No fields in this group.</div>'
    status = f'<span class="pc-surface-status pc-dashboard-tone-{_tone(group.tone or group.status)}">{escape(str(group.status))}</span>' if group.status else ""
    restart = '<span class="pc-settings-restart">restart required</span>' if group.restart_required else ""
    classes = f"pc-settings-group pc-dashboard-panel pc-dashboard-tone-{_tone(group.tone or group.status)}"
    if group.restart_required:
        classes += " is-restart-required"
    return (
        f'<fieldset class="{classes}" data-settings-group="{escape(key, quote=True)}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<legend class="pc-dashboard-section-title">{escape(str(group.title))}</legend>'
        f'<div class="pc-dashboard-section-meta">{escape(str(group.description))}</div>'
        f'</div><div class="pc-settings-group-meta">{status}{restart}{_badges_html(group.badges)}{_actions_html(group.actions)}</div></div>'
        f'<div class="pc-settings-grid">{fields_html}</div>'
        '</fieldset>'
    )


def _auto_changes(groups: Sequence[SettingsGroup | Mapping[str, object]]) -> list[SettingsChange]:
    changes: list[SettingsChange] = []
    for raw_group in groups:
        group = _coerce(raw_group, SettingsGroup, {"key": "settings", "title": "Settings"})
        for raw_field in group.fields:
            field = _coerce(raw_field, SettingsField, {"key": "setting"})
            if not field.changed:
                continue
            changes.append(
                SettingsChange(
                    label=str(field.label or field.key),
                    field_key=str(field.key),
                    before_display=_display_value(field),
                    after_display=_display_value(field, pending=True),
                    secret=_is_secret(field),
                    restart_required=field.restart_required,
                )
            )
    return changes


def _change_html(raw_change: SettingsChange | Mapping[str, object]) -> str:
    change = _coerce(raw_change, SettingsChange, {"label": "Setting"})
    before = "********" if change.secret else str(change.before_display or _display(change.before))
    after = "********" if change.secret else str(change.after_display or _display(change.after))
    restart = '<span class="pc-settings-restart">restart required</span>' if change.restart_required else ""
    return (
        f'<div class="pc-settings-change pc-dashboard-tone-{_tone(change.tone)}"'
        f'{_attrs(data_field_key=change.field_key)}>'
        f'<strong>{escape(str(change.label))}</strong>'
        f'<span class="pc-settings-diff"><del>{escape(before)}</del><ins>{escape(after)}</ins></span>'
        f'{restart}</div>'
    )


def _changes_html(changes: Sequence[SettingsChange | Mapping[str, object]], groups: Sequence[SettingsGroup | Mapping[str, object]]) -> str:
    all_changes = list(changes) or _auto_changes(groups)
    body = "".join(_change_html(change) for change in all_changes)
    if not body:
        return ""
    return (
        '<section class="pc-settings-changes pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        '<div class="pc-dashboard-section-title">Pending Changes</div>'
        f'<div class="pc-dashboard-section-meta"><span data-pc-settings-changed-count data-initial-count="{len(all_changes)}">{len(all_changes)}</span> changed settings</div>'
        '</div></div>'
        f'<div class="pc-settings-change-list">{body}</div></section>'
    )


def render_settings_editor(
    config: SettingsEditorConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, SettingsEditorConfig)
    if not settings_editor_feature_enabled(model, features):
        return ""
    groups = tuple(model.groups or ())
    group_html = "".join(_group_html(group) for group in groups)
    if not group_html:
        group_html = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    method = str(model.form_method or "post").strip().lower()
    if method not in {"get", "post"}:
        method = "post"
    restart_required = bool(model.restart_required or any(_coerce(group, SettingsGroup, {"key": "settings", "title": "Settings"}).restart_required for group in groups))
    restart = '<span class="pc-settings-restart">restart required</span>' if restart_required else ""
    actions = _actions_html(model.actions, form=bool(model.form_action))
    reset = f'<a class="pc-settings-action pc-dashboard-tone-neutral" href="{escape(model.reset_href, quote=True)}">{escape(str(model.reset_label))}</a>' if model.reset_href else ""
    save = (
        f'<button type="submit" class="pc-settings-action pc-settings-save pc-dashboard-tone-good">{escape(str(model.save_label))}</button>'
        if model.form_action
        else ""
    )
    footer = f'<div class="pc-settings-footer">{save}{reset}{actions}</div>' if save or reset or actions else ""
    body = (
        f'{_banners_html(model.banners)}{_messages_html(model.messages)}'
        f'{_changes_html(model.changes, groups)}{group_html}{footer}'
    )
    shell_open = (
        f'<form class="pc-settings-editor pc-dashboard-surface" id="{escape(_key(model.key, "settings-editor"), quote=True)}"'
        f' method="{method}" action="{escape(model.form_action, quote=True)}" data-pc-settings-editor>'
        if model.form_action
        else f'<section class="pc-settings-editor pc-dashboard-surface" id="{escape(_key(model.key, "settings-editor"), quote=True)}" data-pc-settings-editor>'
    )
    shell_close = "</form>" if model.form_action else "</section>"
    return (
        shell_open
        + '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div><div class="pc-settings-overview-meta">{restart}</div></div>'
        + body
        + shell_close
    )
