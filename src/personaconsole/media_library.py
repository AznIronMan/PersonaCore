from __future__ import annotations

from dataclasses import asdict, fields as dataclass_fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    DashboardFilter,
    DashboardMetric,
    MediaLibraryActionSlot,
    MediaLibraryItem,
    MediaLibraryMetadata,
    MediaLibrarySurfaceConfig,
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

MEDIA_LIBRARY_FEATURE = "media_library"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "high": "bad",
    "unsafe": "bad",
    "warn": "warn",
    "warning": "warn",
    "medium": "warn",
    "pending": "warn",
    "review": "warn",
    "sensitive": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "safe": "good",
    "success": "good",
    "sendable": "good",
    "info": "info",
    "neutral": "neutral",
    "low": "neutral",
    "unknown": "neutral",
    "": "neutral",
}

_IMAGE_TYPES = {"image", "img", "photo", "picture", "jpg", "jpeg", "png", "gif", "webp", "svg"}
_VIDEO_TYPES = {"video", "mp4", "mov", "webm"}
_AUDIO_TYPES = {"audio", "voice", "mp3", "wav", "m4a", "ogg"}


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


def _view(value: object) -> str:
    clean = str(value or "").strip().lower()
    return clean if clean in {"grid", "list"} else "grid"


def _media_kind(value: object) -> str:
    clean = str(value or "").strip().lower()
    if clean in _IMAGE_TYPES:
        return "image"
    if clean in _VIDEO_TYPES:
        return "video"
    if clean in _AUDIO_TYPES:
        return "audio"
    if clean in {"pdf", "document", "file", "text", "archive"}:
        return "file"
    return clean or "file"


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
    return "".join(parts)


def media_library_surface_feature_enabled(
    config: MediaLibrarySurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, MediaLibrarySurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or MEDIA_LIBRARY_FEATURE),
        default=True,
    )


def render_media_library_surface(
    config: MediaLibrarySurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, MediaLibrarySurfaceConfig)
    if not media_library_surface_feature_enabled(model, features):
        return ""

    view = _view(model.view)
    items = [_coerce(item, MediaLibraryItem) for item in model.items]
    controls = _controls_html(model, view=view)
    metrics = _metrics_html(model.metrics)
    action_slots = _action_slots_html(model.action_slots, policy=privacy_policy, context=privacy_context)
    body = (
        _list_html(items, model, policy=privacy_policy, context=privacy_context)
        if view == "list"
        else _grid_html(items, model, policy=privacy_policy, context=privacy_context)
    )
    section_id = str(model.key or "media-library")
    actions = _actions_html(model.actions, class_name="pc-media-library-action", policy=privacy_policy, context=privacy_context)
    header_actions = f'<div class="pc-media-library-actions">{actions}</div>' if actions else ""
    return f"""
<section id="{escape(section_id, quote=True)}" class="pc-dashboard-panel pc-media-library-surface pc-media-library-view-{view}" data-pc-media-library>
  <div class="pc-dashboard-panel-head pc-media-library-head">
    <div class="pc-dashboard-title-group">
      <div class="pc-dashboard-section-title">{escape(str(model.title or "Media Library"))}</div>
      <div class="pc-dashboard-section-meta">{escape(str(model.subtitle or ""))}</div>
    </div>
    {header_actions}
  </div>
  {render_status_tabs(model.status_tabs, aria_label=f"{model.title or 'Media library'} status")}
  {controls}
  {metrics}
  {action_slots}
  {body}
</section>
"""


def _controls_html(model: MediaLibrarySurfaceConfig, *, view: str) -> str:
    filters = "".join(_filter_html(item) for item in model.filters)
    view_options = "".join(_view_option_html(item, active_view=view) for item in model.view_options)
    if not view_options:
        view_options = (
            f'<span class="pc-media-library-view-option{" is-active" if view == "grid" else ""}">Grid</span>'
            f'<span class="pc-media-library-view-option{" is-active" if view == "list" else ""}">List</span>'
        )
    if not filters and not view_options:
        return ""
    return f'<div class="pc-media-library-controls"><div class="pc-dashboard-filters">{filters}</div><div class="pc-media-library-view-switch" aria-label="Media view">{view_options}</div></div>'


