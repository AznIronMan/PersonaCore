from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    ActivityEvent,
    ActivitySurfaceConfig,
    DashboardAction,
    DashboardFilter,
    DashboardMetric,
    MediaArtifactCard,
    MediaSurfaceConfig,
    MessageAttachment,
    MessageConversation,
    MessageSurfaceConfig,
    MessageTranscriptItem,
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

T = TypeVar("T")

MESSAGES_FEATURE = "messages"
ACTIVITY_FEATURE = "activity"
MEDIA_FEATURE = "media"

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "red": "bad",
    "rose": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
    "lagging": "warn",
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
    "unknown": "neutral",
    "": "neutral",
}

_DIRECTION_ALIASES = {
    "in": "incoming",
    "inbound": "incoming",
    "incoming": "incoming",
    "received": "incoming",
    "out": "outgoing",
    "outbound": "outgoing",
    "outgoing": "outgoing",
    "sent": "outgoing",
    "system": "system",
    "note": "system",
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


def _direction(value: object) -> str:
    return _DIRECTION_ALIASES.get(str(value or "").strip().lower(), "incoming")


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
    return "".join(parts)


def _link_or_tag(tag: str, href: str, class_name: str, body: str, *, title: str = "") -> str:
    if href:
        return f'<a class="{class_name}" href="{escape(href, quote=True)}"{_attrs(title=title)}>{body}</a>'
    return f'<{tag} class="{class_name}"{_attrs(title=title)}>{body}</{tag}>'


def _badge_html(raw_badge: SurfaceBadge | Mapping[str, object] | str) -> str:
    badge = SurfaceBadge(str(raw_badge)) if isinstance(raw_badge, str) else _coerce(raw_badge, SurfaceBadge)
    if not badge.label:
        return ""
    return f'<span class="pc-surface-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Sequence[SurfaceBadge | Mapping[str, object] | str]) -> str:
    body = "".join(_badge_html(badge) for badge in badges)
    return f'<div class="pc-surface-badges">{body}</div>' if body else ""


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


def _panel_head(title: str, subtitle: str) -> str:
    return (
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(subtitle))}</div>'
        "</div></div>"
    )


def _message_filters_html(filters: Sequence[DashboardFilter | Mapping[str, object]]) -> str:
    chips: list[str] = []
    for raw_filter in filters:
        item = _coerce(raw_filter, DashboardFilter)
        if not item.label:
            continue
        active = " is-active" if item.active else ""
        swatch = ""
        if item.color:
            swatch = (
                '<span class="pc-message-filter-swatch" aria-hidden="true" '
                f'style="background: {escape(item.color, quote=True)}"></span>'
            )
        key = f"<small>{escape(str(item.key))}</small>" if item.key else ""
        chips.append(
            f'<a class="pc-message-filter{active}" href="{escape(item.href or "#", quote=True)}">'
            f'{swatch}<span>{escape(str(item.label))}</span>{key}</a>'
        )
    if not chips:
        return ""
    return '<nav class="pc-message-filters" aria-label="Message filters">' + "".join(chips) + "</nav>"


def _message_actions_html(actions: Sequence[DashboardAction | Mapping[str, object]]) -> str:
    links: list[str] = []
    for raw_action in actions:
        item = _coerce(raw_action, DashboardAction)
        if not item.label or not item.href:
            continue
        links.append(
            f'<a class="pc-message-action pc-dashboard-tone-{_tone(item.tone)}" '
            f'href="{escape(str(item.href), quote=True)}">{escape(str(item.label))}</a>'
        )
    if not links:
        return ""
    return '<div class="pc-message-actions">' + "".join(links) + "</div>"


