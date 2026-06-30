"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.surfaces import (
    ACTIVITY_FEATURE,
    MEDIA_FEATURE,
    MESSAGES_FEATURE,
    activity_surface_feature_enabled,
    media_surface_feature_enabled,
    message_surface_feature_enabled,
    render_activity_surface,
    render_media_surface,
    render_message_surface,
    render_surface_sections,
)

__all__ = [
    "ACTIVITY_FEATURE",
    "MEDIA_FEATURE",
    "MESSAGES_FEATURE",
    "activity_surface_feature_enabled",
    "media_surface_feature_enabled",
    "message_surface_feature_enabled",
    "render_activity_surface",
    "render_media_surface",
    "render_message_surface",
    "render_surface_sections",
]