def _filter_html(raw_filter: DashboardFilter | Mapping[str, object]) -> str:
    item = _coerce(raw_filter, DashboardFilter)
    if not item.label:
        return ""
    swatch = f'<span class="pc-dashboard-filter-swatch pc-dashboard-tone-{_tone(item.color)}"></span>'
    cls = f'pc-dashboard-filter pc-dashboard-tone-{_tone(item.color)}{" is-active" if item.active else ""}'
    href = _safe_url(item.href)
    body = f"{swatch}<span>{escape(str(item.label))}</span>"
    return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>' if href else f'<span class="{cls}">{body}</span>'


def _view_option_html(raw_filter: DashboardFilter | Mapping[str, object], *, active_view: str) -> str:
    item = _coerce(raw_filter, DashboardFilter)
    if not item.label:
        return ""
    key = str(item.key or item.label).strip().lower()
    active = item.active or key == active_view
    cls = f'pc-media-library-view-option{" is-active" if active else ""}'
    href = _safe_url(item.href)
    body = escape(str(item.label))
    return f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>' if href else f'<span class="{cls}">{body}</span>'


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
        cls = f"pc-dashboard-stat pc-media-library-metric pc-dashboard-tone-{_tone(metric.tone)}"
        href = _safe_url(metric.href)
        cards.append(f'<a class="{cls}" href="{escape(href, quote=True)}">{body}</a>' if href else f'<div class="{cls}">{body}</div>')
    return f'<div class="pc-dashboard-stat-grid pc-media-library-metrics">{"".join(cards)}</div>' if cards else ""


