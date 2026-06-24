from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Callable, Mapping, TypeVar

from .models import TokenHealthCheck, TokenHealthConfig

T = TypeVar("T")
TokenLookup = Callable[[str], object]

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "error": "bad",
    "red": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
    "amber": "warn",
    "yellow": "warn",
    "good": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "info": "info",
    "blue": "info",
    "cyan": "info",
    "neutral": "neutral",
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


def _secret_names(value: object) -> tuple[str, ...]:
    if isinstance(value, str):
        names = [value]
    elif value is None:
        names = []
    else:
        try:
            names = list(value)  # type: ignore[arg-type]
        except TypeError:
            names = [value]
    return tuple(str(name).strip() for name in names if str(name).strip())


def _value_present(value: object) -> bool:
    if value is None or value is False:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (bytes, bytearray)):
        return bool(value.strip())
    return True


def _lookup_secret(
    name: str,
    *,
    values: Mapping[str, object],
    lookup: TokenLookup | None,
) -> object:
    if name in values:
        return values[name]
    if lookup:
        return lookup(name)
    return None


def _check_present(
    check: TokenHealthCheck,
    *,
    values: Mapping[str, object],
    lookup: TokenLookup | None,
) -> tuple[bool, tuple[str, ...]]:
    names = _secret_names(check.secret_names)
    if check.configured is not None:
        return bool(check.configured), () if check.configured else names
    if not names:
        return False, ()
    missing: list[str] = []
    for name in names:
        if _value_present(_lookup_secret(name, values=values, lookup=lookup)):
            return True, ()
        missing.append(name)
    return False, tuple(missing)


def build_token_health_report(
    config: TokenHealthConfig | Mapping[str, object],
    *,
    values: Mapping[str, object] | None = None,
    lookup: TokenLookup | None = None,
) -> dict[str, object]:
    """Build a redacted token health report from runtime-owned settings.

    PersonaCore only records whether a configured token exists. Raw values from
    ``values`` or ``lookup`` are never copied into the returned report.
    """

    model = _coerce(config, TokenHealthConfig)
    rows: list[dict[str, object]] = []
    if model.enabled:
        source_values = values or {}
        for raw_check in model.checks:
            check = _coerce(raw_check, TokenHealthCheck)
            if not check.enabled:
                continue
            names = _secret_names(check.secret_names)
            present, missing = _check_present(check, values=source_values, lookup=lookup)
            status = "ready" if present else ("blocked" if check.required else "degraded")
            tone = "good" if present else ("bad" if check.required else "warn")
            label = check.label or check.key.replace("_", " ").replace("-", " ").title()
            summary = check.summary
            if not summary:
                if present:
                    summary = "Configured"
                elif check.required:
                    summary = "Required token is missing"
                else:
                    summary = "Optional token is not configured"
            rows.append(
                {
                    "key": str(check.key),
                    "label": str(label),
                    "name": str(label),
                    "group": str(check.group or "Integrations"),
                    "status": status,
                    "tone": tone,
                    "present": present,
                    "configured": present,
                    "required": bool(check.required),
                    "secret_names": names if model.show_secret_names else (),
                    "missing": missing if model.show_secret_names else (),
                    "href": str(check.href or ""),
                    "summary": str(summary),
                    "detail": str(check.detail or ""),
                }
            )

    blocked_required = sum(1 for row in rows if row["status"] == "blocked")
    warnings = sum(1 for row in rows if row["status"] == "degraded")
    present_count = sum(1 for row in rows if row["present"])
    tone = "bad" if blocked_required else ("warn" if warnings else "good")
    return {
        "enabled": bool(model.enabled),
        "title": str(model.title),
        "subtitle": str(model.subtitle),
        "empty_label": str(model.empty_label),
        "ok": blocked_required == 0,
        "tone": tone,
        "status": "blocked" if blocked_required else ("degraded" if warnings else "ready"),
        "token_count": len(rows),
        "present_count": present_count,
        "missing_count": len(rows) - present_count,
        "blocked_required": blocked_required,
        "warnings": warnings,
        "tokens": rows,
    }


