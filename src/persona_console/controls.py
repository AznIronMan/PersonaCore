from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from time import time
from typing import Any, Mapping, Sequence, TypeVar
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import FlashBanner, StatusTab

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "red": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
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


def render_status_tabs(
    tabs: Sequence[StatusTab | Mapping[str, object]],
    *,
    aria_label: str = "Status filters",
    empty_label: str = "",
) -> str:
    """Render dense status tabs for review queues and filtered list pages."""

    items = [_coerce(tab, StatusTab) for tab in tabs]
    body = "".join(_status_tab_html(item) for item in items if item.label)
    if not body and empty_label:
        body = f'<span class="status-tab pc-status-tab is-empty">{escape(str(empty_label))}</span>'
    if not body:
        return ""
    return (
        f'<nav class="status-tabs pc-status-tabs" aria-label="{escape(str(aria_label), quote=True)}">'
        f"{body}</nav>"
    )


def _status_tab_html(tab: StatusTab) -> str:
    tone = _tone(tab.tone)
    classes = ["status-tab", "pc-status-tab", f"pc-status-tab-{tone}"]
    if tab.active:
        classes.append("is-active")
    label = f'<span class="pc-status-tab-label">{escape(str(tab.label))}</span>'
    count = str(tab.count)
    count_html = ""
    if count:
        count_html = (
            '<span class="status-tab-count pc-status-tab-count">'
            f"{escape(count)}</span>"
        )
    attrs = f'class="{" ".join(classes)}"'
    if tab.title:
        attrs += f' title="{escape(str(tab.title), quote=True)}"'
    if tab.href:
        return f'<a {attrs} href="{escape(str(tab.href), quote=True)}">{label}{count_html}</a>'
    return f"<span {attrs}>{label}{count_html}</span>"


def flash_query_params(
    message: object,
    *,
    level: object = "good",
    timestamp: object | None = None,
) -> dict[str, str]:
    """Build the shared flash-message query parameters used by the shell JS."""

    stamp = int(time()) if timestamp is None else timestamp
    return {
        "flash": str(message or ""),
        "flash_level": _flash_tone(level),
        "flash_ts": str(stamp),
    }


def flash_url(
    href: str,
    message: object,
    *,
    level: object = "good",
    timestamp: object | None = None,
) -> str:
    """Append shared flash query parameters while preserving query and fragment."""

    parts = urlsplit(str(href or ""))
    query = [
        (key, value)
        for key, value in parse_qsl(parts.query, keep_blank_values=True)
        if key not in {"flash", "flash_level", "flash_ts"}
    ]
    query.extend(flash_query_params(message, level=level, timestamp=timestamp).items())
    return urlunsplit((parts.scheme, parts.netloc, parts.path, urlencode(query), parts.fragment))


def render_flash_banners(
    banners: Sequence[FlashBanner | Mapping[str, object] | str],
    *,
    aria_live: str = "polite",
) -> str:
    """Render action-capable flash banners with legacy and PersonaCore hooks."""

    body = "".join(_flash_banner_html(_coerce_flash(banner)) for banner in banners)
    if not body:
        return ""
    return (
        f'<div class="flash-stack pc-flash-stack" aria-live="{escape(str(aria_live), quote=True)}">'
        f"{body}</div>"
    )


def _coerce_flash(value: FlashBanner | Mapping[str, object] | str) -> FlashBanner:
    if isinstance(value, str):
        return FlashBanner(value)
    return _coerce(value, FlashBanner)


def _flash_tone(value: object) -> str:
    tone = _tone(value)
    return tone if tone in {"good", "warn", "bad", "info", "neutral"} else "good"


def _flash_banner_html(banner: FlashBanner) -> str:
    tone = _flash_tone(banner.tone)
    classes = ["flash-banner", "pc-flash-banner", f"flash-{tone}", f"pc-flash-{tone}"]
    attrs = f'class="{" ".join(classes)}"'
    if banner.title:
        attrs += f' title="{escape(str(banner.title), quote=True)}"'
    message = f'<span class="flash-message pc-flash-message">{escape(str(banner.message or ""))}</span>'
    actions: list[str] = []
    if banner.action_label and banner.action_href:
        actions.append(
            '<a class="flash-action pc-flash-action" '
            f'href="{escape(str(banner.action_href), quote=True)}">'
            f"{escape(str(banner.action_label))}</a>"
        )
    if banner.dismissible:
        actions.append(
            '<button type="button" class="flash-dismiss pc-flash-dismiss" data-dismiss-flash>'
            f"{escape(str(banner.dismiss_label or 'Dismiss'))}</button>"
        )
    action_html = ""
    if actions:
        action_html = '<span class="flash-actions pc-flash-actions">' + "".join(actions) + "</span>"
    return f"<div {attrs}>{message}{action_html}</div>"
