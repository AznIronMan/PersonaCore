from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar
from urllib.parse import urlsplit

from .controls import render_flash_banners
from .models import (
    AdminAuthLink,
    AdminAuthSummaryItem,
    AdminLoginPageConfig,
    AdminPasswordChangePageConfig,
    BrandAssets,
    FlashBanner,
    ThemeTokens,
)

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
    "amber": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "green": "good",
    "info": "info",
    "blue": "info",
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


def _coerce(value: T | Mapping[str, object] | None, cls: type[T], defaults: Mapping[str, Any] | None = None) -> T:
    if isinstance(value, cls):
        return value
    data = {**(defaults or {}), **_mapping(value)}
    allowed = {field.name for field in fields(cls)}
    return cls(**{key: value for key, value in data.items() if key in allowed})


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _safe_name(value: object, default: str) -> str:
    raw = str(value or "").strip()
    safe = "".join(char if char.isalnum() or char in {"_", "-"} else "_" for char in raw)
    safe = safe.strip("_-")
    return safe or default


def _safe_dom_id(value: object, default: str) -> str:
    raw = str(value or "").strip()
    safe = "".join(char if char.isalnum() or char in {"_", "-"} else "-" for char in raw)
    safe = safe.strip("_-")
    return safe or default


def _safe_root_relative(value: object, fallback: str = "/") -> str:
    raw = str(value or "").strip()
    if not raw:
        return fallback
    if any(char in raw for char in ("\r", "\n", "\t", "\x00", "\\")):
        return fallback
    parts = urlsplit(raw)
    if parts.scheme or parts.netloc or raw.startswith("//") or not raw.startswith("/"):
        return fallback
    return raw


def _safe_next_path(value: object, blocked_prefixes: Sequence[str], fallback: str = "/") -> str:
    safe = _safe_root_relative(value, fallback)
    path = urlsplit(safe).path.rstrip("/") or "/"
    for prefix in blocked_prefixes:
        blocked = _safe_root_relative(prefix, "").rstrip("/")
        if not blocked:
            continue
        if path == blocked or path.startswith(blocked + "/"):
            return fallback
    return safe


def _brand(value: BrandAssets | Mapping[str, object] | None, fallback_name: str) -> BrandAssets:
    model = _coerce(value, BrandAssets, {"name": fallback_name, "alt_text": fallback_name, "home_url": "/"})
    name = str(model.name or fallback_name or "Admin")
    return BrandAssets(
        name=name,
        small_logo_url=_safe_root_relative(model.small_logo_url, ""),
        large_logo_url=_safe_root_relative(model.large_logo_url, ""),
        wordmark_url=_safe_root_relative(model.wordmark_url, ""),
        favicon_url=_safe_root_relative(model.favicon_url, ""),
        signature_text=str(model.signature_text or ""),
        alt_text=str(model.alt_text or name),
        home_url=_safe_root_relative(model.home_url, "/"),
    )


def _theme(value: ThemeTokens | Mapping[str, object] | None) -> ThemeTokens:
    return _coerce(value, ThemeTokens)


def _asset_base(value: object) -> str:
    return _safe_root_relative(value, "/persona-console/static").rstrip("/") or "/persona-console/static"


def _initials(value: str) -> str:
    initials: list[str] = []
    for part in value.replace("-", " ").replace("_", " ").split():
        for char in part:
            if char.isalnum():
                initials.append(char.upper())
                break
        if len(initials) >= 2:
            break
    compact = "".join(char for char in value if char.isalnum())
    return "".join(initials)[:2] or compact[:2].upper() or "AD"


def _brand_mark(model: BrandAssets) -> str:
    image = model.wordmark_url or model.large_logo_url or model.small_logo_url
    if image:
        return (
            '<img class="pc-admin-auth-logo" '
            f'src="{escape(image, quote=True)}" '
            f'alt="{escape(model.alt_text or model.name, quote=True)}">'
        )
    return f'<span class="pc-admin-auth-logo-fallback" aria-hidden="true">{escape(_initials(model.name))}</span>'


def _links_html(links: Sequence[AdminAuthLink | Mapping[str, object]], class_name: str, label: str) -> str:
    items: list[str] = []
    for raw_link in links:
        link = _coerce(raw_link, AdminAuthLink, {"label": "", "href": ""})
        href = _safe_root_relative(link.href, "")
        if not link.label or not href:
            continue
        target = ' target="_blank"' if link.external else ""
        rel = f' rel="{escape(str(link.rel or "noopener noreferrer"), quote=True)}"' if link.external else ""
        title = f' title="{escape(str(link.title), quote=True)}"' if link.title else ""
        items.append(
            f'<a href="{escape(href, quote=True)}"{target}{rel}{title}>{escape(str(link.label))}</a>'
        )
    if not items:
        return ""
    return f'<nav class="{class_name}" aria-label="{escape(label, quote=True)}">{"".join(items)}</nav>'


