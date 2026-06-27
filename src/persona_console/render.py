from __future__ import annotations

from dataclasses import asdict, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence

from .models import NavGroup, NavItem, PersonaConsoleConfig, StatusPill, UserPill
from .privacy import feature_enabled


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _nav_item(value: NavItem | Mapping[str, object]) -> NavItem:
    if isinstance(value, NavItem):
        return value
    if isinstance(value, (tuple, list)):
        label = str(value[1] if len(value) > 1 else "")
        return NavItem(
            label=label,
            href=str(value[0] if len(value) > 0 else "#"),
            badge=value[2] if len(value) > 2 else None,
        )
    data = dict(value)
    return NavItem(
        label=str(data.get("label") or ""),
        href=str(data.get("href") or "#"),
        active=str(data.get("active") or "") or None,
        badge=data.get("badge"),
        external=bool(data.get("external")),
        feature=str(data.get("feature") or ""),
    )


def _nav_group(value: NavGroup | Mapping[str, object]) -> NavGroup:
    if isinstance(value, NavGroup):
        return value
    if isinstance(value, (tuple, list)):
        return NavGroup(
            label=str(value[0] if len(value) > 0 else ""),
            items=value[1] if len(value) > 1 else (),
        )
    data = dict(value)
    return NavGroup(
        label=str(data.get("label") or ""),
        key=str(data.get("key") or "") or None,
        items=data.get("items") or (),
    )


def _badge_value(value: object, badges: Mapping[str, int]) -> int:
    if value is None or value == "":
        return 0
    if isinstance(value, int):
        return max(0, value)
    key = str(value)
    if key.isdigit():
        return int(key)
    return max(0, int(badges.get(key, 0) or 0))


def _badge_html(value: int) -> str:
    if value <= 0:
        return ""
    label = "999+" if value > 999 else str(value)
    return f'<span class="admin-nav-badge">{escape(label)}</span>'


def _item_active(active: str, item: NavItem, current_path: str = "") -> bool:
    if item.active and item.active == active:
        return True
    if current_path:
        href = item.href.rstrip("/") or "/"
        path = current_path.rstrip("/") or "/"
        return path == href or (href != "/" and path.startswith(href + "/"))
    return False


def active_nav_label(
    nav_groups: Sequence[NavGroup | Mapping[str, object]],
    active: str,
    current_path: str = "",
    features: Mapping[str, bool] | None = None,
) -> str:
    for raw_group in nav_groups:
        group = _nav_group(raw_group)
        for raw_item in group.items:
            item = _nav_item(raw_item)
            if item.feature and not feature_enabled(features, item.feature):
                continue
            if _item_active(active, item, current_path):
                return item.label or group.label or "Current"
    return active.replace("_", " ").replace("-", " ").title() or "Dashboard"


