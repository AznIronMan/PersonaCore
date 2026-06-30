from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from time import time
from typing import Any, Callable, Mapping, Sequence, TypeVar
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

from .models import DiagnosticActionCard, DiagnosticMetaPair, DiagnosticTableColumn, FlashBanner, StatusTab

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


def render_diagnostic_action_card(card: DiagnosticActionCard | Mapping[str, object]) -> str:
    """Render a dense diagnostic card with legacy action-card CSS hooks."""

    model = _coerce(card, DiagnosticActionCard, {"title": "Diagnostic"})
    title = str(model.title or "Diagnostic")
    tone = _tone(model.tone)
    classes = ["action-card", "pc-diagnostic-card", f"pc-diagnostic-card-{tone}"]
    status = str(model.status or "")
    status_html = ""
    if status:
        status_tone = tone if tone in {"good", "warn", "bad"} else "neutral"
        status_html = (
            f'<span class="status-pill status-{escape(status_tone)} pc-diagnostic-status">'
            f"<span></span>{escape(status)}</span>"
        )
    pair_html = "".join(_diagnostic_pair_html(pair) for pair in model.pairs)
    body = (
        '<div class="action-card-head pc-diagnostic-card-head"><div>'
        f'<div class="action-card-kicker pc-diagnostic-kicker">{escape(str(model.kicker or "diagnostic"))}</div>'
        f"<h3>{escape(title)}</h3></div>{status_html}</div>"
    )
    if model.summary:
        body += f'<p class="pc-diagnostic-summary">{escape(str(model.summary))}</p>'
    if pair_html:
        body += f'<div class="meta-pair-grid pc-diagnostic-pairs">{pair_html}</div>'
    if model.href:
        return (
            f'<a class="{" ".join(classes)}" href="{escape(str(model.href), quote=True)}">'
            f"{body}</a>"
        )
    return f'<article class="{" ".join(classes)}">{body}</article>'


def render_diagnostic_action_cards(
    cards: Sequence[DiagnosticActionCard | Mapping[str, object]],
    *,
    empty_label: str = "No diagnostic cards.",
    wrapper_class: str = "action-card-list pc-diagnostic-card-list",
) -> str:
    """Render a diagnostic card list with a safe empty state."""

    body = "".join(render_diagnostic_action_card(card) for card in cards)
    if not body:
        body = f'<p class="hint pc-diagnostic-empty">{escape(str(empty_label))}</p>'
    return f'<div class="{escape(str(wrapper_class), quote=True)}">{body}</div>'


def render_surface_unavailable(
    title: object,
    *,
    status: object = "renderer unavailable",
    summary: object = "Shared renderer output is unavailable; showing runtime-owned diagnostics.",
    href: object = "",
    tone: object = "warn",
    kicker: object = "diagnostic",
    pairs: Sequence[DiagnosticMetaPair | Mapping[str, object] | tuple[str, str]] = (),
) -> str:
    """Render one generic unavailable-renderer diagnostic card."""

    return render_diagnostic_action_card(
        DiagnosticActionCard(
            title=str(title or "Shared surface"),
            kicker=str(kicker or "diagnostic"),
            status=str(status or "renderer unavailable"),
            summary=str(summary or ""),
            href=str(href or ""),
            tone=_tone(tone),
            pairs=tuple(pairs),
        )
    )


def _diagnostic_pair_html(raw: DiagnosticMetaPair | Mapping[str, object] | tuple[str, str]) -> str:
    if isinstance(raw, tuple):
        pair = DiagnosticMetaPair(str(raw[0] if len(raw) > 0 else ""), str(raw[1] if len(raw) > 1 else ""))
    else:
        pair = _coerce(raw, DiagnosticMetaPair, {"label": "", "value": ""})
    if not pair.label and not pair.value:
        return ""
    return (
        '<div class="meta-pair pc-diagnostic-pair">'
        f"<span>{escape(str(pair.label))}</span><strong>{escape(str(pair.value))}</strong></div>"
    )


def render_diagnostic_table(
    rows: Sequence[Mapping[str, object]],
    columns: Sequence[str | DiagnosticTableColumn | Mapping[str, object] | tuple[str, str]],
    *,
    empty_label: str = "No rows yet.",
    wrapper_class: str = "table-wrap",
    table_class: str = "compact-table",
    cell_renderer: Callable[[object, Mapping[str, object], str], str] | None = None,
) -> str:
    """Render a compact diagnostic table with safe defaults and legacy classes."""

    models = tuple(_diagnostic_column(column) for column in columns)
    clean_rows = tuple(row for row in rows if isinstance(row, Mapping))
    if not clean_rows:
        return f'<p class="hint pc-diagnostic-empty">{escape(str(empty_label))}</p>'
    header = "".join(f"<th>{escape(column.label or column.key.replace('_', ' '))}</th>" for column in models)
    body = ""
    for row in clean_rows:
        cells = "".join(
            f"<td>{_diagnostic_cell_html(row.get(column.key), row, column, cell_renderer=cell_renderer)}</td>"
            for column in models
        )
        body += f"<tr>{cells}</tr>"
    return (
        f'<div class="{escape(str(wrapper_class), quote=True)}">'
        f'<table class="{escape(str(table_class), quote=True)}"><thead><tr>{header}</tr></thead>'
        f"<tbody>{body}</tbody></table></div>"
    )


