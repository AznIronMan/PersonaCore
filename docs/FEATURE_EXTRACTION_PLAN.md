# Feature Extraction Plan

PersonaCore should pull shared behavior out of private consoles deliberately.
The public repo should describe the process without naming private consumers or
including private screenshots, paths, or operational details.

## Reference-First Approach

1. Treat the best current private console as the reference implementation for
   initial quality, density, and workflow expectations.
2. Inventory other private consoles for features the reference does not have.
3. Inventory attempted next-generation admin work for useful ideas that did not
   yet land in the main reference console.
4. Convert the union into a public-safe feature backlog with generic names.
5. Extract only the pieces that can be made generic: body styles, cards,
   metrics, tables, review queues, dashboards, activity feeds, message views,
   media/workflow panels, worker health, scheduling, and feature toggles.

## First Shared Modules

Recommended first extraction targets:

- Dashboard attention overview, filter chips, metric/stat cards, route cards,
  queue bars, and activity rows.
- Count/status summary-card builders that turn consumer-owned mappings into
  shared metric cards without moving route or database ownership into
  PersonaCore.
- Runtime health/status summary strip and health detail cards.
- Token/credential health panels for provider tokens and webhook secrets,
  enabled by runtime settings and populated by runtime-owned lookups.
- Adapter/provider health cards with route state, last in/out timestamps,
  queued/failed counts, and optional sparkline buckets.
  - Initial public-safe renderer: PersonaCore `1.0.8`.
- Message flow visualization for inbound/outbound activity.
- Review queue summary cards and decision rows.
- Conversation/message browser surfaces.
  - Initial public-safe message/activity/media surfaces shipped in PersonaCore
    `1.0.9`.
- Command preview/queue panels.
- Media/workflow status panels.
- Worker, scheduling, and availability/live monitor panels.

## Acceptance For Each Extracted Feature

- Generic public naming and fake fixture data.
- Feature flag or capability setting controls visibility.
- No private runtime imports.
- No optional heavy dependency on the core import path.
- Focused tests for rendering, disabled states, and missing data.
- Browser visual fixture when practical.

## Consumer Migration Requirements

Each private consumer migration should be handled in that consumer's repository
and task system. The public PersonaCore repo should only receive generic shared
code and sanitized docs.

For each consumer:

1. Update the consumer's `AGENTS.md` with its PersonaCore update process.
2. Document where the consumer gets PersonaCore from: installed package,
   checked-out tag, mounted source directory, or another versioned mechanism.
3. Document required focused tests, visual/render smoke, and restart/rebuild
   steps.
4. Archive the legacy hardcoded console implementation into the consumer's
   ignored private area before removing it from tracked code.
5. Remove the old tracked console implementation only after the PersonaCore
   implementation passes tests and live/render smoke.

Archives are operational safety nets. They should not be committed to
PersonaCore or to public consumer repos.

## Backlog

See [Reference Console Backlog](REFERENCE_CONSOLE_BACKLOG.md) for the sanitized
module list derived from the private reference console.
