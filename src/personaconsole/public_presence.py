from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
import json
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    BrandAssets,
    ChatPageConfig,
    ConnectorGroup,
    ConnectorOption,
    LegalNotice,
    LoginPageConfig,
    PublicLink,
    PublicMediaConfig,
    PublicMediaSource,
    PublicSettingsSurfaceConfig,
    PublicSplashPageConfig,
    PublicThemeOption,
)
from .privacy import feature_enabled


PUBLIC_PRESENCE_FEATURE = "public_presence"

PUBLIC_THEME_KEYS = (
    "studio",
    "paper",
    "traditional",
    "console",
    "matrix",
    "midnight",
    "sunrise",
    "gallery",
    "broadcast",
    "ink",
    "minimal",
    "high-contrast",
)

_THEME_LABELS = {
    "studio": "Studio",
    "paper": "Paper",
    "traditional": "Traditional",
    "console": "Console",
    "matrix": "Matrix",
    "midnight": "Midnight",
    "sunrise": "Sunrise",
    "gallery": "Gallery",
    "broadcast": "Broadcast",
    "ink": "Ink",
    "minimal": "Minimal",
    "high-contrast": "High Contrast",
}

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "warn": "warn",
    "warning": "warn",
    "held": "warn",
    "pending": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "info": "info",
    "configured": "info",
    "neutral": "neutral",
    "unknown": "neutral",
    "": "neutral",
}

T = TypeVar("T")


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


def _key(value: object, default: str = "") -> str:
    raw = str(value or default or "").strip().lower().replace("_", "-")
    safe = "".join(char for char in raw if char.isalnum() or char == "-")
    return safe or default


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _theme_key(value: object) -> str:
    key = _key(value, "studio")
    return key if key in PUBLIC_THEME_KEYS else "studio"


def _css_value(value: object, default: str) -> str:
    text = str(value or default).strip()
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 %.-_()")
    return text if text and all(char in allowed for char in text) else default


def _asset_base(static_base_url: str) -> str:
    return (static_base_url or "/persona-console/static").rstrip("/")


def _attrs(**attrs: str) -> str:
    parts: list[str] = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(str(value), quote=True)}"')
    return "".join(parts)


def public_theme_options(selected: str = "studio") -> tuple[PublicThemeOption, ...]:
    selected_key = _theme_key(selected)
    return tuple(
        PublicThemeOption(key, _THEME_LABELS[key], selected=key == selected_key)
        for key in PUBLIC_THEME_KEYS
    )


def public_presence_feature_enabled(
    config: PublicSettingsSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, PublicSettingsSurfaceConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or PUBLIC_PRESENCE_FEATURE), default=True)


def _brand(value: BrandAssets | Mapping[str, object] | None, *, default_name: str = "Persona") -> BrandAssets:
    model = _coerce(value, BrandAssets, {"name": default_name, "alt_text": default_name, "home_url": "/"})
    name = str(model.name or default_name)
    alt = str(model.alt_text or name)
    return BrandAssets(
        name=name,
        small_logo_url=str(model.small_logo_url or ""),
        large_logo_url=str(model.large_logo_url or ""),
        wordmark_url=str(model.wordmark_url or ""),
        favicon_url=str(model.favicon_url or ""),
        signature_text=str(model.signature_text or ""),
        alt_text=alt,
        home_url=str(model.home_url or "/"),
    )


def render_brand_logo(
    brand: BrandAssets | Mapping[str, object] | None,
    *,
    variant: str = "small",
    fallback_name: str = "Persona",
) -> str:
    model = _brand(brand, default_name=fallback_name)
    selected = ""
    if variant == "large":
        selected = model.large_logo_url or model.wordmark_url or model.small_logo_url
    elif variant == "wordmark":
        selected = model.wordmark_url or model.large_logo_url or model.small_logo_url
    else:
        selected = model.small_logo_url or model.large_logo_url or model.wordmark_url
    cls = f"pc-public-brand-logo pc-public-brand-logo-{_key(variant, 'small')}"
    if selected:
        return f'<img class="{cls}" src="{escape(selected)}" alt="{escape(model.alt_text)}">'
    initials = "".join(part[0].upper() for part in model.name.replace("-", " ").replace("_", " ").split()[:2])
    return f'<span class="{cls} pc-public-brand-logo-fallback" aria-hidden="true">{escape(initials or "P")}</span>'