def render_sortable_diagnostic_table(
    rows: Sequence[Mapping[str, object]],
    columns: Sequence[str | DiagnosticTableColumn | Mapping[str, object] | tuple[str, str]],
    *,
    sortable_columns: Sequence[str] = (),
    sort_key: str = "",
    direction: str = "",
    sort_href_builder: Callable[[str, str], str] | None = None,
    link_columns: Mapping[str, Callable[[Mapping[str, object]], str]] | None = None,
    numeric_columns: Sequence[str] = (),
    boolean_columns: Sequence[str] = (),
    primary_columns: Sequence[str] = (),
    empty_label: str = "No rows yet.",
    wrapper_class: str = "table-wrap",
    table_class: str = "list-table",
    cell_renderer: Callable[[object, Mapping[str, object], str], str] | None = None,
) -> str:
    """Render a sortable diagnostic table without owning consumer sorting logic."""

    sortable = {str(key) for key in sortable_columns}
    numeric = {str(key) for key in numeric_columns}
    boolean = {str(key) for key in boolean_columns}
    primary = {str(key) for key in primary_columns}
    links = dict(link_columns or {})
    models = tuple(
        _diagnostic_column(
            column,
            sortable=str(_diagnostic_column(column).key) in sortable,
            numeric=str(_diagnostic_column(column).key) in numeric,
            boolean=str(_diagnostic_column(column).key) in boolean,
            primary=str(_diagnostic_column(column).key) in primary,
        )
        for column in columns
    )
    clean_rows = tuple(row for row in rows if isinstance(row, Mapping))
    if not clean_rows:
        return f'<p class="hint pc-diagnostic-empty">{escape(str(empty_label))}</p>'
    direction_key = str(direction or "").lower()
    if direction_key not in {"asc", "desc"}:
        direction_key = "asc"
    header = ""
    for column in models:
        label = escape(column.label or column.key.replace("_", " "))
        if column.sortable and sort_href_builder:
            next_direction = "desc" if sort_key == column.key and direction_key == "asc" else "asc"
            href = sort_href_builder(column.key, next_direction)
            marker = _diagnostic_sort_marker(column.key, sort_key, direction_key)
            header += f'<th><a href="{escape(str(href), quote=True)}">{label}{marker}</a></th>'
        else:
            header += f"<th>{label}</th>"
    body = ""
    for row in clean_rows:
        cells: list[str] = []
        for column in models:
            classes: list[str] = []
            if column.numeric:
                classes.append("numeric")
            if column.boolean:
                classes.append("boolean")
            value_html = _diagnostic_cell_html(row.get(column.key), row, column, cell_renderer=cell_renderer)
            href_builder = links.get(column.key)
            if href_builder:
                href = href_builder(row)
                if href:
                    cls = "row-primary" if column.primary else ""
                    class_attr = f' class="{cls}"' if cls else ""
                    value_html = f'<a{class_attr} href="{escape(str(href), quote=True)}">{value_html}</a>'
            elif column.primary:
                value_html = f'<span class="row-primary">{value_html}</span>'
            class_attr = f' class="{" ".join(classes)}"' if classes else ""
            cells.append(f"<td{class_attr}>{value_html}</td>")
        body += f"<tr>{''.join(cells)}</tr>"
    return (
        f'<div class="{escape(str(wrapper_class), quote=True)}">'
        f'<table class="{escape(str(table_class), quote=True)}"><thead><tr>{header}</tr></thead>'
        f"<tbody>{body}</tbody></table></div>"
    )


def _diagnostic_column(
    raw: str | DiagnosticTableColumn | Mapping[str, object] | tuple[str, str],
    *,
    sortable: bool | None = None,
    numeric: bool | None = None,
    boolean: bool | None = None,
    primary: bool | None = None,
) -> DiagnosticTableColumn:
    if isinstance(raw, str):
        column = DiagnosticTableColumn(raw)
    elif isinstance(raw, tuple):
        column = DiagnosticTableColumn(str(raw[0] if len(raw) > 0 else ""), str(raw[1] if len(raw) > 1 else ""))
    else:
        column = _coerce(raw, DiagnosticTableColumn, {"key": ""})
    return DiagnosticTableColumn(
        key=str(column.key or ""),
        label=str(column.label or ""),
        sortable=column.sortable if sortable is None else sortable,
        numeric=column.numeric if numeric is None else numeric,
        boolean=column.boolean if boolean is None else boolean,
        primary=column.primary if primary is None else primary,
    )


def _diagnostic_cell_html(
    value: object,
    row: Mapping[str, object],
    column: DiagnosticTableColumn,
    *,
    cell_renderer: Callable[[object, Mapping[str, object], str], str] | None,
) -> str:
    if cell_renderer:
        return str(cell_renderer(value, row, column.key))
    if value is None:
        return '<span class="pc-diagnostic-empty-value">-</span>'
    return escape(str(value))


def _diagnostic_sort_marker(key: str, sort_key: str, direction: str) -> str:
    if key != sort_key:
        return ""
    marker = "up" if direction == "asc" else "down"
    return f'<span class="sort-marker pc-diagnostic-sort-marker">{escape(marker)}</span>'


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
    """Render action-capable flash banners with legacy and PersonaConsole hooks."""

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