def _summary_html(items: Sequence[AdminAuthSummaryItem | Mapping[str, object]]) -> str:
    body: list[str] = []
    for raw_item in items:
        item = _coerce(raw_item, AdminAuthSummaryItem, {"label": ""})
        if not item.label:
            continue
        tone = _tone(item.tone)
        value = f'<strong>{escape(str(item.value))}</strong>' if item.value else ""
        detail = f'<small>{escape(str(item.detail))}</small>' if item.detail else ""
        body.append(
            f'<li class="pc-admin-auth-summary-item pc-admin-auth-summary-{tone}">'
            f'<span>{escape(str(item.label))}</span>{value}{detail}</li>'
        )
    if not body:
        return ""
    return f'<ul class="pc-admin-auth-summary" aria-label="Authentication status">{"".join(body)}</ul>'


def _banners_html(
    banners: Sequence[FlashBanner | Mapping[str, object] | str],
    *,
    status_message: str = "",
    status_tone: str = "bad",
) -> str:
    all_banners: list[FlashBanner | Mapping[str, object] | str] = []
    if status_message:
        all_banners.append(FlashBanner(str(status_message), tone=_tone(status_tone), dismissible=False))
    all_banners.extend(banners)
    return render_flash_banners(all_banners, aria_live="assertive") if all_banners else ""


def _page_head(title: str, brand: BrandAssets, static_base_url: str, theme: ThemeTokens) -> str:
    favicon = f'  <link rel="icon" href="{escape(brand.favicon_url, quote=True)}">\n' if brand.favicon_url else ""
    return f"""<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{escape(title)}</title>
{favicon}  <style>
:root {{
{theme.css_variables()}
}}
  </style>
  <link rel="stylesheet" href="{escape(static_base_url, quote=True)}/persona-console.css">
</head>"""


def _shell_html(
    *,
    page_title: str,
    title: str,
    subtitle: str,
    brand: BrandAssets,
    static_base_url: str,
    theme: ThemeTokens,
    method_label: str,
    banners_html: str,
    summary_html: str,
    form_html: str,
    help_links_html: str,
    legal_links_html: str,
    no_script_message: str,
    body_class: str,
) -> str:
    document_title = page_title or (title if brand.name in title else f"{brand.name} {title}".strip())
    method = f'<span class="pc-admin-auth-method">{escape(method_label)}</span>' if method_label else ""
    noscript = (
        f'<noscript><p class="pc-admin-auth-noscript">{escape(no_script_message)}</p></noscript>'
        if no_script_message
        else ""
    )
    return f"""<!doctype html>
<html lang="en">
{_page_head(document_title, brand, static_base_url, theme)}
<body class="admin-shell pc-admin-auth-page {escape(body_class, quote=True)}">
  <main class="pc-admin-auth-shell" aria-labelledby="pc-admin-auth-title">
    <section class="pc-admin-auth-card">
      <header class="pc-admin-auth-header">
        <a class="pc-admin-auth-brand" href="{escape(brand.home_url, quote=True)}" aria-label="{escape(brand.name, quote=True)} home">
          {_brand_mark(brand)}
          <span class="pc-admin-auth-brand-copy">
            <strong>{escape(brand.name)}</strong>
            {method}
          </span>
        </a>
        <h1 id="pc-admin-auth-title">{escape(title)}</h1>
        <p>{escape(subtitle)}</p>
      </header>
      {banners_html}
      {summary_html}
      {form_html}
      {help_links_html}
      {noscript}
    </section>
    {legal_links_html}
  </main>
</body>
</html>"""