def _brand_header(brand: BrandAssets, *, logo_variant: str = "small") -> str:
    signature = f'<span>{escape(brand.signature_text)}</span>' if brand.signature_text else ""
    return (
        f'<a class="pc-public-brand" href="{escape(brand.home_url)}">'
        f'{render_brand_logo(brand, variant=logo_variant, fallback_name=brand.name)}'
        '<span class="pc-public-brand-copy">'
        f'<strong>{escape(brand.name)}</strong>'
        f'{signature}'
        '</span></a>'
    )


def _media_sources(model: PublicMediaConfig) -> list[PublicMediaSource]:
    raw_sources: Sequence[PublicMediaSource | Mapping[str, object]]
    raw_sources = model.sources or ()
    sources = [
        _coerce(source, PublicMediaSource, {"src": ""})
        for source in raw_sources
    ]
    if not sources and model.src:
        sources.append(PublicMediaSource(src=model.src))
    return [source for source in sources if source.src]


def _media_kind(model: PublicMediaConfig, sources: Sequence[PublicMediaSource]) -> str:
    kind = _key(model.kind, "image")
    if kind in {"image", "slideshow", "video"}:
        return kind
    first = sources[0].src.lower() if sources else ""
    mime = sources[0].mime_type.lower() if sources else ""
    if mime.startswith("video/") or first.endswith((".mp4", ".webm", ".mov")):
        return "video"
    if len(sources) > 1:
        return "slideshow"
    return "image"


def render_public_media(
    media: PublicMediaConfig | Mapping[str, object] | None,
    *,
    surface: str = "splash",
    fallback_alt: str = "Persona media",
) -> str:
    model = _coerce(media, PublicMediaConfig)
    sources = _media_sources(model)
    kind = _media_kind(model, sources)
    focus_x = _css_value(model.focus_x, "50%")
    focus_y = _css_value(model.focus_y, "50%")
    overlay = _key(model.overlay, "medium")
    if overlay not in {"none", "soft", "medium", "strong"}:
        overlay = "medium"
    style = f"--pc-public-focus-x:{focus_x};--pc-public-focus-y:{focus_y};"
    alt = model.alt_text or fallback_alt
    base_cls = (
        f'pc-public-media pc-public-media-{kind} pc-public-media-{_key(surface, "surface")} '
        f'pc-public-overlay-{overlay}'
    )
    if not sources:
        return (
            f'<div class="{base_cls} pc-public-media-empty" data-pc-public-media style="{escape(style)}">'
            f'<span>{escape(alt)}</span></div>'
        )
    if kind == "video":
        return _video_media_html(model, sources, base_cls, style, alt)
    if kind == "slideshow":
        return _slideshow_media_html(model, sources, base_cls, style, alt)
    source = sources[0]
    return (
        f'<figure class="{base_cls}" data-pc-public-media style="{escape(style)}">'
        f'<img src="{escape(source.src)}" alt="{escape(alt)}" loading="eager" decoding="async">'
        '</figure>'
    )


def _source_type_attr(source: PublicMediaSource) -> str:
    return f' type="{escape(source.mime_type, quote=True)}"' if source.mime_type else ""


def _source_media_attr(source: PublicMediaSource) -> str:
    return f' media="{escape(source.media, quote=True)}"' if source.media else ""


