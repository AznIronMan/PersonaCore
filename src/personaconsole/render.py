from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence

from .models import BrandAssets, LiveRefreshConfig, NavGroup, NavItem, PersonaConsoleConfig, StatusPill, UserPill
from .privacy import feature_enabled


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _mapped_text(data: Mapping[str, Any], key: str, default: str = "") -> str:
    if key in data:
        return str(data.get(key) or "")
    return default


def _brand_assets(config: PersonaConsoleConfig) -> BrandAssets:
    data = _mapping(config.brand_assets)
    return BrandAssets(
        name=str(data.get("name") or config.brand_name or ""),
        admin_title=str(data.get("admin_title") or ""),
        admin_subtitle=_mapped_text(data, "admin_subtitle", "admin"),
        small_logo_url=str(data.get("small_logo_url") or config.icon_url or ""),
        large_logo_url=str(data.get("large_logo_url") or ""),
        wordmark_url=str(data.get("wordmark_url") or ""),
        lockup_url=str(data.get("lockup_url") or ""),
        favicon_url=str(data.get("favicon_url") or ""),
        signature_text=str(data.get("signature_text") or ""),
        alt_text=str(data.get("alt_text") or data.get("name") or config.brand_name or ""),
        home_url=str(data.get("home_url") or config.home_url or "/"),
    )


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


def _bool(value: object, default: bool = False) -> bool:
    if value is None:
        return default
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    raw = str(value).strip().lower()
    if raw in {"1", "true", "yes", "on"}:
        return True
    if raw in {"0", "false", "no", "off"}:
        return False
    return default


def _positive_int(value: object, default: int, *, minimum: int = 0, maximum: int = 3600) -> int:
    try:
        number = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        number = default
    return max(minimum, min(maximum, number))


def _safe_dom_id(value: object, default: str) -> str:
    raw = str(value or "").strip()
    safe = "".join(char if char.isalnum() or char in {"-", "_"} else "-" for char in raw)
    safe = safe.strip("-_")
    return safe or default


def _interval_options(value: object, default: Sequence[int]) -> tuple[int, ...]:
    if isinstance(value, str):
        values: Sequence[object] = [part.strip() for part in value.split(",")]
    elif isinstance(value, Sequence):
        values = value
    else:
        values = default
    options: list[int] = []
    for raw in values:
        option = _positive_int(raw, 0, minimum=1, maximum=3600)
        if option and option not in options:
            options.append(option)
    return tuple(options or default or (15,))


def _attr(name: str, value: object, *, boolean: bool = False) -> str:
    if boolean:
        return f" {name}" if value else ""
    if value is None or value == "":
        return ""
    return f' {name}="{escape(str(value), quote=True)}"'


def _live_refresh_from_mapping(data: Mapping[str, object], fallback: LiveRefreshConfig | None = None) -> LiveRefreshConfig:
    base = fallback or LiveRefreshConfig()
    normalized = dict(data)
    aliases = {
        "endpoint": "url",
        "live_url": "url",
        "interval": "interval_seconds",
        "poll_interval": "interval_seconds",
        "stale_after": "stale_after_seconds",
        "fallback_url": "fallback_href",
    }
    for alias, canonical in aliases.items():
        if alias in normalized and canonical not in normalized:
            normalized[canonical] = normalized[alias]
    field_names = {field.name for field in fields(LiveRefreshConfig)}
    values: dict[str, object] = {name: getattr(base, name) for name in field_names}
    for name in field_names:
        if name in normalized:
            values[name] = normalized[name]
    values["enabled"] = _bool(values.get("enabled"), bool(base.enabled))
    values["interval_seconds"] = _positive_int(values.get("interval_seconds"), base.interval_seconds, minimum=1)
    values["stale_after_seconds"] = _positive_int(values.get("stale_after_seconds"), 0, minimum=0)
    values["paused"] = _bool(values.get("paused"), bool(base.paused))
    values["include_controls"] = _bool(values.get("include_controls"), bool(base.include_controls))
    values["interval_options"] = _interval_options(values.get("interval_options"), base.interval_options)
    return LiveRefreshConfig(**values)  # type: ignore[arg-type]


