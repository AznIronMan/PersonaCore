from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
import json
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    BrandAssets,
    ControlAccessContext,
    ControlCenterConfig,
    ControlChange,
    ControlGroup,
    ControlItem,
    ControlOption,
    ControlSection,
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
    SurfaceRegistration,
    SurfaceRegistryConfig,
    ThemeTokens,
)
from .privacy import feature_enabled

SETTINGS_EDITOR_FEATURE = "settings_editor"
CONTROL_CENTER_FEATURE = "control_center"

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

_CONTROL_KINDS = _FIELD_KINDS | {
    "switch",
    "toggle",
    "segmented",
    "color",
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
    if cls is ControlOption and isinstance(value, str):
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
        elif value is not None and value is not False and value != "":
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


def control_center_feature_enabled(
    config: ControlCenterConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, ControlCenterConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or CONTROL_CENTER_FEATURE), default=True)


def _control_access_context(value: ControlAccessContext | Mapping[str, object] | None) -> ControlAccessContext | None:
    if value is None:
        return None
    return _coerce(value, ControlAccessContext)


def _control_access_term(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _control_access_terms(values: Sequence[str] | str | None) -> tuple[str, ...]:
    if not values:
        return ()
    raw_values: Sequence[object]
    if isinstance(values, str):
        raw_values = (values,)
    else:
        raw_values = tuple(values)
    terms: list[str] = []
    for value in raw_values:
        term = _control_access_term(value)
        if term and term not in terms:
            terms.append(term)
    return tuple(terms)


def _control_context_terms(access: ControlAccessContext) -> set[str]:
    terms = set(_control_access_terms(access.scopes))
    role = _control_access_term(access.role)
    if role:
        terms.add(role)
    return terms


def _control_context_role_terms(access: ControlAccessContext) -> set[str]:
    role = _control_access_term(access.role)
    return {role} if role else set()


def _control_can_view(item: ControlItem, access: ControlAccessContext | None) -> bool:
    if access is None or access.can_view_all:
        return True
    roles = set(_control_access_terms(item.view_roles))
    if not roles:
        return True
    return bool(roles & _control_context_terms(access))


def _control_can_edit(item: ControlItem, access: ControlAccessContext | None) -> bool:
    if item.disabled or item.readonly:
        return False
    if access is None:
        return True
    if access.can_edit_all:
        return True
    roles = set(_control_access_terms(item.edit_roles))
    if roles:
        return bool(roles & _control_context_role_terms(access))
    return bool(access.default_can_edit)


def _control_access_badge(item: ControlItem) -> str:
    roles = _control_access_terms(item.edit_roles)
    if not roles:
        return ""
    label = "/".join(role.replace("_", " ") for role in roles)
    return f'<span class="pc-control-badge pc-control-access">{escape(label)} edit</span>'


def _control_kind(value: object) -> str:
    raw = str(value or "").strip().lower().replace("_", "-")
    return raw if raw in _CONTROL_KINDS else "text"


def _control_name(item: ControlItem) -> str:
    return str(item.name or item.source_path or item.key or "").strip()


def _control_is_secret(item: ControlItem) -> bool:
    return bool(item.secret or item.redacted or _control_kind(item.kind) == "secret")


def _control_has_pending(item: ControlItem) -> bool:
    return item.pending_value is not None or bool(item.pending_display_value)


def _control_value_for_edit(item: ControlItem) -> Any:
    if _control_is_secret(item):
        return ""
    if item.pending_value is not None:
        return item.pending_value
    return item.value


def _control_display_value(item: ControlItem, *, pending: bool = False) -> str:
    if _control_is_secret(item):
        explicit = item.display_value
        return str(explicit or ("configured" if (item.value or item.changed or item.pending_value is not None) else "not configured"))
    if pending and item.pending_display_value:
        return str(item.pending_display_value)
    if pending and item.pending_value is not None:
        return _display(item.pending_value)
    if item.display_value:
        return str(item.display_value)
    return _display(item.value)


def _control_original_value(item: ControlItem) -> str:
    if _control_is_secret(item):
        return ""
    if isinstance(item.value, (Mapping, list, tuple)):
        try:
            return json.dumps(_control_detail_value(item.value), sort_keys=True, default=str)
        except TypeError:
            return _display(_control_detail_value(item.value))
    return _display(item.value)


def _control_sensitive_key(key: object) -> bool:
    normalized = str(key or "").strip().lower().replace("-", "_")
    markers = (
        "api_key",
        "apikey",
        "authorization",
        "bearer",
        "credential",
        "password",
        "private_key",
        "secret",
        "token",
    )
    return any(marker in normalized for marker in markers)


def _control_sensitive_value(value: object) -> bool:
    text = str(value or "").strip()
    lowered = text.lower()
    return bool(
        text
        and (
            lowered.startswith(("bearer ", "sk-", "xox", "ghp_", "gho_", "github_pat_"))
            or "api_key=" in lowered
            or "authorization:" in lowered
        )
    )


def _control_detail_value(value: Any, *, key: object = "", depth: int = 0) -> Any:
    if _control_sensitive_key(key):
        return "REDACTED" if value not in (None, "", (), [], {}) else ""
    if depth > 6:
        return "..."
    if isinstance(value, Mapping):
        return {str(child_key): _control_detail_value(child, key=child_key, depth=depth + 1) for child_key, child in value.items()}
    if isinstance(value, (list, tuple)):
        return [_control_detail_value(child, depth=depth + 1) for child in value]
    if _control_sensitive_value(value):
        return "REDACTED"
    return value


def _control_detail_payload(item: ControlItem) -> Any:
    if _control_is_secret(item):
        return None
    metadata = item.metadata if isinstance(item.metadata, Mapping) else {}
    for detail_key in ("details", "detail", "detail_payload", "detailPayload"):
        if detail_key in metadata:
            detail = metadata.get(detail_key)
            if isinstance(detail, (Mapping, list, tuple)):
                return _control_detail_value(detail)
    if isinstance(item.value, (Mapping, list, tuple)):
        return _control_detail_value(item.value)
    return None


def _control_detail_html(item: ControlItem) -> str:
    payload = _control_detail_payload(item)
    if payload in (None, {}, [], ()):
        return ""
    try:
        text = json.dumps(payload, indent=2, sort_keys=True, default=str)
    except TypeError:
        text = _display(payload)
    return (
        '<details class="pc-control-detail">'
        '<summary>View details</summary>'
        f'<pre>{escape(text)}</pre>'
        '</details>'
    )


def _control_option_html(raw_option: ControlOption | Mapping[str, object] | str, selected_value: str) -> str:
    option = _coerce(raw_option, ControlOption)
    key = str(option.key)
    label = str(option.label or option.key)
    selected = bool(option.selected or key == selected_value)
    return (
        f'<option value="{escape(key, quote=True)}"'
        f'{_attrs(selected=selected, disabled=option.disabled)}>{escape(label)}</option>'
    )


def _control_segment_html(item: ControlItem, item_id: str, selected_value: str, *, editable: bool = True) -> str:
    name = _control_name(item)
    disabled = bool(not editable or item.disabled or item.readonly)
    buttons: list[str] = []
    for index, raw_option in enumerate(item.options):
        option = _coerce(raw_option, ControlOption)
        option_id = f"{item_id}-{index}"
        key = str(option.key)
        checked = bool(option.selected or key == selected_value)
        buttons.append(
            '<label class="pc-control-segment">'
            f'<input type="radio"{_attrs(id=option_id, name=name, value=key, checked=checked, disabled=disabled or option.disabled, required=item.required, data_original_value=_display(item.value))}>'
            f'<span>{escape(str(option.label or option.key))}</span></label>'
        )
    return f'<div class="pc-control-segments" role="group" aria-labelledby="{escape(item_id, quote=True)}-label">{"".join(buttons)}</div>'


def _control_secret_configured(item: ControlItem) -> bool:
    status = str(item.status or "").strip().lower()
    display = str(item.display_value or "").strip().lower()
    return bool(item.value or item.changed or item.pending_value is not None or status == "configured" or display == "configured")


def _control_control_html(item: ControlItem, item_id: str, *, editable: bool = True) -> str:
    kind = _control_kind(item.kind)
    name = _control_name(item)
    disabled = bool(not editable or item.disabled)
    required = bool(item.required)
    value = _control_value_for_edit(item)
    value_text = _display(value)
    original = _control_original_value(item)
    common = _attrs(
        id=item_id,
        name=name,
        disabled=disabled,
        required=required,
        data_original_value=original,
        data_secret="true" if _control_is_secret(item) else "",
    )
    if kind in {"readonly", "json", "code"} or item.readonly:
        language = _key("json" if kind == "json" else "text", "text")
        return (
            f'<pre class="pc-control-readonly pc-settings-code-{language}"'
            f'{_attrs(data_original_value=original)}>{escape(_control_display_value(item, pending=_control_has_pending(item)))}</pre>'
        )
    if kind == "textarea":
        rows = max(2, int(item.rows or 4))
        return f'<textarea{common}{_attrs(rows=rows, placeholder=item.placeholder)}>{escape(value_text)}</textarea>'
    if kind == "select":
        options = "".join(_control_option_html(option, value_text) for option in item.options)
        return f'<select{common}>{options}</select>'
    if kind == "segmented":
        return _control_segment_html(item, item_id, value_text, editable=editable)
    if kind in {"boolean", "switch", "toggle"}:
        checked = _bool(value)
        hidden = f'<input type="hidden" name="{escape(name, quote=True)}" value="false"{_attrs(disabled=disabled)}>'
        return (
            f'<label class="pc-control-switch">{hidden}<input type="checkbox"{common}'
            f'{_attrs(value="true", checked=checked)}><span aria-hidden="true"></span>'
            f'<strong>{escape("On" if checked else "Off")}</strong></label>'
        )
    if _control_is_secret(item):
        input_type = "password"
    elif kind in {"number", "url"}:
        input_type = kind
    else:
        input_type = "text"
    placeholder = item.placeholder or (
        "Stored; type here to overwrite" if _control_is_secret(item) and _control_secret_configured(item) else "Type to store value" if _control_is_secret(item) else ""
    )
    swatch = f'<span class="pc-control-swatch"{_attrs(style=f"background: {value_text}")}></span>' if kind == "color" and value_text else ""
    input_html = (
        f'{swatch}<input type="{input_type}"{common}'
        f'{_attrs(value="" if _control_is_secret(item) else value_text, placeholder=placeholder, min=item.min_value, max=item.max_value, step=item.step)}>'
    )
    if _control_is_secret(item) and item.clearable and name:
        clear_name = str(item.clear_name or f"{name}.__clear")
        clear_label = str(item.clear_label or "Clear stored value")
        input_html += (
            '<label class="pc-control-clear">'
            f'<input type="checkbox"{_attrs(name=clear_name, value="true", disabled=disabled)}>'
            f'<span>{escape(clear_label)}</span></label>'
        )
    return input_html


def _control_item_html(raw_item: ControlItem | Mapping[str, object], access: ControlAccessContext | None = None) -> str:
    item = _coerce(raw_item, ControlItem, {"key": "control"})
    if not _control_can_view(item, access):
        return ""
    key = _key(item.key, "control")
    label = str(item.label or item.key)
    item_id = f"pc-control-{key}"
    changed = bool(item.changed)
    restart_required = bool(item.restart_required)
    editable = _control_can_edit(item, access)
    tone = item.tone or item.status
    if item.dangerous and not tone:
        tone = "bad"
    classes = [
        "pc-control-item",
        f"pc-control-kind-{_control_kind(item.kind)}",
        f"pc-dashboard-tone-{_tone(tone)}",
    ]
    if changed:
        classes.append("is-changed")
    if restart_required:
        classes.append("is-restart-required")
    if item.disabled:
        classes.append("is-disabled")
    if item.readonly:
        classes.append("is-readonly")
    if not editable and not item.readonly and not item.disabled:
        classes.append("is-view-only")
    if item.dangerous:
        classes.append("is-dangerous")
    if _control_is_secret(item):
        classes.append("is-secret")
    status = f'<span class="pc-control-badge pc-dashboard-tone-{_tone(item.status)}">{escape(str(item.status))}</span>' if item.status else ""
    owner = f'<span class="pc-control-owner">{escape(str(item.owner or "Runtime"))}</span>'
    mode_label = "disabled" if item.disabled else "read-only" if item.readonly else "editable" if editable else "view-only"
    mode = f'<span class="pc-control-badge">{mode_label}</span>'
    required = '<span class="pc-control-badge">required</span>' if item.required else ""
    redacted = '<span class="pc-control-badge">redacted</span>' if _control_is_secret(item) else ""
    restart = '<span class="pc-control-restart">restart required</span>' if restart_required else ""
    changed_pill = '<span class="pc-control-changed">changed</span>' if changed else ""
    dangerous = '<span class="pc-control-danger">danger</span>' if item.dangerous else ""
    help_text = f'<div class="pc-control-help">{escape(str(item.help_text))}</div>' if item.help_text else ""
    source = f'<code>{escape(str(item.source_path))}</code>' if item.source_path else ""
    preview = (
        f'<div class="pc-control-value-preview">{escape(_control_display_value(item))}</div>'
        if _control_is_secret(item) or item.display_value
        else ""
    )
    return (
        f'<article class="{" ".join(classes)}" data-pc-control-item data-pc-settings-field data-control-key="{escape(key, quote=True)}">'
        '<div class="pc-control-item-head">'
        f'<div><label id="{escape(item_id, quote=True)}-label" for="{escape(item_id, quote=True)}">{escape(label)}</label>{source}</div>'
        f'<div class="pc-control-flags">{owner}{mode}{_control_access_badge(item)}{status}{required}{redacted}{changed_pill}{restart}{dangerous}</div>'
        '</div>'
        f'<div class="pc-control-input">{_control_control_html(item, item_id, editable=editable)}</div>'
        f'{preview}{help_text}{_control_detail_html(item)}{_messages_html(item.messages)}{_badges_html(item.badges)}{_actions_html(item.actions)}'
        '</article>'
    )


def _control_group_html(raw_group: ControlGroup | Mapping[str, object], access: ControlAccessContext | None = None) -> str:
    group = _coerce(raw_group, ControlGroup, {"key": "controls", "title": "Controls"})
    key = _key(group.key, "controls")
    item_html = "".join(_control_item_html(item, access) for item in group.items)
    if not item_html:
        if access is not None:
            return ""
        item_html = '<div class="pc-dashboard-empty">No controls in this group.</div>'
    status = f'<span class="pc-surface-status pc-dashboard-tone-{_tone(group.tone or group.status)}">{escape(str(group.status))}</span>' if group.status else ""
    restart = '<span class="pc-control-restart">restart required</span>' if group.restart_required else ""
    owner = f'<span class="pc-control-owner">{escape(str(group.owner))}</span>' if group.owner else ""
    return (
        f'<section class="pc-control-group pc-dashboard-panel pc-dashboard-tone-{_tone(group.tone or group.status)}" data-control-group="{escape(key, quote=True)}">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<h3 class="pc-dashboard-section-title">{escape(str(group.title))}</h3>'
        f'<div class="pc-dashboard-section-meta">{escape(str(group.description))}</div>'
        f'</div><div class="pc-control-group-meta">{owner}{status}{restart}{_badges_html(group.badges)}{_actions_html(group.actions)}</div></div>'
        f'<div class="pc-control-grid">{item_html}</div></section>'
    )


def _control_section_html(raw_section: ControlSection | Mapping[str, object], access: ControlAccessContext | None = None) -> str:
    section = _coerce(raw_section, ControlSection, {"key": "section", "title": "Section"})
    key = _key(section.key, "section")
    groups_html = "".join(_control_group_html(group, access) for group in section.groups)
    if not groups_html:
        if access is not None:
            return ""
        groups_html = '<div class="pc-dashboard-empty">No controls in this section.</div>'
    status = f'<span class="pc-surface-status pc-dashboard-tone-{_tone(section.tone or section.status)}">{escape(str(section.status))}</span>' if section.status else ""
    return (
        f'<section id="pc-control-section-{escape(key, quote=True)}" class="pc-control-section" data-control-section="{escape(key, quote=True)}">'
        '<div class="pc-control-section-head">'
        f'<div><h2>{escape(str(section.title))}</h2><p>{escape(str(section.description))}</p></div>'
        f'<div class="pc-control-section-meta">{status}{_badges_html(section.badges)}{_actions_html(section.actions)}</div></div>'
        f'{groups_html}</section>'
    )


def _control_items(
    sections: Sequence[ControlSection | Mapping[str, object]],
    access: ControlAccessContext | None = None,
) -> list[ControlItem]:
    items: list[ControlItem] = []
    for raw_section in sections:
        section = _coerce(raw_section, ControlSection, {"key": "section", "title": "Section"})
        for raw_group in section.groups:
            group = _coerce(raw_group, ControlGroup, {"key": "controls", "title": "Controls"})
            for raw_item in group.items:
                item = _coerce(raw_item, ControlItem, {"key": "control"})
                if _control_can_view(item, access):
                    items.append(item)
    return items


def _auto_control_changes(
    sections: Sequence[ControlSection | Mapping[str, object]],
    access: ControlAccessContext | None = None,
) -> list[ControlChange]:
    changes: list[ControlChange] = []
    for item in _control_items(sections, access):
        if not item.changed:
            continue
        changes.append(
            ControlChange(
                label=str(item.label or item.key),
                control_key=str(item.key),
                before_display=_control_display_value(item),
                after_display="********" if _control_is_secret(item) else _control_display_value(item, pending=True),
                secret=_control_is_secret(item),
                restart_required=item.restart_required,
            )
        )
    return changes


def _control_change_html(raw_change: ControlChange | Mapping[str, object]) -> str:
    change = _coerce(raw_change, ControlChange, {"label": "Control"})
    before = "********" if change.secret else str(change.before_display or _display(change.before))
    after = "********" if change.secret else str(change.after_display or _display(change.after))
    restart = '<span class="pc-control-restart">restart required</span>' if change.restart_required else ""
    return (
        f'<div class="pc-control-change pc-dashboard-tone-{_tone(change.tone)}"'
        f'{_attrs(data_control_key=change.control_key)}>'
        f'<strong>{escape(str(change.label))}</strong>'
        f'<span class="pc-control-diff"><del>{escape(before)}</del><ins>{escape(after)}</ins></span>'
        f'{restart}</div>'
    )


def _control_visible_keys(
    sections: Sequence[ControlSection | Mapping[str, object]],
    access: ControlAccessContext | None = None,
) -> set[str]:
    return {
        key
        for item in _control_items(sections, access)
        for key in (str(item.key or ""), str(item.source_path or ""), _control_name(item))
        if key
    }


def _control_explicit_changes(
    changes: Sequence[ControlChange | Mapping[str, object]],
    sections: Sequence[ControlSection | Mapping[str, object]],
    access: ControlAccessContext | None = None,
) -> list[ControlChange]:
    visible_keys = _control_visible_keys(sections, access)
    rendered: list[ControlChange] = []
    for raw_change in changes:
        change = _coerce(raw_change, ControlChange, {"label": "Control"})
        if access is not None and change.control_key and str(change.control_key) not in visible_keys:
            continue
        rendered.append(change)
    return rendered


def _control_changes_html(
    changes: Sequence[ControlChange | Mapping[str, object]],
    sections: Sequence[ControlSection | Mapping[str, object]],
    access: ControlAccessContext | None = None,
) -> str:
    if changes:
        all_changes = _control_explicit_changes(changes, sections, access)
    else:
        all_changes = _auto_control_changes(sections, access)
    body = "".join(_control_change_html(change) for change in all_changes)
    if not body:
        return ""
    return (
        '<section class="pc-control-changes pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        '<div class="pc-dashboard-section-title">Pending Changes</div>'
        f'<div class="pc-dashboard-section-meta"><span data-pc-control-changed-count data-initial-count="{len(all_changes)}">{len(all_changes)}</span> staged controls</div>'
        '</div></div>'
        f'<div class="pc-control-change-list">{body}</div></section>'
    )


def _control_overview_html(
    model: ControlCenterConfig,
    sections: Sequence[ControlSection | Mapping[str, object]],
    access: ControlAccessContext | None = None,
) -> str:
    items = _control_items(sections, access)
    bool_items = [item for item in items if _control_kind(item.kind) in {"boolean", "switch", "toggle"}]
    enabled = sum(1 for item in bool_items if _bool(item.pending_value if item.pending_value is not None else item.value))
    disabled = max(0, len(bool_items) - enabled)
    changes = len(_control_explicit_changes(model.changes, sections, access)) if model.changes else len(_auto_control_changes(sections, access))
    restart = sum(1 for item in items if item.restart_required or item.changed and item.restart_required)
    secrets = sum(1 for item in items if _control_is_secret(item))
    metrics = (
        ("Controls", len(items), "configured"),
        ("Enabled", enabled, "switches on"),
        ("Off", disabled, "switches off"),
        ("Pending", changes, "staged"),
        ("Restart", restart, "required"),
        ("Secrets", secrets, "redacted"),
    )
    body = "".join(
        f'<div class="pc-control-metric"><span>{escape(label)}</span><strong>{escape(str(value))}</strong><small>{escape(detail)}</small></div>'
        for label, value, detail in metrics
    )
    return f'<section class="pc-control-overview" aria-label="Control summary">{body}</section>'


def render_control_center(
    config: ControlCenterConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    access_context: ControlAccessContext | Mapping[str, object] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, ControlCenterConfig)
    if not control_center_feature_enabled(model, features):
        return ""
    access = _control_access_context(access_context)
    sections = tuple(model.sections or ())
    rendered_sections: list[tuple[ControlSection, str]] = []
    for raw_section in sections:
        section = _coerce(raw_section, ControlSection, {"key": "section", "title": "Section"})
        html = _control_section_html(section, access)
        if html:
            rendered_sections.append((section, html))
    section_html = "".join(html for _section, html in rendered_sections)
    if not section_html:
        section_html = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    method = str(model.form_method or "post").strip().lower()
    if method not in {"get", "post"}:
        method = "post"
    visible_items = _control_items(sections, access)
    restart_required = bool(model.restart_required or any(item.restart_required for item in visible_items))
    restart = '<span class="pc-control-restart">restart required</span>' if restart_required else ""
    actions = _actions_html(model.actions, form=bool(model.form_action))
    reset = f'<a class="pc-settings-action pc-dashboard-tone-neutral" href="{escape(model.reset_href, quote=True)}">{escape(str(model.reset_label))}</a>' if model.reset_href else ""
    save_disabled = bool(access is not None and not any(_control_can_edit(item, access) for item in visible_items))
    save = (
        f'<button type="submit" class="pc-settings-action pc-settings-save pc-dashboard-tone-good"{_attrs(disabled=save_disabled, title="No editable controls for this access level" if save_disabled else "")}>{escape(str(model.save_label))}</button>'
        if model.form_action
        else ""
    )
    footer = f'<div class="pc-control-footer">{save}{reset}{actions}</div>' if save or reset or actions else ""
    nav = "".join(
        f'<a href="#pc-control-section-{escape(_key(_coerce(section, ControlSection, {"key": "section", "title": "Section"}).key), quote=True)}">{escape(str(_coerce(section, ControlSection, {"key": "section", "title": "Section"}).title))}</a>'
        for section, _html in rendered_sections
    )
    body = (
        f'{_banners_html(model.banners)}{_messages_html(model.messages)}'
        f'{_control_overview_html(model, sections, access)}{_control_changes_html(model.changes, sections, access)}'
        f'{f"<nav class=\"pc-control-nav\" aria-label=\"Control Center sections\">{nav}</nav>" if nav else ""}'
        f'{section_html}{footer}'
    )
    shell_open = (
        f'<form class="pc-control-center pc-dashboard-surface" id="{escape(_key(model.key, "control-center"), quote=True)}"'
        f' method="{method}" action="{escape(model.form_action, quote=True)}" data-pc-control-center>'
        if model.form_action
        else f'<section class="pc-control-center pc-dashboard-surface" id="{escape(_key(model.key, "control-center"), quote=True)}" data-pc-control-center>'
    )
    shell_close = "</form>" if model.form_action else "</section>"
    return (
        shell_open
        + '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div><div class="pc-control-overview-meta">{restart}</div></div>'
        + body
        + shell_close
    )


def build_control_center_from_sources(
    console_config: PersonaConsoleConfig | Mapping[str, object] | None = None,
    *,
    surface_registry: SurfaceRegistryConfig | Mapping[str, object] | None = None,
    engine_catalog: Mapping[str, object] | object | None = None,
    sections: Sequence[ControlSection | Mapping[str, object]] = (),
    form_action: str = "",
    form_method: str = "post",
    key: str = "control-center",
    title: str = "Control Center",
    subtitle: str = "Feature gates, runtime behavior, appearance, integrations, and staged changes.",
    actions: Sequence[SurfaceAction | Mapping[str, object]] = (),
    messages: Sequence[SettingsValidationMessage | Mapping[str, object] | str] = (),
    banners: Sequence[FlashBanner | Mapping[str, object]] = (),
    save_label: str = "Save staged changes",
    reset_href: str = "",
) -> ControlCenterConfig:
    configured_sections = _base_control_sections()
    console_feature_items = _console_feature_controls(console_config, surface_registry)
    if console_feature_items:
        configured_sections["features"].append(ControlGroup("console-features", "PersonaConsole Features", "Shared admin surface switches.", "Console", tuple(console_feature_items)))
    appearance_groups = _appearance_control_groups(console_config)
    configured_sections["appearance"].extend(appearance_groups)
    registry_groups = _surface_registry_control_groups(surface_registry)
    configured_sections["advanced"].extend(registry_groups)
    for group in _engine_control_groups(engine_catalog):
        section_key = group.metadata.get("section") if isinstance(group.metadata, Mapping) else ""
        target = str(section_key or _section_for_group(group))
        configured_sections.setdefault(target, []).append(group)
    for raw_section in sections:
        section = _coerce(raw_section, ControlSection, {"key": "custom", "title": "Custom"})
        configured_sections.setdefault(str(section.key or "custom"), []).extend(
            _coerce(group, ControlGroup, {"key": "custom", "title": "Custom"}) for group in section.groups
        )
    ordered = []
    titles = {
        "features": ("Features", "PersonaConsole surface switches and PersonaEngine feature gates."),
        "appearance": ("Appearance & Navigation", "Branding, theme tokens, and navigation labels."),
        "runtime": ("Runtime Behavior", "Cadence, policy, canary, memory, media, and worker controls."),
        "persona": ("Persona Extensions", "Runtime-owned persona pack, profile, memory, and voice/media controls."),
        "integrations": ("Integrations", "Connectors, provider routes, token posture, and adapter references."),
        "advanced": ("Advanced & Audit", "Read-only previews, schema references, and runtime-owned audit actions."),
    }
    for section_key in ("features", "appearance", "runtime", "persona", "integrations", "advanced"):
        groups = tuple(group for group in configured_sections.get(section_key, ()) if group.items)
        if not groups:
            continue
        title_text, description = titles[section_key]
        ordered.append(ControlSection(section_key, title_text, description, groups))
    for section_key, raw_groups in configured_sections.items():
        if section_key in titles:
            continue
        groups = tuple(group for group in raw_groups if group.items)
        if groups:
            ordered.append(ControlSection(section_key, _human_label(section_key), "Runtime-supplied controls.", groups))
    return ControlCenterConfig(
        enabled=True,
        key=key,
        title=title,
        subtitle=subtitle,
        form_action=form_action,
        form_method=form_method,
        sections=tuple(ordered),
        actions=actions,
        messages=messages,
        banners=banners,
        save_label=save_label,
        reset_href=reset_href,
    )


def _base_control_sections() -> dict[str, list[ControlGroup]]:
    return {"features": [], "appearance": [], "runtime": [], "persona": [], "integrations": [], "advanced": []}


def _section_for_group(group: ControlGroup) -> str:
    if group.key.startswith("engine-feature"):
        return "features"
    if "persona" in group.key or "extension" in group.key:
        return "persona"
    if "provider" in group.key or "connector" in group.key:
        return "integrations"
    if "advanced" in group.key or "registry" in group.key:
        return "advanced"
    return "runtime"


def _console_feature_controls(
    console_config: PersonaConsoleConfig | Mapping[str, object] | None,
    surface_registry: SurfaceRegistryConfig | Mapping[str, object] | None,
) -> list[ControlItem]:
    feature_map: dict[str, bool] = {}
    summaries: dict[str, str] = {}
    if console_config is not None:
        config_data = _mapping(console_config)
        feature_map.update({str(key): bool(value) for key, value in _mapping(config_data.get("features")).items()})
    if surface_registry is not None:
        registry = _coerce(surface_registry, SurfaceRegistryConfig)
        feature_map.update({str(key): bool(value) for key, value in registry.features.items() if str(key) not in feature_map})
        for raw_surface in registry.surfaces:
            surface = _coerce(raw_surface, SurfaceRegistration, {"key": "surface", "label": "Surface"})
            if surface.feature:
                feature_map.setdefault(surface.feature, bool(surface.enabled))
                summaries.setdefault(surface.feature, surface.summary or f"Surface: {surface.label}")
    return [
        ControlItem(
            key=f"pc-feature-{_key(feature, 'feature')}",
            label=_human_label(feature),
            name=f"pc.feature.{feature}",
            kind="switch",
            value=enabled,
            help_text=summaries.get(feature, f"PersonaConsole feature flag for {feature}."),
            owner="Console",
            source_path=f"pc.feature.{feature}",
            section="features",
            status="enabled" if enabled else "disabled",
            tone="good" if enabled else "warn",
            restart_required=True,
            metadata={"feature_key": feature},
        )
        for feature, enabled in sorted(feature_map.items())
    ]


def _appearance_control_groups(console_config: PersonaConsoleConfig | Mapping[str, object] | None) -> list[ControlGroup]:
    if console_config is None:
        return []
    config_data = _mapping(console_config)
    brand = _brand_model(console_config)
    theme_raw = config_data.get("theme")
    theme = theme_raw if isinstance(theme_raw, ThemeTokens) else ThemeTokens(**_mapping(theme_raw)) if _mapping(theme_raw) else ThemeTokens()
    brand_items = (
        ControlItem("pc-brand-name", "Brand title", "pc.brand.name", "text", brand.admin_title or brand.name, owner="Console", source_path="pc.brand.name"),
        ControlItem("pc-brand-subtitle", "Brand subtitle", "pc.brand.admin_subtitle", "text", brand.admin_subtitle, owner="Console", source_path="pc.brand.admin_subtitle"),
        ControlItem("pc-brand-icon", "Admin icon URL", "pc.brand.small_logo_url", "url", brand.small_logo_url, owner="Console", source_path="pc.brand.small_logo_url"),
        ControlItem("pc-brand-home", "Brand home URL", "pc.brand.home_url", "url", brand.home_url, owner="Console", source_path="pc.brand.home_url"),
    )
    theme_items = (
        ControlItem("pc-theme-accent", "Accent", "pc.theme.accent", "color", theme.accent, owner="Console", source_path="pc.theme.accent"),
        ControlItem("pc-theme-background", "Background", "pc.theme.background", "text", theme.background, owner="Console", source_path="pc.theme.background"),
        ControlItem("pc-theme-surface", "Surface", "pc.theme.surface", "text", theme.surface, owner="Console", source_path="pc.theme.surface"),
        ControlItem("pc-theme-text", "Text", "pc.theme.text", "text", theme.text, owner="Console", source_path="pc.theme.text"),
    )
    nav_items: list[ControlItem] = []
    for index, raw_group in enumerate(config_data.get("nav_groups", ()) or ()):
        group = _mapping(raw_group)
        label = str(group.get("label", f"Group {index + 1}"))
        nav_items.append(
            ControlItem(
                f"pc-nav-group-{index}",
                f"Navigation group {index + 1}",
                f"pc.nav_groups.{index}.label",
                "text",
                label,
                owner="Console",
                source_path=f"pc.nav_groups.{index}.label",
                help_text="Runtime-owned label for a grouped admin navigation menu.",
            )
        )
    groups = [
        ControlGroup("pc-branding", "Branding", "Admin shell brand assets and header target.", "Console", brand_items),
        ControlGroup("pc-theme", "Theme Tokens", "Shared admin color tokens.", "Console", theme_items),
    ]
    if nav_items:
        groups.append(ControlGroup("pc-navigation", "Navigation", "Grouped admin navigation labels.", "Console", tuple(nav_items)))
    return groups


def _surface_registry_control_groups(surface_registry: SurfaceRegistryConfig | Mapping[str, object] | None) -> list[ControlGroup]:
    if surface_registry is None:
        return []
    registry = _coerce(surface_registry, SurfaceRegistryConfig)
    preview = {
        "surface_count": len(registry.surfaces),
        "feature_count": len(registry.features),
        "theme_key": registry.theme_key,
    }
    items = [
        ControlItem(
            "pc-surface-registry-preview",
            "Surface registry preview",
            "pc.surface_registry",
            "json",
            preview,
            owner="Console",
            source_path="pc.surface_registry",
            readonly=True,
            display_value=json.dumps(preview, indent=2, sort_keys=True),
            help_text="Read-only summary of configured shared admin surfaces.",
        )
    ]
    return [ControlGroup("pc-surface-registry", "Surface Registry", "Read-only composition coverage.", "Console", tuple(items))]


def _engine_control_groups(engine_catalog: Mapping[str, object] | object | None) -> list[ControlGroup]:
    if engine_catalog is None:
        return []
    data = _mapping(engine_catalog)
    groups: list[ControlGroup] = []
    for raw_group in data.get("groups", ()) or ():
        group_data = _mapping(raw_group)
        section = str(group_data.get("section") or "runtime")
        items = tuple(_engine_control_item(raw_control, section) for raw_control in group_data.get("controls", ()) or ())
        groups.append(
            ControlGroup(
                str(group_data.get("key") or "engine-controls"),
                str(group_data.get("label") or group_data.get("title") or "Engine Controls"),
                str(group_data.get("description") or ""),
                str(group_data.get("owner") or "Engine"),
                items,
                metadata={"section": section},  # type: ignore[arg-type]
            )
        )
    return groups


def _engine_control_item(raw_control: Mapping[str, object] | object, section: str) -> ControlItem:
    data = _mapping(raw_control)
    options = tuple(
        ControlOption(
            str(_mapping(option).get("key") or ""),
            str(_mapping(option).get("label") or _mapping(option).get("key") or ""),
            bool(_mapping(option).get("selected", False)),
            bool(_mapping(option).get("disabled", False)),
            str(_mapping(option).get("description") or ""),
        )
        for option in data.get("options", ()) or ()
    )
    source_path = str(data.get("source_path") or data.get("sourcePath") or data.get("name") or data.get("key") or "")
    return ControlItem(
        key=str(data.get("key") or _key(source_path, "engine-control")),
        label=str(data.get("label") or _human_label(source_path)),
        name=source_path,
        kind=str(data.get("kind") or "text"),
        value=data.get("value", ""),
        pending_value=data.get("pending_value", data.get("pendingValue", None)),
        display_value=str(data.get("display_value") or data.get("displayValue") or ""),
        pending_display_value=str(data.get("pending_display_value") or data.get("pendingDisplayValue") or ""),
        placeholder=str(data.get("placeholder") or ""),
        help_text=str(data.get("description") or ""),
        owner=str(data.get("owner") or "Engine"),
        source_path=source_path,
        section=str(data.get("section") or section),
        status=str(data.get("status") or ""),
        tone=str(data.get("tone") or "neutral"),
        required=bool(data.get("required") or False),
        readonly=bool(data.get("readonly") or False),
        disabled=bool(data.get("disabled") or False),
        restart_required=bool(data.get("restart_required") or data.get("restartRequired") or False),
        secret=bool(data.get("secret") or False),
        redacted=bool(data.get("redacted") or False),
        changed=bool(data.get("changed") or False),
        dangerous=bool(data.get("dangerous") or False),
        clearable=bool(data.get("clearable") or False),
        clear_name=str(data.get("clear_name") or data.get("clearName") or ""),
        clear_label=str(data.get("clear_label") or data.get("clearLabel") or "Clear stored value"),
        view_roles=tuple(str(role) for role in data.get("view_roles", data.get("viewRoles", ())) or ()),
        edit_roles=tuple(str(role) for role in data.get("edit_roles", data.get("editRoles", ())) or ()),
        rows=int(data.get("rows") or 4),
        min_value=data.get("min_value", data.get("minValue", "")),
        max_value=data.get("max_value", data.get("maxValue", "")),
        step=data.get("step", ""),
        options=options,
        messages=tuple(data.get("messages", ()) or ()),
        badges=tuple(data.get("badges", ()) or ()),
        actions=tuple(data.get("actions", ()) or ()),
        metadata=_mapping(data.get("metadata")),
    )


def _human_label(value: object) -> str:
    text = str(value or "").split(".")[-1]
    return text.replace("_", " ").replace("-", " ").title()