def _video_media_html(
    model: PublicMediaConfig,
    sources: Sequence[PublicMediaSource],
    base_cls: str,
    style: str,
    alt: str,
) -> str:
    poster = model.poster_url or next((source.poster_url for source in sources if source.poster_url), "")
    autoplay = " autoplay" if model.autoplay else ""
    muted = " muted" if model.muted else ""
    loop = " loop" if model.loop else ""
    controls = " controls" if model.controls else ""
    poster_attr = f' poster="{escape(poster)}"' if poster else ""
    source_html = "".join(
        f'<source src="{escape(source.src)}"{_source_type_attr(source)}{_source_media_attr(source)}>'
        for source in sources
    )
    audio = ""
    if model.audio_src:
        audio = f'<audio data-pc-public-audio src="{escape(model.audio_src)}" preload="metadata"></audio>'
    sound = _sound_control(model) if model.controls and (model.audio_src or sources) else ""
    return (
        f'<figure class="{base_cls}" data-pc-public-media data-pc-media-muted="{str(model.muted).lower()}" '
        f'style="{escape(style)}">'
        f'<video class="pc-public-media-video" playsinline{autoplay}{muted}{loop}{controls}{poster_attr} '
        f'aria-label="{escape(alt)}" data-pc-public-video>{source_html}</video>'
        f'{audio}{sound}</figure>'
    )


def _slideshow_media_html(
    model: PublicMediaConfig,
    sources: Sequence[PublicMediaSource],
    base_cls: str,
    style: str,
    alt: str,
) -> str:
    slides = [{"src": source.src, "alt": source.label or alt} for source in sources]
    payload = escape(json.dumps(slides), quote=True)
    first = sources[0]
    dots = "".join(
        f'<span class="pc-public-slide-dot{" is-active" if index == 0 else ""}" aria-hidden="true"></span>'
        for index, _source in enumerate(sources)
    )
    return (
        f'<figure class="{base_cls}" data-pc-public-media data-pc-slideshow '
        f'data-pc-slide-srcs="{payload}" data-pc-slide-interval="{int(model.interval_ms or 7000)}" '
        f'style="{escape(style)}">'
        f'<img src="{escape(first.src)}" alt="{escape(first.label or alt)}" loading="eager" decoding="async" '
        'data-pc-slide-image>'
        f'<div class="pc-public-slide-dots">{dots}</div>'
        f'<noscript><img src="{escape(first.src)}" alt="{escape(first.label or alt)}"></noscript>'
        '</figure>'
    )


def _sound_control(model: PublicMediaConfig) -> str:
    pressed = "false" if model.muted else "true"
    label = "Sound off" if model.muted else "Sound on"
    return (
        '<button type="button" class="pc-public-sound-toggle" data-pc-sound-toggle '
        f'aria-pressed="{pressed}"><span data-pc-sound-label>{escape(label)}</span></button>'
    )


def _link(value: PublicLink | Mapping[str, object]) -> PublicLink:
    return _coerce(value, PublicLink, {"label": "", "href": ""})


def _links_html(links: Sequence[PublicLink | Mapping[str, object]], *, class_name: str) -> str:
    items = []
    for raw_link in links:
        link = _link(raw_link)
        if not link.href or not link.label:
            continue
        target = ' target="_blank"' if link.external else ""
        rel = f' rel="{escape(link.rel, quote=True)}"' if link.external and link.rel else ""
        title = f' title="{escape(link.title, quote=True)}"' if link.title else ""
        icon = f'<span class="pc-public-link-icon">{escape(link.icon)}</span>' if link.icon else ""
        items.append(
            f'<a class="{class_name}-item" href="{escape(link.href)}"{target}{rel}{title}>'
            f'{icon}<span>{escape(link.label)}</span></a>'
        )
    if not items:
        return ""
    return f'<nav class="{class_name}" aria-label="Public links">{"".join(items)}</nav>'


def _legal_notice(value: LegalNotice | Mapping[str, object]) -> LegalNotice:
    return _coerce(value, LegalNotice, {"key": "", "label": ""})


