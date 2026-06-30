"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.token_health import (
    TOKEN_HEALTH_FEATURE,
    build_token_health_report,
    render_token_health_panel,
    token_health_checks_for_providers,
    token_health_config_for_providers,
    token_health_feature_enabled,
    token_health_lookup,
    token_health_provider_keys,
)

__all__ = [
    "TOKEN_HEALTH_FEATURE",
    "build_token_health_report",
    "render_token_health_panel",
    "token_health_checks_for_providers",
    "token_health_config_for_providers",
    "token_health_feature_enabled",
    "token_health_lookup",
    "token_health_provider_keys",
]
