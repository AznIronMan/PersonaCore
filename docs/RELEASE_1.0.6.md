# Release 1.0.6

`1.0.6` extends the public-safe token health primitive with a shared feature
flag and common provider presets.

## Changes

- Added `TOKEN_HEALTH_FEATURE` for runtimes that gate modules through
  `features["token_health"]`.
- Added `token_health_config_for_providers(...)`,
  `token_health_checks_for_providers(...)`, `token_health_provider_keys()`, and
  `token_health_feature_enabled(...)`.
- Added sanitized provider presets for Meta, Instagram, X, Discord, and webhook
  token checks, with runtime-owned overrides for private credential names or
  required/optional policy.
- Let dashboard rendering hide token health when the dashboard data feature map
  explicitly disables the module.
- Kept report generation redacted: raw values supplied through mappings or
  lookup callables are never copied into returned reports or rendered HTML.

## Consumer Notes

Consumers can continue defining explicit `TokenHealthCheck` entries. Presets are
only a convenience for common provider labels and source-name defaults.
Runtime-specific credential names, validation calls, token refresh state,
admin routes, and secrets remain owned by the consuming runtime.