def _legal_html(notices: Sequence[LegalNotice | Mapping[str, object]]) -> tuple[str, str]:
    links: list[str] = []
    modals: list[str] = []
    for raw_notice in notices:
        notice = _legal_notice(raw_notice)
        key = _key(notice.key or notice.label, "legal")
        if notice.href:
            links.append(f'<a href="{escape(notice.href)}">{escape(notice.label)}</a>')
        elif notice.body:
            links.append(
                f'<button type="button" data-pc-legal-open="{escape(key, quote=True)}">'
                f'{escape(notice.label)}</button>'
            )
            modals.append(
                f'<div class="pc-public-modal" role="dialog" aria-modal="true" hidden '
                f'data-pc-legal-modal="{escape(key, quote=True)}">'
                '<div class="pc-public-modal-panel">'
                f'<h2>{escape(notice.label)}</h2>'
                f'<p>{escape(notice.body)}</p>'
                '<button type="button" class="pc-public-modal-close" data-pc-modal-close>Close</button>'
                '</div></div>'
            )
    if not links:
        return "", "".join(modals)
    return f'<div class="pc-public-legal">{"".join(links)}</div>', "".join(modals)


def _connector(value: ConnectorOption | Mapping[str, object]) -> ConnectorOption:
    return _coerce(value, ConnectorOption, {"key": "", "label": ""})


def _connector_group(value: ConnectorGroup | Mapping[str, object]) -> ConnectorGroup:
    return _coerce(value, ConnectorGroup, {"label": "", "connectors": ()})


def render_connector_groups(
    groups: Sequence[ConnectorGroup | Mapping[str, object]],
    *,
    aria_label: str = "Connectors",
) -> str:
    group_html: list[str] = []
    for raw_group in groups:
        group = _connector_group(raw_group)
        connectors = [_connector(connector) for connector in group.connectors]
        connector_html = [_connector_html(connector) for connector in connectors if connector.key or connector.label]
        if not connector_html:
            continue
        label = group.label or "Connectors"
        description = f'<p>{escape(group.description)}</p>' if group.description else ""
        group_key = _key(group.key or label, "connectors")
        group_html.append(
            f'<section class="pc-connector-group" data-connector-group="{escape(group_key, quote=True)}">'
            f'<div class="pc-connector-group-head"><h2>{escape(label)}</h2>{description}</div>'
            f'<div class="pc-connector-grid">{"".join(connector_html)}</div></section>'
        )
    if not group_html:
        return ""
    return f'<div class="pc-connector-groups" aria-label="{escape(aria_label, quote=True)}">{"".join(group_html)}</div>'


def _connector_html(connector: ConnectorOption) -> str:
    tone = _tone(connector.tone or connector.status)
    key = _key(connector.key or connector.label, "connector")
    classes = [
        "pc-connector-option",
        f"pc-connector-tone-{tone}",
        "is-enabled" if connector.enabled else "is-disabled",
        "is-configured" if connector.configured else "is-unconfigured",
    ]
    if connector.selected:
        classes.append("is-selected")
    status = connector.status or ("Configured" if connector.configured else "Not configured")
    attrs = (
        f'class="{" ".join(classes)}" data-connector-key="{escape(key, quote=True)}" '
        f'data-connector-enabled="{str(connector.enabled).lower()}" '
        f'data-connector-configured="{str(connector.configured).lower()}"'
    )
    if connector.action:
        attrs += f' data-connector-action="{escape(connector.action, quote=True)}"'
    icon = connector.icon or key[:1].upper()
    description = f'<small>{escape(connector.description)}</small>' if connector.description else ""
    body = (
        f'<span class="pc-connector-icon">{escape(icon)}</span>'
        '<span class="pc-connector-copy">'
        f'<strong>{escape(connector.label)}</strong>'
        f'{description}'
        '</span>'
        f'<span class="pc-connector-status">{escape(status)}</span>'
    )
    if connector.enabled and connector.href:
        return f'<a {attrs} href="{escape(connector.href)}">{body}</a>'
    disabled = " disabled" if not connector.enabled else ""
    return f'<button type="button" {attrs}{disabled}>{body}</button>'