def token_health_lookup(report: Mapping[str, object], key: str) -> Mapping[str, object] | None:
    for row in report.get("tokens", []) or []:
        if isinstance(row, Mapping) and str(row.get("key") or "") == key:
            return row
    return None


def _tag(label: object, tone: object) -> str:
    safe_tone = _tone(tone)
    return (
        f'<span class="pc-dashboard-tag pc-dashboard-tone-{safe_tone}">'
        f"{escape(str(label))}</span>"
    )


def _code_list(values: object) -> str:
    names = _secret_names(values)
    if not names:
        return '<span class="pc-token-health-muted">runtime supplied</span>'
    return "".join(f"<code>{escape(name)}</code>" for name in names)


def _row_html(raw_row: Mapping[str, object]) -> str:
    tone = _tone(raw_row.get("tone"))
    status = str(raw_row.get("status") or "unknown")
    required = "required" if raw_row.get("required") else "optional"
    label = str(raw_row.get("label") or raw_row.get("name") or raw_row.get("key") or "Token")
    group = str(raw_row.get("group") or "Integrations")
    summary = str(raw_row.get("summary") or "")
    detail = str(raw_row.get("detail") or "")
    href = str(raw_row.get("href") or "")
    title = (
        f'<a href="{escape(href, quote=True)}">{escape(label)}</a>'
        if href
        else escape(label)
    )
    detail_html = (
        f'<span class="pc-token-health-detail">{escape(detail)}</span>'
        if detail
        else ""
    )
    return (
        f'<tr class="pc-dashboard-tone-{tone}">'
        f'<td><strong>{title}</strong><span>{escape(required)}</span></td>'
        f"<td>{escape(group)}</td>"
        f"<td>{_tag(status, tone)}</td>"
        f'<td class="pc-token-health-sources">{_code_list(raw_row.get("secret_names"))}</td>'
        f"<td>{escape(summary)}{detail_html}</td>"
        "</tr>"
    )


def render_token_health_panel(
    report: TokenHealthConfig | Mapping[str, object] | None,
    *,
    values: Mapping[str, object] | None = None,
    lookup: TokenLookup | None = None,
) -> str:
    if report is None:
        return ""
    data = (
        build_token_health_report(report, values=values, lookup=lookup)
        if isinstance(report, TokenHealthConfig) or "checks" in report
        else dict(report)
    )
    if not data.get("enabled", True):
        return ""
    rows = [row for row in data.get("tokens", []) or [] if isinstance(row, Mapping)]
    title = str(data.get("title") or "Token Health")
    subtitle = str(data.get("subtitle") or "")
    token_count = int(data.get("token_count") or len(rows))
    present_count = int(data.get("present_count") or 0)
    missing_count = int(data.get("missing_count") or max(0, token_count - present_count))
    status = str(data.get("status") or "ready")
    tone = _tone(data.get("tone") or status)
    empty = str(data.get("empty_label") or "No token checks configured.")
    body = ""
    if rows:
        body = (
            '<div class="pc-token-health-table-wrap"><table class="pc-token-health-table">'
            "<thead><tr><th>Token</th><th>Group</th><th>Status</th><th>Source</th><th>Detail</th></tr></thead>"
            "<tbody>"
            + "".join(_row_html(row) for row in rows)
            + "</tbody></table></div>"
        )
    else:
        body = f'<div class="pc-dashboard-empty">{escape(empty)}</div>'
    return (
        '<section id="token-health" class="pc-token-health pc-dashboard-panel">'
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(title)}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(subtitle)}</div>'
        "</div>"
        f'{_tag(status, tone)}</div>'
        '<div class="pc-token-health-summary">'
        f'<span><strong>{token_count}</strong> tracked</span>'
        f'<span><strong>{present_count}</strong> configured</span>'
        f'<span><strong>{missing_count}</strong> missing</span>'
        "</div>"
        f"{body}</section>"
    )