def _live_refresh_config(value: PersonaConsoleConfig | LiveRefreshConfig | Mapping[str, object]) -> LiveRefreshConfig:
    if isinstance(value, LiveRefreshConfig):
        return value
    if isinstance(value, PersonaConsoleConfig):
        default = LiveRefreshConfig(
            enabled=bool(value.live_interval),
            key=value.active or "page",
            url=value.live_url,
            interval_seconds=_positive_int(value.live_interval, 15, minimum=1),
            target_id="live-target",
            controls_id="live-pill",
            status_id="page-refresh-status",
            hold_selector=value.live_hold_selector,
            storage_key=f"live:{value.active or 'page'}",
            updated_label=value.updated_label,
        )
        if value.live_refresh:
            return _live_refresh_from_mapping(_mapping(value.live_refresh), default)
        return default
    return _live_refresh_from_mapping(dict(value))


def live_refresh_attributes(config: PersonaConsoleConfig | LiveRefreshConfig | Mapping[str, object]) -> str:
    model = _live_refresh_config(config)
    if not model.enabled or not model.url:
        return ""
    target_id = _safe_dom_id(model.target_id, "live-target")
    key = _safe_dom_id(model.key, target_id)
    target_selector = model.target_selector or f"#{target_id}"
    classes = "pc-live-region"
    return (
        _attr("id", target_id)
        + _attr("class", classes)
        + _attr("data-pc-live-target", True, boolean=True)
        + _attr("data-pc-live-key", key)
        + _attr("data-pc-live-url", model.url)
        + _attr("data-live-url", model.url)
        + _attr("data-pc-live-target-selector", target_selector)
        + _attr("data-pc-live-interval", model.interval_seconds)
        + _attr("data-pc-live-hold-when", model.hold_selector)
        + _attr("data-live-hold-when", model.hold_selector)
        + _attr("data-pc-live-stale-after", model.stale_after_seconds)
        + _attr("data-pc-live-status", _safe_dom_id(model.status_id, "page-refresh-status"))
        + _attr("data-pc-live-updated-label", model.updated_label)
        + _attr("data-pc-live-stale-label", model.stale_label)
        + _attr("data-pc-live-error-label", model.error_label)
    ).strip()


def render_live_region(body_html: str, config: PersonaConsoleConfig | LiveRefreshConfig | Mapping[str, object]) -> str:
    attrs = live_refresh_attributes(config)
    if not attrs:
        return body_html
    return f"<div {attrs}>{body_html}</div>"


def render_live_status(config: PersonaConsoleConfig | LiveRefreshConfig | Mapping[str, object] | None = None) -> str:
    model = _live_refresh_config(config) if config is not None else LiveRefreshConfig()
    status_id = _safe_dom_id(model.status_id, "page-refresh-status")
    label = model.updated_label or "Updated now"
    return (
        f'<span id="{escape(status_id, quote=True)}" '
        'class="page-refresh-status pc-page-refresh-status" data-pc-live-status-text>'
        f"{escape(label)}</span>"
    )


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


