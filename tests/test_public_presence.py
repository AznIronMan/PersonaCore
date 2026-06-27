import personacore


PRIVATE_HOSTS = ("private-login.example", "private-chat.example", "private-home.example")


def _brand() -> personacore.BrandAssets:
    return personacore.BrandAssets(
        name="Example <Persona>",
        small_logo_url="/assets/small.svg",
        large_logo_url="/assets/large.svg",
        wordmark_url="/assets/wordmark.svg",
        signature_text="public shell",
        home_url="/",
    )


def _connectors():
    return (
        personacore.ConnectorGroup(
            "Connect",
            connectors=(
                personacore.ConnectorOption(
                    "web_chat",
                    "Web Chat",
                    href="/login/web-chat",
                    icon="chat",
                    status="Ready",
                    tone="good",
                    description="<strong>escaped</strong>",
                    configured=True,
                    selected=True,
                ),
                personacore.ConnectorOption(
                    "social",
                    "Social",
                    action="connect",
                    icon="share",
                    status="Needs setup",
                    tone="warn",
                    configured=False,
                ),
            ),
        ),
    )


def test_public_splash_renders_brand_media_links_and_muted_controls():
    html = personacore.render_public_splash_page(
        personacore.PublicSplashPageConfig(
            brand=_brand(),
            title="Example <Persona>",
            subtitle="Public home",
            description="Generic homepage",
            media=personacore.PublicMediaConfig(
                kind="video",
                sources=(personacore.PublicMediaSource("/media/hero.mp4", "video/mp4"),),
                poster_url="/media/poster.jpg",
                audio_src="/media/hero.mp3",
            ),
            chat_label="Chat now",
            chat_href="/chat",
            social_links=(personacore.PublicLink("Updates", "/updates", external=False),),
            update_form_action="/updates",
            legal_notices=(personacore.LegalNotice("terms", "Terms", body="Generic legal copy."),),
        )
    )

    assert "pc-public-splash" in html
    assert "persona-public.css" in html
    assert "persona-public.js" in html
    assert "/assets/large.svg" in html
    assert "/media/hero.mp4" in html
    assert "/media/hero.mp3" in html
    assert " muted" in html
    assert "pc-public-sound-toggle" in html
    assert "Chat now" in html
    assert "data-pc-signup-form" in html
    assert "&lt;Persona&gt;" in html
    assert "Example <Persona>" not in html
    assert not any(host in html for host in PRIVATE_HOSTS)


def test_login_renders_connector_status_and_escaped_generic_data():
    html = personacore.render_login_page(
        personacore.LoginPageConfig(
            brand=_brand(),
            title="Sign in",
            subtitle="Choose a provider",
            connector_groups=_connectors(),
            email_action="/login/email",
            phone_action="/login/phone",
            phone_enabled=True,
            status_message="<b>Pick one</b>",
        )
    )

    assert "pc-public-login-page" in html
    assert "pc-connector-option" in html
    assert 'data-connector-key="web-chat"' in html
    assert 'data-connector-configured="false"' in html
    assert 'data-connector-action="connect"' in html
    assert "Needs setup" in html
    assert "&lt;strong&gt;escaped&lt;/strong&gt;" in html
    assert "&lt;b&gt;Pick one&lt;/b&gt;" in html
    assert "<strong>escaped</strong>" not in html
    assert not any(host in html for host in PRIVATE_HOSTS)


def test_chat_page_renders_api_hooks_settings_modal_and_composer():
    html = personacore.render_chat_page(
        personacore.ChatPageConfig(
            brand=_brand(),
            title="Chat",
            subtitle="Runtime-owned chat processing",
            media=personacore.PublicMediaConfig(kind="image", src="/media/chat.jpg"),
            connector_groups=_connectors(),
            settings_themes=personacore.public_theme_options("matrix"),
        )
    )

    assert "pc-public-chat-shell" in html
    assert "data-pc-message-url" in html
    assert "/api/chat/message" in html
    assert "data-pc-chat-form" in html
    assert "pc-public-settings-modal" in html
    assert "pc-public-theme-choice-matrix" in html
    assert "Runtime-owned chat processing" in html
    assert not any(host in html for host in PRIVATE_HOSTS)


def test_public_settings_surface_is_feature_gated_and_renders_forms():
    config = personacore.PublicSettingsSurfaceConfig(
        enabled=True,
        brand=_brand(),
        splash_media=personacore.PublicMediaConfig(kind="video", src="/media/splash.mp4"),
        login_media=personacore.PublicMediaConfig(kind="image", src="/media/login.jpg"),
        chat_media=personacore.PublicMediaConfig(kind="image", src="/media/chat.jpg"),
        connector_groups=_connectors(),
        social_links=(personacore.PublicLink("Updates", "/updates", external=False),),
        theme_options=personacore.public_theme_options("studio"),
        settings_action="/settings/public-presence",
    )

    disabled = personacore.render_public_settings_surface(config, features={personacore.PUBLIC_PRESENCE_FEATURE: False})
    html = personacore.render_public_settings_surface(config, features={personacore.PUBLIC_PRESENCE_FEATURE: True})

    assert disabled == ""
    assert "pc-public-settings-surface" in html
    assert "Small logo URL" in html
    assert "Muted by default" in html
    assert "Save connectors" in html
    assert "pc-public-theme-choice-studio" in html
    assert "/settings/public-presence" in html
    assert not any(host in html for host in PRIVATE_HOSTS)


def test_public_css_keeps_connector_buttons_and_fallback_logos_stable():
    css = (
        __import__("pathlib")
        .Path("src/persona_console/static/persona-public.css")
        .read_text(encoding="utf-8")
    )

    assert ".pc-public-brand-logo-fallback.pc-public-brand-logo-large" in css
    assert ".pc-public-page .pc-connector-option" in css
    assert "cursor: default" in css
    assert ".pc-public-page .pc-connector-option[data-connector-action]" in css


def test_admin_shell_uses_brand_assets_without_breaking_icon_fallback():
    html = personacore.render_shell_html(
        personacore.PersonaCoreConfig(
            brand_name="Example Runtime",
            page_title="Dashboard",
            brand_assets=_brand(),
            nav_groups=[personacore.NavGroup("Core", [personacore.NavItem("Home", "/")])],
        ),
        "<section>body</section>",
    )

    assert "admin-brand-wordmark" in html
    assert "/assets/wordmark.svg" in html
    assert "Example &lt;Persona&gt;" in html
    assert "body" in html
