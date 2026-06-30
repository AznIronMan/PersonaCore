# PersonaConsole 1.0.5

`1.0.5` adds public-safe owner-private admin visibility primitives for
consuming runtimes.

## Changes

- Added `OwnerPrivateScopePolicy`, `AdminPrivacyContext`, `PrivacyRenderMode`,
  and helper functions for canonical privacy scopes, raw owner-private access
  checks, safe alternate rendering, and direct-message owner-private
  classification.
- Added `NavItem.feature` and feature-aware navigation rendering so runtimes can
  hide opt-in modules such as `owner_private_admin`.
- Re-exported the privacy helpers through both `personaconsole` and
  `personaconsole` import paths.
- Added unit coverage for owner-only raw visibility, admin non-override
  behavior, safe alternate rendering, withheld placeholders, direct-message
  classification, and feature-gated navigation.

## Consumer Notes

PersonaConsole does not know private users, hosts, databases, or account mappings.
Consumers must supply their own private scope policy and enforce it in every
server-side HTML, JSON, query/snapshot, and media route that can expose raw
owner-private content.