def _message_metrics_html(metrics: Sequence[DashboardMetric | Mapping[str, object]]) -> str:
    cards: list[str] = []
    for raw_metric in metrics:
        item = _coerce(raw_metric, DashboardMetric)
        if not item.label:
            continue
        body = (
            f'<span>{escape(str(item.label))}</span>'
            f'<strong>{escape(str(item.value))}</strong>'
            + (f'<em>{escape(str(item.detail))}</em>' if item.detail else "")
        )
        cards.append(
            _link_or_tag(
                "div",
                item.href,
                f"pc-message-metric pc-dashboard-tone-{_tone(item.tone)}",
                body,
            )
        )
    if not cards:
        return ""
    return '<div class="pc-message-metrics">' + "".join(cards) + "</div>"


def message_surface_feature_enabled(
    config: MessageSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, MessageSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or MESSAGES_FEATURE),
        default=True,
    )


def activity_surface_feature_enabled(
    config: ActivitySurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, ActivitySurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or ACTIVITY_FEATURE),
        default=True,
    )


def media_surface_feature_enabled(
    config: MediaSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, MediaSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or MEDIA_FEATURE),
        default=True,
    )


def _conversation_html(
    raw_item: MessageConversation | Mapping[str, object],
    *,
    selected_key: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    item = _coerce(raw_item, MessageConversation)
    summary = _private_text(
        item.summary,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(item.href, privacy_scope=item.privacy_scope, policy=policy, context=context)
    selected = " is-active" if item.key and item.key == selected_key else ""
    private = _private_class(privacy_scope=item.privacy_scope, policy=policy, context=context)
    unread = f'<span class="pc-message-unread">{int(item.unread)}</span>' if int(item.unread or 0) > 0 else ""
    provider = f'<span class="pc-message-provider">{escape(str(item.provider))}</span>' if item.provider else ""
    participant = f'<span>{escape(str(item.participant))}</span>' if item.participant else ""
    body = (
        '<div class="pc-message-conversation-top">'
        f'<strong>{escape(str(item.label))}</strong>'
        f'<time>{escape(str(item.timestamp))}</time>'
        "</div>"
        '<div class="pc-message-conversation-meta">'
        f"{provider}{participant}{unread}</div>"
        + (f'<div class="pc-message-summary">{escape(summary)}</div>' if summary else "")
        + _badges_html(item.badges)
    )
    return _link_or_tag(
        "article",
        href,
        f"pc-message-conversation pc-dashboard-tone-{_tone(item.tone)}{selected}{private}",
        body,
    )


def _attachment_html(
    raw_item: MessageAttachment | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    item = _coerce(raw_item, MessageAttachment)
    label = _private_text(
        item.label,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        item.detail,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(item.href, privacy_scope=item.privacy_scope, policy=policy, context=context)
    preview = _raw_href(item.preview_url, privacy_scope=item.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=item.privacy_scope, policy=policy, context=context)
    preview_html = (
        f'<img class="pc-surface-preview" src="{escape(preview, quote=True)}" alt="" loading="lazy">'
        if preview
        else ""
    )
    body = (
        preview_html
        + '<span class="pc-message-attachment-copy">'
        f'<strong>{escape(label)}</strong>'
        + (f'<em>{escape(str(item.media_type))}</em>' if item.media_type else "")
        + (f'<small>{escape(detail)}</small>' if detail else "")
        + "</span>"
        + (f'<span class="pc-surface-status pc-dashboard-tone-{_tone(item.tone)}">{escape(str(item.status))}</span>' if item.status else "")
    )
    return _link_or_tag(
        "span",
        href,
        f"pc-message-attachment pc-dashboard-tone-{_tone(item.tone)}{private}",
        body,
    )


def _transcript_html(
    raw_item: MessageTranscriptItem | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    item = _coerce(raw_item, MessageTranscriptItem)
    text = _private_text(
        item.text,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(item.href, privacy_scope=item.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=item.privacy_scope, policy=policy, context=context)
    attachments = "".join(_attachment_html(raw, policy=policy, context=context) for raw in item.attachments)
    provider = f'<span>{escape(str(item.provider))}</span>' if item.provider else ""
    meta = f'<small>{escape(str(item.meta))}</small>' if item.meta else ""
    body = (
        '<div class="pc-message-bubble-head">'
        f'<strong>{escape(str(item.sender))}</strong>{provider}<time>{escape(str(item.timestamp))}</time>'
        "</div>"
        + (f'<div class="pc-message-bubble-text">{escape(text)}</div>' if text else "")
        + (f'<div class="pc-message-attachments">{attachments}</div>' if attachments else "")
        + meta
    )
    return _link_or_tag(
        "article",
        href,
        f"pc-message-bubble pc-message-{_direction(item.direction)} pc-dashboard-tone-{_tone(item.tone)}{private}",
        body,
    )


def render_message_surface(
    config: MessageSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, MessageSurfaceConfig)
    if not message_surface_feature_enabled(model, features):
        return ""
    conversations = [
        _conversation_html(item, selected_key=model.selected_key, policy=privacy_policy, context=privacy_context)
        for item in model.conversations
    ]
    transcript = [
        _transcript_html(item, policy=privacy_policy, context=privacy_context)
        for item in model.transcript
    ]
    conversation_body = (
        "".join(conversations)
        if conversations
        else f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    )
    transcript_body = (
        "".join(transcript)
        if transcript
        else f'<div class="pc-dashboard-empty">{escape(str(model.transcript_empty_label))}</div>'
    )
    filters = _message_filters_html(model.filters)
    actions = _message_actions_html(model.actions)
    metrics = _message_metrics_html(model.metrics)
    controls = (
        f'<div class="pc-message-controls">{filters}{actions}</div>'
        if filters or actions
        else ""
    )
    transcript_meta = f'<em>{escape(str(model.transcript_meta))}</em>' if model.transcript_meta else ""
    return (
        '<section id="messages" class="pc-message-surface pc-dashboard-panel">'
        f"{_panel_head(model.title, model.subtitle)}"
        f"{controls}"
        f"{metrics}"
        '<div class="pc-message-layout">'
        '<div class="pc-message-conversation-list">'
        '<div class="pc-message-column-head">'
        f'<strong>{escape(str(model.conversation_title))}</strong>'
        f'<em>{len(conversations)}</em></div>'
        f"{conversation_body}</div>"
        '<div class="pc-message-transcript">'
        '<div class="pc-message-column-head">'
        f'<strong>{escape(str(model.transcript_title))}</strong>{transcript_meta}</div>'
        f"{transcript_body}</div>"
        "</div></section>"
    )


def _activity_event_html(
    raw_item: ActivityEvent | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    item = _coerce(raw_item, ActivityEvent)
    title = _private_text(
        item.title,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    summary = _private_text(
        item.summary,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(item.href, privacy_scope=item.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=item.privacy_scope, policy=policy, context=context)
    provider = f'<span class="pc-message-provider">{escape(str(item.provider))}</span>' if item.provider else ""
    row_meta = provider + _badges_html(item.badges)
    body = (
        '<span class="pc-dashboard-activity-dot" aria-hidden="true"></span>'
        '<div class="pc-dashboard-activity-main">'
        '<div class="pc-dashboard-activity-title-row">'
        f'<span class="pc-dashboard-activity-label">{escape(str(item.label))}</span>'
        f"<strong>{escape(title)}</strong>"
        f"<time>{escape(str(item.timestamp))}</time></div>"
        + (f'<div class="pc-surface-row-meta">{row_meta}</div>' if row_meta else "")
        + (f'<div class="pc-dashboard-activity-summary">{escape(summary)}</div>' if summary else "")
        + (f'<div class="pc-dashboard-activity-meta">{escape(str(item.meta))}</div>' if item.meta else "")
        + "</div>"
    )
    return _link_or_tag(
        "article",
        href,
        f"pc-surface-activity-item pc-dashboard-activity-item pc-dashboard-tone-{_tone(item.tone)}{private}",
        body,
    )


def render_activity_surface(
    config: ActivitySurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, ActivitySurfaceConfig)
    if not activity_surface_feature_enabled(model, features):
        return ""
    rows = [_activity_event_html(item, policy=privacy_policy, context=privacy_context) for item in model.events]
    body = (
        '<div class="pc-dashboard-activity-list">' + "".join(rows) + "</div>"
        if rows
        else f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    )
    return (
        '<section id="activity" class="pc-activity-surface pc-dashboard-panel">'
        f"{_panel_head(model.title, model.subtitle)}"
        f"{body}</section>"
    )


def _media_card_html(
    raw_item: MediaArtifactCard | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    item = _coerce(raw_item, MediaArtifactCard)
    label = _private_text(
        item.label,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    detail = _private_text(
        item.detail,
        privacy_scope=item.privacy_scope,
        safe_alternate=item.safe_alternate,
        policy=policy,
        context=context,
    )
    href = _raw_href(item.href, privacy_scope=item.privacy_scope, policy=policy, context=context)
    preview = _raw_href(item.preview_url, privacy_scope=item.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=item.privacy_scope, policy=policy, context=context)
    preview_html = (
        '<div class="pc-media-preview">'
        f'<img src="{escape(preview, quote=True)}" alt="" loading="lazy">'
        "</div>"
        if preview
        else '<div class="pc-media-preview pc-media-preview-empty" aria-hidden="true"></div>'
    )
    provider = f'<span class="pc-message-provider">{escape(str(item.provider))}</span>' if item.provider else ""
    status = (
        f'<span class="pc-surface-status pc-dashboard-tone-{_tone(item.tone)}">{escape(str(item.status))}</span>'
        if item.status
        else ""
    )
    meta_parts = [
        provider,
        f"<span>{escape(str(item.media_type))}</span>" if item.media_type else "",
        f"<time>{escape(str(item.timestamp))}</time>" if item.timestamp else "",
    ]
    row_meta = "".join(part for part in meta_parts if part)
    body = (
        preview_html
        + '<div class="pc-media-copy">'
        '<div class="pc-media-title-row">'
        f'<strong>{escape(label)}</strong>'
        f"{status}"
        "</div>"
        + (f'<div class="pc-surface-row-meta">{row_meta}</div>' if row_meta else "")
        + (f'<div class="pc-media-detail">{escape(detail)}</div>' if detail else "")
        + _badges_html(item.badges)
        + "</div>"
    )
    return _link_or_tag(
        "article",
        href,
        f"pc-media-card pc-dashboard-tone-{_tone(item.tone)}{private}",
        body,
    )


def render_media_surface(
    config: MediaSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, MediaSurfaceConfig)
    if not media_surface_feature_enabled(model, features):
        return ""
    cards = [_media_card_html(item, policy=privacy_policy, context=privacy_context) for item in model.cards]
    body = (
        '<div class="pc-media-grid">' + "".join(cards) + "</div>"
        if cards
        else f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>'
    )
    return (
        '<section id="media" class="pc-media-surface pc-dashboard-panel">'
        f"{_panel_head(model.title, model.subtitle)}"
        f"{body}</section>"
    )


def render_surface_sections(
    *,
    messages: MessageSurfaceConfig | Mapping[str, object] | None = None,
    activity: ActivitySurfaceConfig | Mapping[str, object] | None = None,
    media: MediaSurfaceConfig | Mapping[str, object] | None = None,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    sections = [
        render_message_surface(
            messages,
            features=features,
            privacy_policy=privacy_policy,
            privacy_context=privacy_context,
        ),
        render_activity_surface(
            activity,
            features=features,
            privacy_policy=privacy_policy,
            privacy_context=privacy_context,
        ),
        render_media_surface(
            media,
            features=features,
            privacy_policy=privacy_policy,
            privacy_context=privacy_context,
        ),
    ]
    return "\n".join(section for section in sections if section)
