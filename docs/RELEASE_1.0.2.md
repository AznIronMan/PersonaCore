# PersonaCore 1.0.2

## Summary

`1.0.2` adds configurable token health as a shared PersonaCore feature
primitive.

## Changes

- Added `TokenHealthConfig` and `TokenHealthCheck` settings models.
- Added `build_token_health_report(...)` for redacted configured/missing token
  status from runtime-provided mappings or lookup callables.
- Added `render_token_health_panel(...)` and dashboard integration through
  `DashboardData(token_health=...)`.
- Added public-safe fixture examples and CSS for the token health panel.
- Kept raw credential values outside returned reports and rendered HTML.

## Consumer Notes

Consumers should enable token health only when their own runtime settings
provide the required token names or lookup callback. PersonaCore does not read
private `.env` files, databases, or deployment state directly.