def _theme_options_html(options: Sequence[PublicThemeOption | Mapping[str, object] | str], selected: str) -> str:
    if not options:
        options = public_theme_options(selected)
    selected_key = _theme_key(selected)
    rendered: list[str] = []
    for raw_option in options:
        if isinstance(raw_option, str):
            key = _theme_key(raw_option)
            option = PublicThemeOption(key, _THEME_LABELS[key], selected=key == selected_key)
        else:
            data = _mapping(raw_option)
            key = _theme_key(data.get("key") or data.get("label") or selected_key)
            option = _coerce(raw_option, PublicThemeOption, {"key": key, "label": _THEME_LABELS[key]})
            option = PublicThemeOption(
                key=key,
                label=option.label or _THEME_LABELS[key],
                selected=bool(option.selected) or key == selected_key,
                description=option.description,
            )
        checked = " checked" if option.selected else ""
        description = f'<span>{escape(option.description)}</span>' if option.description else ""
        rendered.append(
            f'<label class="pc-public-theme-choice pc-public-theme-choice-{escape(option.key)}">'
            f'<input type="radio" name="public_theme" value="{escape(option.key)}"{checked}>'
            f'<strong>{escape(option.label)}</strong>{description}</label>'
        )
    return f'<div class="pc-public-theme-grid">{"".join(rendered)}</div>'


def _public_head(title: str, brand: BrandAssets, static_base_url: str, *, meta_description: str = "") -> str:
    base = _asset_base(static_base_url)
    favicon = f'  <link rel="icon" href="{escape(brand.favicon_url)}">\n' if brand.favicon_url else ""
    meta = f'  <meta name="description" content="{escape(meta_description, quote=True)}">\n' if meta_description else ""
    return (
        "<head>\n"
        '  <meta charset="utf-8">\n'
        '  <meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">\n'
        f"  <title>{escape(title)} · {escape(brand.name)}</title>\n"
        f"{meta}{favicon}"
        f'  <link rel="stylesheet" href="{escape(base)}/persona-public.css">\n'
        "</head>"
    )


def render_public_splash_page(config: PublicSplashPageConfig | Mapping[str, object]) -> str:
    model = _coerce(config, PublicSplashPageConfig)
    brand = _brand(model.brand, default_name=model.title or "Persona")
    title = model.page_title or model.title or brand.name
    legal_links, modals = _legal_html(model.legal_notices)
    social = _links_html(model.social_links, class_name="pc-public-social")
    signup = _signup_form_html(model)
    media = render_public_media(model.media, surface="splash", fallback_alt=f"{brand.name} hero media")
    base = _asset_base(model.static_base_url)
    theme = _theme_key(model.theme)
    return f"""<!doctype html>
<html lang="en" class="pc-public-root pc-public-theme-{theme}">
{_public_head(title, brand, model.static_base_url, meta_description=model.meta_description)}
<body class="pc-public-page pc-public-splash-page">
  <main class="pc-public-splash">
    {media}
    <header class="pc-public-header">
      {_brand_header(brand, logo_variant="large")}
    </header>
    <section class="pc-public-splash-content">
      <p class="pc-public-eyebrow">{escape(model.subtitle)}</p>
      <h1>{escape(model.title)}</h1>
      <p class="pc-public-lede">{escape(model.description)}</p>
      <div class="pc-public-actions">
        <a class="pc-public-primary-action" href="{escape(model.chat_href)}">{escape(model.chat_label)}</a>
      </div>
      {signup}
      {social}
      {legal_links}
    </section>
  </main>
  {modals}
  <script src="{escape(base)}/persona-public.js"></script>
</body>
</html>"""


