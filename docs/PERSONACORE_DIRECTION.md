# PersonaCore Direction

PersonaCore should become the shared admin distro for persona runtimes. The
central idea is that each runtime should not carry its own copied console.
Instead, PersonaCore provides the common console implementation, and runtime
settings decide which capabilities are visible and active.

## Product Shape

PersonaCore should include reusable pieces for:

- Shell, navigation, responsive layout, theme tokens, and static assets.
- Dashboards, status panels, health summaries, activity feeds, review queues,
  conversation/message browsers, media/workflow surfaces, and operator tools.
- Live refresh, flash messages, user/status pills, badges, filters, tables,
  cards, metrics, and route cards.
- Owner-private visibility helpers that consuming runtimes enforce at their
  route, snapshot, and media-serving boundaries.
- Generic adapters or extension points for runtime-owned data providers.

The public distro should be broad enough that future personas can adopt it
without copying an existing private console. Runtime-specific features can still
exist, but they should attach through generic configuration or extension points
when possible.

## Configuration First

Each runtime should be able to define:

- Brand label, icon path, home path, and theme tokens.
- Navigation groups and route visibility.
- Enabled feature modules and disabled feature modules.
- Capability flags, such as whether a runtime has messages, media, review,
  worker queues, scheduling, or external adapters.
- Status pills, user display data, live-refresh URLs, and refresh cadence.
- Public/static asset paths and optional integration helpers.

The result may look different for each runtime, but differences should usually
come from settings rather than forked shell code.

## What Stays Out

PersonaCore should not contain:

- Private persona names, story/canon, relationships, or character-specific text.
- Production credentials, hostnames, account IDs, local paths, or deployment
  state.
- Runtime database logic that only belongs to one private app.
- Auth decisions or permission policies that only belong to one private app.
- Private owner-account mappings, private scope names, or runtime database
  rules. PersonaCore can expose generic policy helpers, but consumers own the
  private mappings and enforcement points.
- Public docs that describe private infrastructure.

Private consumers should pass sanitized, generic data into PersonaCore or keep
private behavior inside their own repos.

## Migration Direction

1. Keep the existing shell stable.
2. Add a public `personacore` import path while keeping `persona_console` as a
   v1.x compatibility alias.
3. Extract shared dashboard/body styles so existing runtime pages do not rely
   on copied inline CSS.
4. Use the best current private console as the reference for first-class
   shared features, then compare other private consoles and next-generation
   admin experiments to fill the backlog.
5. Introduce feature/module configuration for common admin surfaces.
6. Move repeated body panels and controls into shared render primitives.
7. Add browser visual QA for fixture pages and private consumer smoke tests.
8. Publish only sanitized public source and docs.

As private consumers migrate, their own `AGENTS.md` files should explain how
PersonaCore updates are received, tested, and deployed. Their legacy hardcoded
console implementations should be archived into ignored private folders before
tracked source is removed.

## Public Example Direction

The public example app should be generic and modest: a base runtime with common
stock features enabled, fake data, and generic labels. It should demonstrate
feature toggles and configuration without attempting to replicate private
runtime behavior.
