"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.adapter_health import (
    ADAPTER_HEALTH_FEATURE,
    adapter_health_feature_enabled,
    render_adapter_health_panel,
)

__all__ = [
    "ADAPTER_HEALTH_FEATURE",
    "adapter_health_feature_enabled",
    "render_adapter_health_panel",
]