def render_nav_groups(
    nav_groups: Sequence[NavGroup | Mapping[str, object]],
    *,
    active: str,
    badges: Mapping[str, int] | None = None,
    current_path: str = "",
    features: Mapping[str, bool] | None = None,
) -> str:
    badge_map = badges or {}
    desktop: list[str] = []
    mobile: list[str] = []
    for raw_group in nav_groups:
        group = _nav_group(raw_group)
        items = [
            item
            for item in (_nav_item(item) for item in group.items)
            if not item.feature or feature_enabled(features, item.feature)
        ]
        if not items:
            continue
        group_active = group.key == active or any(_item_active(active, item, current_path) for item in items)
        group_badge = sum(_badge_value(item.badge, badge_map) for item in items)
        item_html: list[str] = []
        mobile_item_html: list[str] = []
        for item in items:
            is_active = _item_active(active, item, current_path)
            item_cls = "admin-nav-item is-active" if is_active else "admin-nav-item"
            mobile_cls = "admin-mobile-link is-active" if is_active else "admin-mobile-link"
            target = ' target="_blank" rel="noopener noreferrer"' if item.external else ""
            badge = _badge_html(_badge_value(item.badge, badge_map))
            item_html.append(
                f'<a class="{item_cls}" href="{escape(item.href)}"{target}>'
                f'<span class="admin-nav-text">{escape(item.label)}</span>{badge}</a>'
            )
            mobile_item_html.append(
                f'<a class="{mobile_cls}" href="{escape(item.href)}"{target}>'
                f'<span class="admin-nav-text">{escape(item.label)}</span>{badge}</a>'
            )
        summary_cls = "admin-nav-summary is-active" if group_active else "admin-nav-summary"
        desktop.append(
            f'<details class="admin-nav-group"><summary class="{summary_cls}">'
            f'<span>{escape(group.label)}</span>{_badge_html(group_badge)}</summary>'
            f'<div class="admin-nav-menu">{"".join(item_html)}</div></details>'
        )
        mobile.append(
            f'<section class="admin-mobile-section"><div class="admin-mobile-section-title">'
            f'{escape(group.label)}</div><div class="admin-mobile-links">'
            f'{"".join(mobile_item_html)}</div></section>'
        )
    label = active_nav_label(nav_groups, active, current_path, features)
    return (
        '<nav class="admin-nav-groups" aria-label="Admin sections">'
        + "".join(desktop)
        + '</nav><details class="admin-mobile-nav"><summary class="admin-mobile-toggle" '
        + 'aria-label="Open admin navigation"><span class="admin-menu-icon" aria-hidden="true">'
        + "<span></span><span></span><span></span></span>"
        + f"<span>{escape(label)}</span></summary><div class=\"admin-mobile-panel\">"
        + "".join(mobile)
        + "</div></details>"
    )


def render_status_pill(value: StatusPill | Mapping[str, object] | str) -> str:
    if isinstance(value, str):
        pill = StatusPill(value)
    elif isinstance(value, StatusPill):
        pill = value
    else:
        data = dict(value)
        pill = StatusPill(
            label=str(data.get("label") or ""),
            tone=str(data.get("tone") or "neutral"),
            title=str(data.get("title") or ""),
        )
    tone = pill.tone if pill.tone in {"good", "warn", "bad", "info", "neutral"} else "neutral"
    title = f' title="{escape(pill.title)}"' if pill.title else ""
    return f'<span class="status-pill status-{tone}"{title}><span></span>{escape(pill.label)}</span>'


def _fallback_initials(display: str) -> str:
    initials: list[str] = []
    for part in display.replace("-", " ").replace("_", " ").split():
        for char in part:
            if char.isalnum():
                initials.append(char.upper())
                break
        if len(initials) >= 2:
            return "".join(initials)
    compact = "".join(char for char in display if char.isalnum())
    return compact[:2].upper() or "AD"


def render_user_pill(user: UserPill | Mapping[str, object] | None) -> str:
    if not user:
        return ""
    data = _mapping(user)
    display = str(data.get("display_name") or data.get("operator") or data.get("username") or "Admin")
    username = str(data.get("username") or data.get("operator") or "")
    tier = str(data.get("tier") or data.get("access_tier") or "")
    source = str(data.get("source") or "")
    initials = str(data.get("initials") or "").strip()
    if not initials:
        initials = _fallback_initials(display)
    subtitle = " · ".join(part for part in (tier, source) if part)
    return (
        '<span class="admin-user-pill">'
        f'<span class="admin-user-avatar">{escape(initials[:3])}</span>'
        '<span class="admin-user-copy">'
        '<small>Logged in</small>'
        f'<strong>{escape(display)}</strong>'
        f'<em>{escape(subtitle)}</em>'
        '</span></span>'
    )


def render_live_controls(config: PersonaConsoleConfig) -> str:
    if not config.live_interval:
        return ""
    return f"""
<div id="live-pill"
     class="live-pill pc-live-pill"
     data-default-interval="{int(config.live_interval)}"
     data-storage-key="live:{escape(config.active)}"
     role="group"
     aria-label="Live refresh">
  <button type="button" id="live-toggle" class="live-pill-btn pc-live-toggle" aria-pressed="false" title="Toggle live auto-refresh">
    <span class="live-pill-dot pc-live-dot" aria-hidden="true"></span>
    <span class="live-pill-label pc-live-label">Paused</span>
  </button>
  <label class="live-pill-interval pc-live-interval" title="Auto-refresh interval (seconds)">
    <span class="live-pill-interval-prefix pc-live-interval-prefix" aria-hidden="true">every</span>
    <select id="live-interval" class="live-pill-select pc-live-select" aria-label="Refresh interval (seconds)">
      <option value="5">5s</option>
      <option value="15">15s</option>
      <option value="30">30s</option>
      <option value="60">60s</option>
    </select>
  </label>
</div>"""


