from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import StatusTab

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
