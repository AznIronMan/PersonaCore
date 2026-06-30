"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.public_presence import (
    PUBLIC_PRESENCE_FEATURE,
    PUBLIC_THEME_KEYS,
    public_presence_feature_enabled,
    public_theme_options,
    render_brand_logo,
    render_chat_page,
    render_connector_groups,
    render_login_page,
    render_public_media,
    render_public_settings_surface,
    render_public_splash_page,
)

__all__ = [
    "PUBLIC_PRESENCE_FEATURE",
    "PUBLIC_THEME_KEYS",
    "public_presence_feature_enabled",
    "public_theme_options",
    "render_brand_logo",
    "render_chat_page",
    "render_connector_groups",
    "render_login_page",
    "render_public_media",
    "render_public_settings_surface",
    "render_public_splash_page",
]
