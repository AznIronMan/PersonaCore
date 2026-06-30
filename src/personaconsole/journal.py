from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from datetime import date, timedelta
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    JournalCalendarDay,
    JournalDetail,
    JournalEntry,
    JournalMarker,
    JournalSurfaceConfig,
    JournalThemeOption,
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

JOURNAL_FEATURE = "journal"

JOURNAL_THEME_KEYS = (
    "paper",
    "white-paper",
    "typewriter",
    "script",
    "sepia",
    "ledger",
    "night-ink",
    "violet-archive",
    "matrix",
    "amber-terminal",
    "blueprint",
    "glass",
)

_THEME_LABELS = {
    "paper": "Paper",
    "white-paper": "White Paper",
    "typewriter": "Typewriter",
    "script": "Script",
    "sepia": "Sepia",
    "ledger": "Ledger",
    "night-ink": "Night Ink",
    "violet-archive": "Violet Archive",
    "matrix": "Matrix",
    "amber-terminal": "Amber Terminal",
    "blueprint": "Blueprint",
    "glass": "Glass",
}

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "high": "bad",
    "red": "bad",
    "warn": "warn",
    "warning": "warn",
    "held": "warn",
    "medium": "warn",
    "pending": "warn",
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


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
    return "".join(parts)


def journal_theme_key(value: object) -> str:
    key = str(value or "").strip().lower().replace("_", "-")
    return key if key in JOURNAL_THEME_KEYS else "paper"


def journal_theme_options(selected: str = "paper") -> tuple[JournalThemeOption, ...]:
    selected_key = journal_theme_key(selected)
    return tuple(
        JournalThemeOption(key, _THEME_LABELS[key], selected=key == selected_key)
        for key in JOURNAL_THEME_KEYS
    )


def _entry_date(value: object) -> str:
    if isinstance(value, JournalEntry):
        return str(value.date)
    if isinstance(value, Mapping):
        return str(value.get("date") or "")
    return str(value or "")


def build_journal_calendar(
    month: str,
    entry_dates: Sequence[str | JournalEntry | Mapping[str, object]],
    *,
    selected_date: str = "",
    href_template: str = "",
) -> tuple[JournalCalendarDay, ...]:
    first = date.fromisoformat(f"{str(month).strip()}-01")
    start = first - timedelta(days=first.weekday())
    entry_set = {entry_date for entry_date in (_entry_date(value) for value in entry_dates) if entry_date}
    days: list[JournalCalendarDay] = []
    for offset in range(42):
        current = start + timedelta(days=offset)
        current_text = current.isoformat()
        has_entry = current_text in entry_set
        href = href_template.replace("{date}", current_text) if has_entry and href_template else ""
        days.append(
            JournalCalendarDay(
                current_text,
                current.day,
                href=href,
                in_month=current.month == first.month,
                has_entry=has_entry,
                selected=current_text == selected_date,
            )
        )
    return tuple(days)


def journal_surface_feature_enabled(
    config: JournalSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, JournalSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or JOURNAL_FEATURE), default=True)


def render_journal_surface(
    config: JournalSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, JournalSurfaceConfig)
    if not journal_surface_feature_enabled(model, features):
        return ""

    entries = [_coerce(entry, JournalEntry) for entry in model.entries]
    entry = _coerce(model.entry, JournalEntry) if model.entry else (entries[0] if entries else None)
    selected_date = str(entry.date) if entry else ""
    calendar = [_coerce(day, JournalCalendarDay) for day in model.calendar]
    if not calendar and model.month_label and entries:
        try:
            calendar = list(build_journal_calendar(model.month_label, entries, selected_date=selected_date))
        except ValueError:
            calendar = []
    theme = journal_theme_key(model.theme)
    return f"""
<section id="journal" class="pc-journal-surface pc-dashboard-panel pc-journal-theme-{theme}">
  <div class="pc-dashboard-panel-head">
    <div>
      <div class="pc-dashboard-section-title">{escape(str(model.title or "Journal"))}</div>
      <div class="pc-dashboard-section-meta">{escape(str(model.subtitle or ""))}</div>
    </div>
    {_theme_options_html(model.theme_options, theme)}
  </div>
  <div class="pc-journal-layout">
    {_calendar_html(model, calendar, policy=privacy_policy, context=privacy_context)}
    {_entry_html(entry, model.empty_label, features=features, policy=privacy_policy, context=privacy_context)}
  </div>
</section>
"""


def _theme(raw_theme: JournalThemeOption | Mapping[str, object] | str, selected: str) -> JournalThemeOption:
    if isinstance(raw_theme, str):
        key = journal_theme_key(raw_theme)
        return JournalThemeOption(key, _THEME_LABELS[key], selected=key == selected)
    defaults: Mapping[str, Any] = {}
    if isinstance(raw_theme, Mapping):
        key = journal_theme_key(raw_theme.get("key") or raw_theme.get("label"))
        defaults = {"key": key, "label": _THEME_LABELS[key]}
    option = _coerce(raw_theme, JournalThemeOption, defaults)
    key = journal_theme_key(option.key)
    return JournalThemeOption(
        key,
        option.label or _THEME_LABELS[key],
        href=option.href,
        selected=option.selected or key == selected,
        title=option.title,
    )