def render_admin_login_page(config: AdminLoginPageConfig | Mapping[str, object]) -> str:
    model = _coerce(config, AdminLoginPageConfig)
    brand = _brand(model.brand, model.title)
    action = _safe_root_relative(model.form_action, "/login")
    next_path = _safe_next_path(model.next_path, model.blocked_next_prefixes, "/")
    next_name = _safe_name(model.next_field_name, "next")
    username_name = _safe_name(model.username_name, "username")
    password_name = _safe_name(model.password_name, "password")
    username_id = _safe_dom_id(f"{username_name}-field", "username-field")
    password_id = _safe_dom_id(f"{password_name}-field", "password-field")
    autofocus = " autofocus" if model.autofocus else ""
    username_value = (
        f' value="{escape(str(model.username_value), quote=True)}"' if model.username_value else ""
    )
    username_placeholder = (
        f' placeholder="{escape(str(model.username_placeholder), quote=True)}"' if model.username_placeholder else ""
    )
    password_placeholder = (
        f' placeholder="{escape(str(model.password_placeholder), quote=True)}"' if model.password_placeholder else ""
    )
    form_html = f"""
      <form class="pc-admin-auth-form" method="post" action="{escape(action, quote=True)}" data-pc-admin-auth-form>
        <input type="hidden" name="{escape(next_name, quote=True)}" value="{escape(next_path, quote=True)}">
        <label for="{escape(username_id, quote=True)}">{escape(model.username_label)}
          <input id="{escape(username_id, quote=True)}" name="{escape(username_name, quote=True)}" autocomplete="username" required{autofocus}{username_value}{username_placeholder}>
        </label>
        <label for="{escape(password_id, quote=True)}">{escape(model.password_label)}
          <input id="{escape(password_id, quote=True)}" name="{escape(password_name, quote=True)}" type="password" autocomplete="current-password" required{password_placeholder}>
        </label>
        <button type="submit">{escape(model.submit_label)}</button>
      </form>"""
    return _shell_html(
        page_title=model.page_title,
        title=model.title,
        subtitle=model.subtitle,
        brand=brand,
        static_base_url=_asset_base(model.static_base_url),
        theme=_theme(model.theme),
        method_label=model.method_label,
        banners_html=_banners_html(model.banners, status_message=model.status_message, status_tone=model.status_tone),
        summary_html=_summary_html(model.summary_items),
        form_html=form_html,
        help_links_html=_links_html(model.help_links, "pc-admin-auth-help-links", "Admin login help"),
        legal_links_html=_links_html(model.legal_links, "pc-admin-auth-legal-links", "Admin legal links"),
        no_script_message=model.no_script_message,
        body_class="pc-admin-login-page",
    )


def render_admin_password_change_page(config: AdminPasswordChangePageConfig | Mapping[str, object]) -> str:
    model = _coerce(config, AdminPasswordChangePageConfig)
    brand = _brand(model.brand, model.title)
    action = _safe_root_relative(model.form_action, "/login/password-change")
    next_path = _safe_next_path(model.next_path, model.blocked_next_prefixes, "/")
    next_name = _safe_name(model.next_field_name, "next")
    new_name = _safe_name(model.new_password_name, "new_password")
    confirm_name = _safe_name(model.confirm_password_name, "confirm_password")
    new_id = _safe_dom_id(f"{new_name}-field", "new-password-field")
    confirm_id = _safe_dom_id(f"{confirm_name}-field", "confirm-password-field")
    autofocus = " autofocus" if model.autofocus and not model.disabled else ""
    disabled = " disabled" if model.disabled else ""
    min_length = max(0, int(model.min_length or 0))
    min_attr = f' minlength="{min_length}"' if min_length else ""
    subject = str(model.subject_label or "admin")
    subtitle = model.subtitle or f"{subject} needs a new password."
    form_html = f"""
      <form class="pc-admin-auth-form" method="post" action="{escape(action, quote=True)}" data-pc-admin-auth-form>
        <input type="hidden" name="{escape(next_name, quote=True)}" value="{escape(next_path, quote=True)}">
        <label for="{escape(new_id, quote=True)}">{escape(model.new_password_label)}
          <input id="{escape(new_id, quote=True)}" name="{escape(new_name, quote=True)}" type="password" autocomplete="new-password"{min_attr} required{autofocus}{disabled}>
        </label>
        <label for="{escape(confirm_id, quote=True)}">{escape(model.confirm_password_label)}
          <input id="{escape(confirm_id, quote=True)}" name="{escape(confirm_name, quote=True)}" type="password" autocomplete="new-password"{min_attr} required{disabled}>
        </label>
        <button type="submit"{disabled}>{escape(model.submit_label)}</button>
      </form>"""
    return _shell_html(
        page_title=model.page_title,
        title=model.title,
        subtitle=subtitle,
        brand=brand,
        static_base_url=_asset_base(model.static_base_url),
        theme=_theme(model.theme),
        method_label=model.method_label,
        banners_html=_banners_html(model.banners, status_message=model.status_message, status_tone=model.status_tone),
        summary_html=_summary_html(model.summary_items),
        form_html=form_html,
        help_links_html=_links_html(model.help_links, "pc-admin-auth-help-links", "Admin password help"),
        legal_links_html=_links_html(model.legal_links, "pc-admin-auth-legal-links", "Admin legal links"),
        no_script_message=model.no_script_message,
        body_class="pc-admin-password-change-page",
    )


__all__ = [
    "render_admin_login_page",
    "render_admin_password_change_page",
]