def _signup_form_html(model: PublicSplashPageConfig) -> str:
    if not model.update_form_action:
        return ""
    return (
        '<form class="pc-public-signup" method="post" data-pc-signup-form '
        f'action="{escape(model.update_form_action)}">'
        f'<input type="hidden" name="source" value="{escape(model.update_form_source, quote=True)}">'
        f'<label><span>{escape(model.update_form_label)}</span>'
        f'<input type="email" name="email" placeholder="{escape(model.update_form_placeholder, quote=True)}" required></label>'
        '<button type="submit">Join</button>'
        '<output class="pc-public-form-status" data-pc-form-status></output>'
        '</form>'
    )


def render_login_page(config: LoginPageConfig | Mapping[str, object]) -> str:
    model = _coerce(config, LoginPageConfig)
    brand = _brand(model.brand, default_name="Persona")
    title = model.page_title or model.title
    legal_links, modals = _legal_html(model.legal_notices)
    connectors = render_connector_groups(model.connector_groups, aria_label="Login connectors")
    media = render_public_media(model.media, surface="login", fallback_alt=f"{brand.name} login media")
    status = _status_html(model.status_message, model.status_tone)
    base = _asset_base(model.static_base_url)
    theme = _theme_key(model.theme)
    return f"""<!doctype html>
<html lang="en" class="pc-public-root pc-public-theme-{theme}">
{_public_head(title, brand, model.static_base_url)}
<body class="pc-public-page pc-public-login-page">
  <main class="pc-public-auth-layout">
    <aside class="pc-public-auth-hero">
      {media}
      <div class="pc-public-auth-hero-copy">
        {_brand_header(brand, logo_variant="large")}
        <p>{escape(model.subtitle)}</p>
      </div>
    </aside>
    <section class="pc-public-auth-panel" aria-label="Login">
      {_brand_header(brand)}
      <h1>{escape(model.title)}</h1>
      {status}
      {connectors}
      {_login_forms_html(model)}
      {legal_links}
    </section>
  </main>
  {modals}
  <script src="{escape(base)}/persona-public.js"></script>
</body>
</html>"""


def _status_html(message: str, tone: str) -> str:
    if not message:
        return ""
    return f'<div class="pc-public-status pc-public-status-{_tone(tone)}">{escape(message)}</div>'


def _login_forms_html(model: LoginPageConfig) -> str:
    forms: list[str] = []
    if model.email_enabled and model.email_action:
        forms.append(
            f'<form class="pc-public-login-form" method="post" action="{escape(model.email_action)}">'
            f'<input type="hidden" name="next" value="{escape(model.next_url, quote=True)}">'
            f'<label><span>{escape(model.email_label)}</span>'
            f'<input type="email" name="email" placeholder="{escape(model.email_placeholder, quote=True)}" required></label>'
            '<button type="submit">Continue</button></form>'
        )
    if model.phone_enabled and model.phone_action:
        forms.append(
            f'<form class="pc-public-login-form" method="post" action="{escape(model.phone_action)}">'
            f'<input type="hidden" name="next" value="{escape(model.next_url, quote=True)}">'
            f'<label><span>{escape(model.phone_label)}</span>'
            f'<input type="tel" name="phone" placeholder="{escape(model.phone_placeholder, quote=True)}" required></label>'
            '<button type="submit">Send code</button></form>'
        )
    if not forms:
        return '<p class="pc-public-empty">No login methods are configured.</p>'
    return '<div class="pc-public-login-forms">' + "".join(forms) + "</div>"