def _theme_options_html(
    options: Sequence[JournalThemeOption | Mapping[str, object] | str],
    selected: str,
) -> str:
    if not options:
        return ""
    body: list[str] = []
    for raw_option in options:
        option = _theme(raw_option, selected)
        classes = f"pc-journal-theme-option pc-journal-theme-swatch-{option.key}"
        if option.selected:
            classes += " is-active"
        label = escape(str(option.label))
        if option.href:
            body.append(
                f'<a class="{classes}" href="{escape(str(option.href), quote=True)}"{_attrs(title=option.title)}>{label}</a>'
            )
        else:
            body.append(f'<span class="{classes}"{_attrs(title=option.title)}>{label}</span>')
    return f'<div class="pc-journal-theme-options">{"".join(body)}</div>'


def _calendar_html(
    config: JournalSurfaceConfig,
    days: Sequence[JournalCalendarDay],
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not days:
        body = f'<div class="pc-dashboard-empty">{escape(str(config.calendar_empty_label))}</div>'
    else:
        weekday_labels = "".join(f'<span class="pc-journal-calendar-label">{label}</span>' for label in ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"))
        body = (
            '<div class="pc-journal-calendar-grid">'
            + weekday_labels
            + "".join(_day_html(day, policy=policy, context=context) for day in days)
            + "</div>"
        )
    return f"""
    <section class="pc-journal-calendar-panel">
      <div class="pc-journal-calendar-head">
        {_month_link(config.previous_month_label, config.previous_month_href)}
        <strong>{escape(str(config.month_label or config.title or "Journal"))}</strong>
        {_month_link(config.next_month_label, config.next_month_href)}
      </div>
      {body}
    </section>
"""


def _month_link(label: str, href: str) -> str:
    text = escape(str(label))
    if href:
        return f'<a class="pc-journal-month-link" href="{escape(str(href), quote=True)}">{text}</a>'
    return f'<span class="pc-journal-month-link is-disabled">{text}</span>'


def _marker(raw_marker: JournalMarker | SurfaceBadge | Mapping[str, object] | str) -> JournalMarker:
    if isinstance(raw_marker, str):
        return JournalMarker(raw_marker)
    if isinstance(raw_marker, SurfaceBadge):
        return JournalMarker(raw_marker.label, tone=raw_marker.tone)
    return _coerce(raw_marker, JournalMarker)


def _markers_html(
    markers: Sequence[JournalMarker | SurfaceBadge | Mapping[str, object] | str],
    *,
    compact: bool = False,
) -> str:
    body: list[str] = []
    for raw_marker in markers:
        marker = _marker(raw_marker)
        if not marker.label:
            continue
        label = "" if compact else escape(str(marker.label))
        body.append(
            f'<span class="pc-journal-marker pc-dashboard-tone-{_tone(marker.tone)}"{_attrs(title=marker.title or marker.label)}>{label}</span>'
        )
    return f'<div class="pc-journal-markers">{"".join(body)}</div>' if body else ""


def _day_html(
    day: JournalCalendarDay,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    classes = ["pc-journal-calendar-day"]
    if not day.in_month:
        classes.append("is-muted")
    if day.has_entry:
        classes.append("has-entry")
    if day.selected:
        classes.append("is-selected")
    body = f"<span>{escape(str(day.day))}</span>"
    if day.has_entry:
        body += '<i aria-hidden="true"></i>'
    body += _markers_html(day.markers, compact=True)
    attrs = _attrs(title=day.title or day.date, aria_current="date" if day.selected else "")
    href = _raw_href(day.href, privacy_scope=day.privacy_scope, policy=policy, context=context)
    if href:
        return f'<a class="{" ".join(classes)}" href="{escape(str(href), quote=True)}"{attrs}>{body}</a>'
    return f'<span class="{" ".join(classes)}"{attrs}>{body}</span>'


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


def _raw_private_allowed(
    *,
    privacy_scope: str,
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


def _raw_href(
    href: str,
    *,
    privacy_scope: str,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if not href or not privacy_scope:
        return href
    return href if _raw_private_allowed(privacy_scope=privacy_scope, policy=policy, context=context) else ""


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


def _entry_html(
    entry: JournalEntry | None,
    empty_label: str,
    *,
    features: Mapping[str, bool] | None,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    if entry is None:
        return f'<section class="pc-journal-page"><div class="pc-dashboard-empty">{escape(str(empty_label))}</div></section>'
    title = _private_text(
        entry.title,
        privacy_scope=entry.privacy_scope,
        safe_alternate=entry.safe_alternate,
        policy=policy,
        context=context,
    )
    text = _private_text(
        entry.text or entry.summary,
        privacy_scope=entry.privacy_scope,
        safe_alternate=entry.safe_alternate,
        policy=policy,
        context=context,
    )
    subtitle = _private_text(
        entry.subtitle,
        privacy_scope=entry.privacy_scope,
        safe_alternate="",
        policy=policy,
        context=context,
    )
    previous_href = _raw_href(entry.previous_href, privacy_scope=entry.privacy_scope, policy=policy, context=context)
    next_href = _raw_href(entry.next_href, privacy_scope=entry.privacy_scope, policy=policy, context=context)
    private = _private_class(privacy_scope=entry.privacy_scope, policy=policy, context=context)
    raw_allowed = _raw_private_allowed(privacy_scope=entry.privacy_scope, policy=policy, context=context)
    details = _details_html(entry) if raw_allowed else ""
    legacy = f'<p class="pc-journal-legacy-note">{escape(str(entry.legacy_label))}</p>' if entry.legacy else ""
    actions = _actions_html(entry.actions, features) if raw_allowed else ""
    return f"""
    <section class="pc-journal-page{private}">
      <article class="pc-journal-paper">
        <p class="pc-journal-eyebrow">{_entry_eyebrow(entry)}</p>
        <h2>{escape(title or entry.date or "Journal Entry")}</h2>
        {_entry_meta_html(entry, subtitle)}
        {_prose_html(text)}
        {legacy}
        {_markers_html(entry.markers)}
        {actions}
      </article>
      <div class="pc-journal-page-turner">
        {_turn_link(entry.previous_label, previous_href)}
        {_turn_link(entry.next_label, next_href)}
      </div>
      {details}
    </section>
"""


def _entry_eyebrow(entry: JournalEntry) -> str:
    parts = [
        str(entry.date or ""),
        str(entry.privacy_label or ""),
        str(entry.author_label or ""),
    ]
    return escape(" - ".join(part for part in parts if part))


def _entry_meta_html(entry: JournalEntry, subtitle: str) -> str:
    parts = [
        f"<span>{escape(str(entry.timestamp))}</span>" if entry.timestamp else "",
        f"<span>{escape(str(subtitle))}</span>" if subtitle else "",
    ]
    body = "".join(parts)
    return f'<div class="pc-journal-entry-meta">{body}</div>' if body else ""


def _prose_html(text: str) -> str:
    paragraphs = [paragraph.strip() for paragraph in str(text or "").split("\n\n") if paragraph.strip()]
    if not paragraphs:
        paragraphs = [WITHHELD_PRIVATE_TEXT]
    body = "".join(f"<p>{escape(paragraph)}</p>" for paragraph in paragraphs)
    return f'<div class="pc-journal-prose">{body}</div>'


def _turn_link(label: str, href: str) -> str:
    text = escape(str(label))
    if href:
        return f'<a class="pc-journal-turn-link" href="{escape(str(href), quote=True)}">{text}</a>'
    return f'<span class="pc-journal-turn-link is-disabled">{text}</span>'


def _detail_html(raw_detail: JournalDetail | Mapping[str, object]) -> str:
    detail = _coerce(raw_detail, JournalDetail)
    if not detail.label:
        return ""
    value = "on" if detail.value is True else "off" if detail.value is False else str(detail.value)
    return (
        f'<div class="pc-journal-detail pc-dashboard-tone-{_tone(detail.tone)}">'
        f"<dt>{escape(str(detail.label))}</dt><dd>{escape(value)}</dd></div>"
    )


def _details_html(entry: JournalEntry) -> str:
    body = "".join(_detail_html(detail) for detail in entry.details)
    if not body:
        return ""
    return f"""
      <details class="pc-journal-details">
        <summary>{escape(str(entry.details_title or "Source And Provenance"))}</summary>
        <dl>{body}</dl>
      </details>
"""


def _action_html(raw_action: SurfaceAction | Mapping[str, object], features: Mapping[str, bool] | None) -> str:
    action = _coerce(raw_action, SurfaceAction)
    if not action.label:
        return ""
    if action.feature and not feature_enabled(features, action.feature, default=True):
        return ""
    tone = _tone(action.tone)
    method = str(action.method or "").strip().upper()
    method_attr = f' data-method="{escape(method, quote=True)}"' if method else ""
    title = f' title="{escape(str(action.title), quote=True)}"' if action.title else ""
    label = escape(str(action.label))
    if action.disabled or not action.href:
        disabled = ' aria-disabled="true"' if action.disabled else ""
        return f'<span class="pc-journal-action pc-dashboard-tone-{tone} is-disabled"{title}{disabled}>{label}</span>'
    return f'<a class="pc-journal-action pc-dashboard-tone-{tone}" href="{escape(str(action.href), quote=True)}"{method_attr}{title}>{label}</a>'


def _actions_html(actions: Sequence[SurfaceAction | Mapping[str, object]], features: Mapping[str, bool] | None) -> str:
    body = "".join(_action_html(action, features) for action in actions)
    return f'<div class="pc-journal-actions">{body}</div>' if body else ""