def render_shell_html(
    config: PersonaConsoleConfig,
    body_html: str,
    *,
    current_path: str = "",
    extra_head: str = "",
    extra_body_end: str = "",
    flash_container: bool = True,
) -> str:
    nav_html = render_nav_groups(
        config.nav_groups,
        active=config.active,
        badges=config.nav_badges,
        current_path=current_path,
        features=config.features,
    )
    status = [render_user_pill(config.user)]
    status.extend(render_status_pill(pill) for pill in config.status_pills)
    if config.app_version:
        status.append(render_status_pill(StatusPill(config.app_version, "good", "Application version")))
    refresh = ""
    if config.include_refresh:
        refresh = (
            '<span id="page-refresh-status" class="page-refresh-status pc-page-refresh-status">'
            f"{escape(config.updated_label)}</span>"
            '<button type="button" id="page-refresh-button" class="page-refresh-button pc-page-refresh-button" '
            'aria-label="Refresh page"><span aria-hidden="true">&#10227;</span></button>'
        )
    live_target_open = ""
    live_target_close = ""
    if config.live_interval and config.live_url:
        attrs = f'id="live-target" data-live-url="{escape(config.live_url)}"'
        if config.live_hold_selector:
            attrs += f' data-live-hold-when="{escape(config.live_hold_selector)}"'
        live_target_open = f"<div {attrs}>"
        live_target_close = "</div>"
    legacy_refresh_alias = ""
    if config.legacy_refresh_global:
        legacy_name = "".join(ch for ch in config.legacy_refresh_global if ch.isalnum() or ch in {"_", "$"})
        if legacy_name:
            legacy_refresh_alias = (
                "<script>window."
                + legacy_name
                + " = function(options) { return window.__personaConsoleRefreshLiveTarget"
                + " ? window.__personaConsoleRefreshLiveTarget(options) : false; };</script>"
            )
    icon = ""
    if config.icon_url:
        icon = (
            '<span class="admin-brand-icon-wrap" aria-hidden="true">'
            f'<img class="admin-brand-icon" src="{escape(config.icon_url)}" alt="" width="32" height="32">'
            '</span>'
        )
    brand = (
        f'<a href="{escape(config.home_url)}" class="admin-brand">{icon}'
        f'<span class="admin-brand-copy"><strong>{escape(config.brand_name)}</strong>'
        '<span>admin</span></span></a>'
    )
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
  <title>{escape(config.page_title)} · {escape(config.brand_name)} admin</title>
  <style>
:root {{
{config.theme.css_variables()}
}}
  </style>
  <link rel="stylesheet" href="{escape(config.static_base_url.rstrip('/'))}/persona-console.css">
  {extra_head}
</head>
<body class="admin-theme-bubble admin-shell persona-console-shell">
  <header class="admin-topbar">
    <div class="admin-header-inner {escape(config.max_width_class)}">
      {brand}
      {nav_html}
      <div class="admin-status">
        {''.join(status)}
      </div>
    </div>
  </header>
  <main class="admin-main {escape(config.max_width_class)}">
    <section class="page-head">
      <div>
        <h1>{escape(config.page_title)}</h1>
        <div class="sub">{escape(config.page_subtitle)}</div>
      </div>
      <div class="page-actions">{refresh}{render_live_controls(config)}</div>
    </section>
    {'<div id="flash-stack" class="flash-stack pc-flash-stack" aria-live="polite"></div>' if flash_container else ''}
    {live_target_open}
    {body_html}
    {live_target_close}
  </main>
  <script src="{escape(config.static_base_url.rstrip('/'))}/persona-console.js"></script>
  {legacy_refresh_alias}
  {extra_body_end}
</body>
</html>"""