def render_live_controls(config: PersonaConsoleConfig | LiveRefreshConfig | Mapping[str, object]) -> str:
    model = _live_refresh_config(config)
    if not model.enabled or not model.include_controls:
        return ""
    target_id = _safe_dom_id(model.target_id, "live-target")
    controls_id = _safe_dom_id(model.controls_id, "live-pill")
    key = _safe_dom_id(model.key, target_id)
    status_id = _safe_dom_id(model.status_id, "page-refresh-status")
    interval = _positive_int(model.interval_seconds, 15, minimum=1)
    options = _interval_options(model.interval_options, (5, 15, 30, 60))
    if interval not in options:
        options = tuple(sorted(options + (interval,)))
    option_html = "".join(
        f'<option value="{option}"{" selected" if option == interval else ""}>{option}s</option>' for option in options
    )
    storage_key = model.storage_key or f"live:{key}"
    target_selector = model.target_selector or f"#{target_id}"
    toggle_id = "live-toggle" if controls_id == "live-pill" else f"{controls_id}-toggle"
    interval_id = "live-interval" if controls_id == "live-pill" else f"{controls_id}-interval"
    pressed = "false" if model.paused else "true"
    live_class = "" if model.paused else " live-on"
    label = model.paused_label if model.paused else model.label
    fallback_href = model.fallback_href or ""
    noscript = (
        f'<noscript><a class="pc-live-noscript" href="{escape(fallback_href, quote=True)}">'
        f"{escape(model.manual_label)}</a></noscript>"
        if fallback_href
        else ""
    )
    return f"""
<div id="{escape(controls_id, quote=True)}"
     class="live-pill pc-live-pill"
     data-pc-live-controls
     data-pc-live-for="{escape(target_selector, quote=True)}"
     data-pc-live-key="{escape(key, quote=True)}"
     data-pc-live-status="{escape(status_id, quote=True)}"
     data-pc-live-paused-label="{escape(model.paused_label, quote=True)}"
     data-pc-live-label="{escape(model.label, quote=True)}"
     data-pc-live-refreshing-label="{escape(model.refreshing_label, quote=True)}"
     data-pc-live-updated-label="{escape(model.updated_label, quote=True)}"
     data-pc-live-stale-label="{escape(model.stale_label, quote=True)}"
     data-pc-live-error-label="{escape(model.error_label, quote=True)}"
     data-pc-live-paused="{"true" if model.paused else "false"}"
     data-default-interval="{interval}"
     data-storage-key="{escape(storage_key, quote=True)}"
     role="group"
     aria-label="Live refresh">
  <button type="button" id="{escape(toggle_id, quote=True)}" class="live-pill-btn pc-live-toggle{live_class}" data-pc-live-toggle aria-pressed="{pressed}" title="Toggle live auto-refresh">
    <span class="live-pill-dot pc-live-dot" aria-hidden="true"></span>
    <span class="live-pill-label pc-live-label">{escape(label)}</span>
  </button>
  <label class="live-pill-interval pc-live-interval" title="Auto-refresh interval (seconds)">
    <span class="live-pill-interval-prefix pc-live-interval-prefix" aria-hidden="true">every</span>
    <select id="{escape(interval_id, quote=True)}" class="live-pill-select pc-live-select" data-pc-live-interval aria-label="Refresh interval (seconds)">
      {option_html}
    </select>
  </label>
  {noscript}
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
    live_config = _live_refresh_config(config)
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
            render_live_status(live_config)
            +
            '<button type="button" id="page-refresh-button" class="page-refresh-button pc-page-refresh-button" '
            'data-pc-live-manual aria-label="Refresh page"><span aria-hidden="true">&#10227;</span></button>'
        )
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
    brand_assets = _brand_assets(config)
    icon = ""
    if brand_assets.small_logo_url:
        icon = (
            '<span class="admin-brand-icon-wrap" aria-hidden="true">'
            f'<img class="admin-brand-icon" src="{escape(brand_assets.small_logo_url)}" alt="" width="32" height="32">'
            '</span>'
        )
    brand_title = brand_assets.admin_title or brand_assets.name
    subtitle_html = f"<span>{escape(brand_assets.admin_subtitle)}</span>" if brand_assets.admin_subtitle else ""
    wordmark = brand_assets.wordmark_url or brand_assets.large_logo_url
    if brand_assets.lockup_url:
        brand_copy_html = (
            f'<img class="admin-brand-lockup" src="{escape(brand_assets.lockup_url)}" '
            f'alt="{escape(brand_assets.alt_text or brand_title)}" height="38">'
        )
    elif wordmark:
        brand_copy_html = (
            f'<img class="admin-brand-wordmark" src="{escape(wordmark)}" '
            f'alt="{escape(brand_assets.alt_text or brand_title)}" height="28">'
            f"{subtitle_html}"
        )
    else:
        brand_copy_html = f"<strong>{escape(brand_title)}</strong>{subtitle_html}"
    brand = (
        f'<a href="{escape(brand_assets.home_url)}" class="admin-brand">{icon}'
        f'<span class="admin-brand-copy">{brand_copy_html}</span></a>'
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
      <div class="page-actions">{refresh}{render_live_controls(live_config)}</div>
    </section>
    {'<div id="flash-stack" class="flash-stack pc-flash-stack" aria-live="polite"></div>' if flash_container else ''}
    {render_live_region(body_html, live_config)}
  </main>
  <script src="{escape(config.static_base_url.rstrip('/'))}/persona-console.js"></script>
  {legacy_refresh_alias}
  {extra_body_end}
</body>
</html>"""
