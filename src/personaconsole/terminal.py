from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, TypeVar

from .models import SurfaceBadge, TerminalStreamConfig, TerminalStreamEvent
from .privacy import (
    WITHHELD_PRIVATE_TEXT,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    PrivacyRenderMode,
    feature_enabled,
    privacy_render_mode,
    render_private_text,
)

TERMINAL_STREAM_FEATURE = "terminal_stream"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "critical": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "fail": "bad",
    "warn": "warn",
    "warning": "warn",
    "held": "warn",
    "pending": "warn",
    "queued": "warn",
    "review": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "info": "info",
    "neutral": "neutral",
    "unknown": "neutral",
    "": "neutral",
}

_ROLE_ALIASES = {
    "command": "input",
    "cmd": "input",
    "human": "input",
    "input": "input",
    "operator": "input",
    "prompt": "input",
    "user": "input",
    "assistant": "output",
    "codex": "output",
    "out": "output",
    "output": "output",
    "stdout": "output",
    "err": "error",
    "error": "error",
    "stderr": "error",
    "fail": "error",
    "failed": "error",
    "note": "system",
    "status": "system",
    "system": "system",
    "tool": "tool",
    "tool_call": "tool",
    "tool_result": "tool",
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


def _role(value: object) -> str:
    return _ROLE_ALIASES.get(str(value or "").strip().lower(), "output")


def _int(value: object, default: int, *, minimum: int = 0) -> int:
    try:
        parsed = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        parsed = default
    return max(minimum, parsed)


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
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
    return f'<span class="pc-terminal-badge pc-dashboard-tone-{_tone(badge.tone)}">{escape(str(badge.label))}</span>'


def _badges_html(badges: Any) -> str:
    body = "".join(_badge_html(badge) for badge in badges or ())
    return f'<span class="pc-terminal-badges">{body}</span>' if body else ""


def terminal_stream_feature_enabled(
    config: TerminalStreamConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, TerminalStreamConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or TERMINAL_STREAM_FEATURE), default=True)


def _event_html(
    raw_event: TerminalStreamEvent | Mapping[str, object],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    event = _coerce(raw_event, TerminalStreamEvent, {"key": "", "text": ""})
    role = _role(event.role)
    tone = _tone(event.tone)
    private = _private_class(privacy_scope=event.privacy_scope, policy=policy, context=context)
    text = _private_text(
        event.text,
        privacy_scope=event.privacy_scope,
        safe_alternate=event.safe_alternate,
        policy=policy,
        context=context,
    )
    meta = "".join(
        part
        for part in [
            f'<span class="pc-terminal-sequence">{escape(str(event.sequence))}</span>' if event.sequence != "" else "",
            f'<time>{escape(str(event.timestamp))}</time>' if event.timestamp else "",
            f'<span>{escape(str(event.source))}</span>' if event.source else "",
        ]
    )
    label = event.label or role
    truncated = '<span class="pc-terminal-truncated">truncated</span>' if event.truncated else ""
    return (
        f'<article class="pc-terminal-event pc-terminal-role-{role} pc-dashboard-tone-{tone}{private}"'
        f'{_attrs(data_event_key=str(event.key), data_event_role=role)}>'
        '<div class="pc-terminal-event-gutter">'
        f'<span class="pc-terminal-role-label">{escape(str(label))}</span>'
        "</div>"
        '<div class="pc-terminal-event-main">'
        + (f'<div class="pc-terminal-event-meta">{meta}{_badges_html(event.badges)}{truncated}</div>' if meta or event.badges or truncated else "")
        + f'<span class="pc-terminal-text">{escape(text)}</span>'
        "</div>"
        "</article>"
    )


def render_terminal_stream(
    config: TerminalStreamConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, TerminalStreamConfig)
    if not terminal_stream_feature_enabled(model, features):
        return ""

    max_events = _int(model.max_rendered_events, 200, minimum=1)
    events = tuple(model.events or ())
    truncated_before = bool(model.truncated_before)
    if len(events) > max_events:
        events = events[-max_events:]
        truncated_before = True
    event_html = "".join(
        _event_html(event, policy=privacy_policy, context=privacy_context)
        for event in events
    )
    empty = f'<div class="pc-dashboard-empty">{escape(str(model.empty_label))}</div>' if not event_html else ""
    status = (
        f'<span class="pc-surface-status pc-dashboard-tone-{_tone(model.status_tone or model.status)}">'
        f'{escape(str(model.status))}</span>'
        if model.status
        else ""
    )
    has_earlier = bool(model.has_more_before or truncated_before)
    history_disabled = "" if model.history_url and has_earlier else " disabled"
    history_button = (
        '<button type="button" class="pc-terminal-history" data-pc-terminal-history'
        f'{history_disabled}>Load earlier</button>'
        if model.history_url or has_earlier
        else ""
    )
    live = '<span class="pc-terminal-live-dot" aria-hidden="true"></span>' if model.stream_url and model.has_more_after else ""
    notices = "".join(
        part
        for part in [
            '<span class="pc-terminal-window-note">older history is buffered</span>' if has_earlier else "",
            '<span class="pc-terminal-window-note">newer events available by stream</span>' if model.has_more_after and model.stream_url else "",
            '<span class="pc-terminal-window-note">tail truncated</span>' if model.truncated_after else "",
        ]
    )
    header = (
        '<div class="pc-terminal-head">'
        '<div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        '</div>'
        f'<div class="pc-terminal-state">{live}{status}</div>'
        '</div>'
    )
    toolbar = (
        '<div class="pc-terminal-toolbar">'
        f'<span>{escape(str(model.window_label))}</span>'
        f'{notices}'
        f'{history_button}'
        '</div>'
    )
    attrs = _attrs(
        data_stream_url=str(model.stream_url),
        data_history_url=str(model.history_url),
        data_after_cursor=str(model.after_cursor),
        data_before_cursor=str(model.before_cursor),
        data_max_events=str(max_events),
        data_poll_interval=str(_int(model.poll_interval_ms, 4000, minimum=1000)),
        data_autoscroll="true" if model.autoscroll else "false",
        data_initial_position=str(model.initial_position or "current"),
        data_readonly="true",
    )
    return (
        f'<section id="{escape(str(model.key), quote=True)}" class="pc-terminal-stream pc-dashboard-panel"'
        ' data-pc-terminal-stream'
        f'{attrs}>'
        f'{header}{toolbar}'
        '<div class="pc-terminal-viewport" role="log" aria-live="polite" aria-relevant="additions text">'
        f'<div class="pc-terminal-events" data-pc-terminal-events>{event_html}</div>{empty}'
        '</div>'
        '<noscript><p class="pc-dashboard-empty">Live terminal updates require JavaScript; the current buffered window is shown.</p></noscript>'
        '</section>'
    )