def _grid_html(
    items: Sequence[MediaLibraryItem],
    model: MediaLibrarySurfaceConfig,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not items:
        return f'<div class="pc-dashboard-empty pc-media-library-empty">{escape(str(model.empty_label))}</div>'
    cards = "".join(_item_card_html(item, policy=policy, context=context) for item in items)
    return f'<div class="pc-media-library-grid" aria-label="{escape(str(model.grid_label), quote=True)}">{cards}</div>'


def _list_html(
    items: Sequence[MediaLibraryItem],
    model: MediaLibrarySurfaceConfig,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not items:
        return f'<div class="pc-dashboard-empty pc-media-library-empty">{escape(str(model.empty_label))}</div>'
    rows = "".join(_item_row_html(item, policy=policy, context=context) for item in items)
    return f"""
<div class="pc-media-library-table-wrap">
  <table class="pc-media-library-table" aria-label="{escape(str(model.list_label), quote=True)}">
    <thead><tr><th>Media</th><th>Posture</th><th>Source</th><th>Actions</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>
"""


def _item_card_html(
    item: MediaLibraryItem,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    title = _item_title_html(item, policy=policy, context=context)
    preview = _preview_html(item, policy=policy, context=context)
    meta = _metadata_html(item, policy=policy, context=context)
    flags = _flag_badges_html(item)
    badges = _badges_html(item.badges)
    actions = _actions_html(item.actions, class_name="pc-media-library-item-action", policy=policy, context=context)
    action_html = f'<div class="pc-media-library-item-actions">{actions}</div>' if actions else ""
    detail = _private_text(item.detail, privacy_scope=item.privacy_scope, safe_alternate=item.safe_alternate, policy=policy, context=context)
    detail_html = f'<p>{escape(str(detail))}</p>' if detail else ""
    custom_detail_html = str(item.detail_html or "") if _raw_html_allowed(item.privacy_scope, policy=policy, context=context) else ""
    classes = [
        "pc-media-library-card",
        f"pc-dashboard-tone-{_tone(item.tone)}",
        f"pc-media-library-kind-{_media_kind(item.media_type)}",
    ]
    if item.selected:
        classes.append("is-selected")
    if item.blur_sensitive:
        classes.append("is-sensitive")
    classes.append(_private_class(privacy_scope=item.privacy_scope, policy=policy, context=context))
    return (
        f'<article class="{" ".join(part for part in classes if part)}">'
        f"{preview}<div class=\"pc-media-library-card-copy\">{title}{flags}{badges}{meta}{detail_html}{custom_detail_html}{action_html}</div></article>"
    )


def _item_row_html(
    item: MediaLibraryItem,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    title = _item_title_html(item, policy=policy, context=context)
    preview = _preview_html(item, compact=True, policy=policy, context=context)
    detail = _private_text(item.detail, privacy_scope=item.privacy_scope, safe_alternate=item.safe_alternate, policy=policy, context=context)
    custom_detail_html = str(item.detail_html or "") if _raw_html_allowed(item.privacy_scope, policy=policy, context=context) else ""
    actions = _actions_html(item.actions, class_name="pc-media-library-item-action", policy=policy, context=context)
    source = _source_html(item)
    flags = _flag_badges_html(item)
    meta = _metadata_html(item, policy=policy, context=context, limit=3)
    private = _private_class(privacy_scope=item.privacy_scope, policy=policy, context=context)
    return f"""
<tr class="{private}">
  <td><div class="pc-media-library-row-media">{preview}<div>{title}{f'<p>{escape(str(detail))}</p>' if detail else ''}{custom_detail_html}</div></div></td>
  <td>{flags}{meta}</td>
  <td>{source}</td>
  <td><div class="pc-media-library-item-actions">{actions}</div></td>
</tr>
"""


def _item_title_html(
    item: MediaLibraryItem,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    label = _private_text(item.label, privacy_scope=item.privacy_scope, safe_alternate=item.safe_alternate, policy=policy, context=context)
    href = _private_url(item.href, privacy_scope=item.privacy_scope, policy=policy, context=context)
    status = f'<span class="pc-surface-status pc-dashboard-tone-{_tone(item.tone)}">{escape(str(item.status))}</span>' if item.status else ""
    title = escape(str(label or "Media item"))
    if href:
        title = f'<a href="{escape(href, quote=True)}">{title}</a>'
    meta_bits = [
        f"<span>{escape(str(item.media_type))}</span>" if item.media_type else "",
        f"<time>{escape(str(item.timestamp))}</time>" if item.timestamp else "",
    ]
    meta = "".join(bit for bit in meta_bits if bit)
    return (
        '<div class="pc-media-library-title-row">'
        f"<strong>{title}</strong>{status}</div>"
        + (f'<div class="pc-surface-row-meta">{meta}</div>' if meta else "")
    )


def _preview_html(
    item: MediaLibraryItem,
    *,
    compact: bool = False,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    preview = _private_url(item.preview_url, privacy_scope=item.privacy_scope, policy=policy, context=context)
    kind = _media_kind(item.media_type)
    alt = _private_text(item.preview_alt or item.label, privacy_scope=item.privacy_scope, safe_alternate=item.safe_alternate, policy=policy, context=context)
    sensitive = " is-sensitive" if item.blur_sensitive else ""
    compact_cls = " pc-media-library-preview-compact" if compact else ""
    placeholder = _placeholder_html(kind, label=item.media_type or "media")
    if not preview:
        return f'<div class="pc-media-library-preview pc-media-library-preview-empty{compact_cls}{sensitive}">{placeholder}</div>'
    if kind == "image":
        media = f'<img src="{escape(preview, quote=True)}" alt="{escape(str(alt), quote=True)}" loading="lazy">'
    elif kind == "video":
        media = f'<video muted playsinline preload="metadata"><source src="{escape(preview, quote=True)}"></video>'
    elif kind == "audio":
        media = f'<audio controls preload="none" src="{escape(preview, quote=True)}"></audio>'
    else:
        media = placeholder
    trigger = ""
    if not compact:
        trigger = (
            '<details class="pc-media-library-dialog">'
            '<summary>Preview</summary>'
            f'<div class="pc-media-library-dialog-panel" role="dialog" aria-label="{escape(str(alt or item.label or "Media preview"), quote=True)}">{media}</div>'
            "</details>"
        )
    return f'<figure class="pc-media-library-preview pc-media-library-preview-{kind}{compact_cls}{sensitive}">{media}{trigger}</figure>'


def _placeholder_html(kind: str, *, label: str) -> str:
    icon = {"image": "IMG", "video": "VID", "audio": "AUD", "file": "FILE"}.get(kind, "MEDIA")
    return f'<span class="pc-media-library-placeholder-icon">{escape(icon)}</span><span>{escape(str(label or kind).upper())}</span>'


def _metadata_html(
    item: MediaLibraryItem,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
    limit: int = 8,
) -> str:
    chips = []
    for raw_meta in item.metadata[:limit]:
        meta = _coerce(raw_meta, MediaLibraryMetadata)
        if not meta.label and not meta.key:
            continue
        value = _private_text(meta.value, privacy_scope=meta.privacy_scope or item.privacy_scope, safe_alternate=meta.safe_alternate or item.safe_alternate, policy=policy, context=context)
        if value in ("", None):
            continue
        label = str(meta.label or meta.key)
        chips.append(f'<span class="pc-media-library-meta pc-dashboard-tone-{_tone(meta.tone)}"><b>{escape(label)}</b>{escape(str(value))}</span>')
    return f'<div class="pc-media-library-meta-list">{"".join(chips)}</div>' if chips else ""


def _flag_badges_html(item: MediaLibraryItem) -> str:
    flags = [
        ("review", item.review_status, _tone(item.review_status)),
        ("safety", item.safety, _safety_tone(item.safety)),
        ("send", item.sendability, _sendability_tone(item.sendability)),
        ("heat", item.heat, _heat_tone(item.heat)),
        ("share", item.shareability, _sendability_tone(item.shareability)),
    ]
    body = "".join(
        f'<span class="pc-media-library-flag pc-dashboard-tone-{tone}"><b>{escape(label)}</b>{escape(str(value))}</span>'
        for label, value, tone in flags
        if str(value or "").strip()
    )
    return f'<div class="pc-media-library-flags">{body}</div>' if body else ""


def _source_html(item: MediaLibraryItem) -> str:
    parts = [
        f"<span><b>Owner</b>{escape(str(item.owner))}</span>" if item.owner else "",
        f"<span><b>Source</b>{escape(str(item.source))}</span>" if item.source else "",
    ]
    body = "".join(part for part in parts if part)
    return f'<div class="pc-media-library-source">{body}</div>' if body else '<span class="pc-media-library-muted">-</span>'


def _action_slots_html(
    slots: Sequence[MediaLibraryActionSlot | Mapping[str, object]],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    cards = []
    for raw_slot in slots:
        slot = _coerce(raw_slot, MediaLibraryActionSlot)
        if not slot.label:
            continue
        body_text = _private_text(slot.body, privacy_scope=slot.privacy_scope, safe_alternate=slot.safe_alternate, policy=policy, context=context)
        body = f'<p>{escape(str(body_text))}</p>' if body_text else ""
        body += str(slot.body_html or "")
        actions = _actions_html(slot.actions, class_name="pc-media-library-slot-action", policy=policy, context=context)
        action_html = f'<div class="pc-media-library-slot-actions">{actions}</div>' if actions else ""
        cards.append(
            f'<section id="{escape(str(slot.key), quote=True)}" class="pc-media-library-action-slot pc-dashboard-tone-{_tone(slot.tone)}">'
            f'<h3>{escape(str(slot.label))}</h3><small>{escape(str(slot.description or ""))}</small>{body}{action_html}</section>'
        )
    return f'<div class="pc-media-library-action-slots">{"".join(cards)}</div>' if cards else ""


def _actions_html(
    actions: Sequence[SurfaceAction | Mapping[str, object]],
    *,
    class_name: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    body = []
    for raw_action in actions:
        action = _coerce(raw_action, SurfaceAction)
        if not action.label:
            continue
        href = _private_url(action.href, privacy_scope="", policy=policy, context=context)
        method = str(action.method or "").strip().lower()
        method_attr = _attrs(data_method=method) if method and method != "get" else ""
        title = _attrs(title=action.title)
        cls = f"{class_name} pc-dashboard-tone-{_tone(action.tone)}"
        if action.disabled or not href:
            body.append(f'<span class="{cls} is-disabled"{title}>{escape(str(action.label))}</span>')
        else:
            body.append(f'<a class="{cls}" href="{escape(href, quote=True)}"{method_attr}{title}>{escape(str(action.label))}</a>')
    return "".join(body)


def _badge_html(raw_badge: SurfaceBadge | Mapping[str, object] | str) -> str:
    badge = SurfaceBadge(str(raw_badge)) if isinstance(raw_badge, str) else _coerce(raw_badge, SurfaceBadge)
    if not badge.label:
        return ""
    return f'<span class="pc-surface-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-surface-badges pc-media-library-badges">{body}</div>' if body else ""


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


def _private_url(
    url: str,
    *,
    privacy_scope: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    safe = _safe_url(url)
    if not safe or not privacy_scope:
        return safe
    if policy is None:
        return ""
    if not policy.is_owner_private_scope(privacy_scope):
        return safe
    return safe if can_view_raw_private(policy, context, privacy_scope) else ""


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


def _raw_html_allowed(
    privacy_scope: str,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> bool:
    if not privacy_scope:
        return True
    if policy is None:
        return False
    if not policy.is_owner_private_scope(privacy_scope):
        return True
    return can_view_raw_private(policy, context, privacy_scope)


def _safe_url(value: object) -> str:
    clean = str(value or "").strip()
    lowered = clean.lower()
    if not clean:
        return ""
    if any(char in clean for char in ("\x00", "\n", "\r", "\t", "\\")):
        return ""
    if lowered.startswith(("http://", "https://", "javascript:", "data:", "mailto:", "tel:", "//")):
        return ""
    if clean.startswith("#"):
        return clean if " " not in clean else ""
    if not clean.startswith("/"):
        return ""
    if clean.startswith("//") or "://" in clean:
        return ""
    private_fragments = ("/.private", "/private/", "/secrets", "/secret", "/token", "/callback", "/oauth")
    if any(fragment in lowered for fragment in private_fragments):
        return ""
    return clean


def _safety_tone(value: object) -> str:
    clean = str(value or "").strip().lower()
    if clean in {"unsafe", "blocked", "adult", "restricted", "failed"}:
        return "bad"
    if clean in {"review", "sensitive", "pending", "needs_review"}:
        return "warn"
    if clean in {"safe", "approved", "clean"}:
        return "good"
    return _tone(clean)


def _sendability_tone(value: object) -> str:
    clean = str(value or "").strip().lower()
    if clean in {"blocked", "no", "not_sendable", "unsafe"}:
        return "bad"
    if clean in {"review", "manual", "queued", "pending"}:
        return "warn"
    if clean in {"sendable", "shareable", "ready", "yes", "approved"}:
        return "good"
    return _tone(clean)


def _heat_tone(value: object) -> str:
    clean = str(value or "").strip().lower()
    if clean in {"high", "hot", "spicy"}:
        return "warn"
    if clean in {"blocked", "unsafe"}:
        return "bad"
    if clean in {"low", "cool", "safe"}:
        return "good"
    return _tone(clean)