def render_chat_page(config: ChatPageConfig | Mapping[str, object]) -> str:
    model = _coerce(config, ChatPageConfig)
    brand = _brand(model.brand, default_name="Persona")
    title = model.page_title or model.title
    legal_links, modals = _legal_html(model.legal_notices)
    connectors = render_connector_groups(model.connector_groups, aria_label="Chat connectors")
    media = render_public_media(model.media, surface="chat", fallback_alt=f"{brand.name} chat media")
    base = _asset_base(model.static_base_url)
    theme = _theme_key(model.theme)
    logout = f'<a href="{escape(model.logout_href)}">Sign out</a>' if model.logout_href else ""
    settings_modal = _chat_settings_modal(model)
    return f"""<!doctype html>
<html lang="en" class="pc-public-root pc-public-theme-{theme}">
{_public_head(title, brand, model.static_base_url)}
<body class="pc-public-page pc-public-chat-page">
  <main class="pc-public-chat-shell" data-pc-chat
      {_attrs(
          data_pc_me_url=model.api_me_url,
          data_pc_history_url=model.api_history_url,
          data_pc_message_url=model.api_message_url,
          data_pc_upload_url=model.api_upload_url,
          data_pc_settings_url=model.api_settings_url,
          data_pc_availability_url=model.api_availability_url,
      )}>
    <aside class="pc-public-chat-presence">
      {media}
      <div class="pc-public-chat-presence-copy">
        {_brand_header(brand, logo_variant="large")}
        <h1>{escape(model.title)}</h1>
        <p>{escape(model.subtitle)}</p>
        <span class="pc-public-presence-pill">{escape(model.initial_presence_label)}</span>
      </div>
    </aside>
    <section class="pc-public-chat-panel" aria-label="Chat">
      <header class="pc-public-chat-header">
        {_brand_header(brand)}
        <nav aria-label="Chat actions">
          <a href="{escape(model.login_href)}">Login</a>
          {logout}
          <button type="button" data-pc-settings-modal-open>Settings</button>
        </nav>
      </header>
      <div class="pc-public-chat-messages" data-pc-chat-messages aria-live="polite">
        <article class="pc-public-chat-message pc-public-chat-message-system">
          <p>{escape(model.subtitle or "Start the conversation when you are ready.")}</p>
        </article>
      </div>
      <form class="pc-public-chat-composer" method="post" action="{escape(model.api_message_url)}"
          data-pc-chat-form data-pc-chat-endpoint="{escape(model.api_message_url, quote=True)}">
        <textarea name="message" rows="2" placeholder="{escape(model.composer_placeholder, quote=True)}" required></textarea>
        <button type="submit">Send</button>
        <output class="pc-public-form-status" data-pc-chat-status></output>
      </form>
      {connectors}
      {legal_links}
    </section>
  </main>
  {settings_modal}
  {modals}
  <script src="{escape(base)}/persona-public.js"></script>
</body>
</html>"""


def _chat_settings_modal(model: ChatPageConfig) -> str:
    themes = _theme_options_html(model.settings_themes, model.theme)
    return (
        '<div class="pc-public-modal pc-public-settings-modal" role="dialog" aria-modal="true" hidden '
        'data-pc-settings-modal>'
        '<div class="pc-public-modal-panel">'
        '<h2>Chat settings</h2>'
        f'{themes}'
        '<button type="button" class="pc-public-modal-close" data-pc-modal-close>Close</button>'
        '</div></div>'
    )


def render_public_settings_surface(
    config: PublicSettingsSurfaceConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, PublicSettingsSurfaceConfig)
    if not public_presence_feature_enabled(model, features):
        return ""
    brand = _brand(model.brand, default_name="Example Persona")
    return f"""
<section id="public-presence" class="pc-public-settings-surface pc-dashboard-panel">
  <div class="pc-dashboard-panel-head">
    <div>
      <div class="pc-dashboard-section-title">{escape(model.title)}</div>
      <div class="pc-dashboard-section-meta">{escape(model.subtitle)}</div>
    </div>
    <button type="button" class="pc-public-settings-open" data-pc-settings-modal-open>Preview settings</button>
  </div>
  <div class="pc-public-settings-grid">
    {_brand_settings_html(model, brand)}
    {_media_settings_html(model)}
    {_connector_settings_html(model)}
    {_social_settings_html(model)}
    {_theme_settings_html(model)}
  </div>
</section>
"""


def _brand_settings_html(model: PublicSettingsSurfaceConfig, brand: BrandAssets) -> str:
    action = model.brand_action or model.settings_action or ""
    logo = render_brand_logo(brand, variant="large", fallback_name=brand.name)
    return (
        f'<form class="pc-public-settings-section" method="post" action="{escape(action)}">'
        '<h3>Branding</h3>'
        f'<div class="pc-public-settings-brand-preview">{logo}<strong>{escape(brand.name)}</strong></div>'
        f'<label><span>Name</span><input name="brand_name" value="{escape(brand.name, quote=True)}"></label>'
        f'<label><span>Small logo URL</span><input name="small_logo_url" value="{escape(brand.small_logo_url, quote=True)}"></label>'
        f'<label><span>Large logo URL</span><input name="large_logo_url" value="{escape(brand.large_logo_url, quote=True)}"></label>'
        f'<label><span>Wordmark URL</span><input name="wordmark_url" value="{escape(brand.wordmark_url, quote=True)}"></label>'
        '<button type="submit">Save branding</button>'
        '</form>'
    )


def _media_settings_html(model: PublicSettingsSurfaceConfig) -> str:
    action = model.media_action or model.settings_action or ""
    rows = [
        ("Splash", _coerce(model.splash_media, PublicMediaConfig)),
        ("Login", _coerce(model.login_media, PublicMediaConfig)),
        ("Chat", _coerce(model.chat_media, PublicMediaConfig)),
    ]
    body = []
    for label, media in rows:
        sources = _media_sources(media)
        first_src = sources[0].src if sources else media.src
        checked = " checked" if media.muted else ""
        body.append(
            '<div class="pc-public-settings-media-row">'
            f'<strong>{escape(label)}</strong>'
            f'<label><span>Kind</span><input name="{escape(label.lower())}_kind" value="{escape(media.kind, quote=True)}"></label>'
            f'<label><span>Source</span><input name="{escape(label.lower())}_src" value="{escape(first_src, quote=True)}"></label>'
            f'<label><span>Poster</span><input name="{escape(label.lower())}_poster" value="{escape(media.poster_url, quote=True)}"></label>'
            f'<label class="pc-public-checkbox"><input type="checkbox" name="{escape(label.lower())}_muted"{checked}>'
            '<span>Muted by default</span></label>'
            '</div>'
        )
    return (
        f'<form class="pc-public-settings-section pc-public-settings-section-wide" method="post" action="{escape(action)}">'
        '<h3>Media</h3>'
        + "".join(body)
        + '<button type="submit">Save media</button></form>'
    )


def _connector_settings_html(model: PublicSettingsSurfaceConfig) -> str:
    action = model.connector_action or model.settings_action or ""
    connectors = render_connector_groups(model.connector_groups, aria_label="Configured connectors")
    if not connectors:
        connectors = '<p class="pc-public-empty">No connectors configured.</p>'
    return (
        f'<form class="pc-public-settings-section pc-public-settings-section-wide" method="post" action="{escape(action)}">'
        '<h3>Connectors</h3>'
        f'{connectors}'
        '<button type="submit">Save connectors</button></form>'
    )


def _social_settings_html(model: PublicSettingsSurfaceConfig) -> str:
    action = model.social_action or model.settings_action or ""
    links = "".join(
        '<div class="pc-public-settings-social-row">'
        f'<input name="social_label" value="{escape(_link(link).label, quote=True)}" aria-label="Social label">'
        f'<input name="social_href" value="{escape(_link(link).href, quote=True)}" aria-label="Social href">'
        '</div>'
        for link in model.social_links
    )
    if not links:
        links = '<p class="pc-public-empty">No public links configured.</p>'
    return (
        f'<form class="pc-public-settings-section" method="post" action="{escape(action)}">'
        '<h3>Social links</h3>'
        f'{links}'
        '<button type="submit">Save links</button></form>'
    )


def _theme_settings_html(model: PublicSettingsSurfaceConfig) -> str:
    action = model.settings_action or ""
    options = _theme_options_html(model.theme_options, "studio")
    return (
        f'<form class="pc-public-settings-section" method="post" action="{escape(action)}">'
        '<h3>Themes</h3>'
        f'{options}'
        '<button type="submit">Save theme</button></form>'
    )
