# Reference Console Backlog

PersonaConsole should use the best current private admin console as the design and
workflow reference, but public source and docs must stay generic. This backlog
names reusable admin patterns only; private names, paths, routes, hosts,
screenshots, data, and runtime policy stay outside the public repo.

## Design Priorities

- Build dense operational workflows, not landing pages.
- Put the most important runtime attention state first.
- Use compact panels, tables, tags, route cards, filter chips, status pills,
  and live-refresh controls.
- Keep actions close to the data they affect while leaving mutation endpoints
  runtime-owned unless the behavior is truly generic.
- Make every shared surface configurable by feature flags, capability flags,
  labels, hrefs, badges, tones, and optional data providers.
- Keep the public fixture aligned with the shared composition target in
  [Reference Admin Parity Spec](REFERENCE_ADMIN_PARITY_SPEC.md). The first
  fuller generic fixture target shipped in PersonaConsole `1.0.10`; the typed
  people surface shipped in PersonaConsole `1.0.11`; operations, persona-runtime,
  continuity, bridge, and agent-ops surfaces shipped in PersonaConsole `1.0.17`;
  the themed journal reader shipped in PersonaConsole `1.0.18`; public presence
  splash/login/chat and connector settings surfaces shipped in PersonaConsole
  `1.0.19`; the read-only terminal stream window shipped in PersonaConsole
  `1.0.22`; the grouped settings editor surface shipped in PersonaConsole
  `1.0.23`; the system health/database/audit posture surface shipped in
  PersonaConsole `1.0.24`; the persona editor primitives shipped in
  PersonaConsole `1.0.25`; bridge operation panels shipped in PersonaConsole
  `1.0.26`; the command intake preview surface shipped in PersonaConsole
  `1.0.27`; the availability/live monitor surface shipped in PersonaConsole
  `1.0.28`; the generic admin-list/table surface shipped in PersonaConsole
  `1.0.29`; the detail/dossier surface shipped in PersonaConsole `1.0.30`;
  the richer media/artifact library surface shipped in PersonaConsole `1.0.31`;
  the worker/process operations surface shipped in PersonaConsole `1.0.32`.

## First Dashboard Modules

1. Attention overview:
   status label, tone, count, optional refreshed-at copy, alert cards, and
   clear state.
2. Route filters:
   chip list for platform/provider/runtime filters, active state, hrefs, and
   optional swatches.
3. Metric cards:
   compact linked counts with labels, values, tones, and optional detail text.
4. Health strip:
   linked runtime health row with metric chips and degraded/missing data states.
5. Token health:
   redacted configured/missing status for provider tokens, webhook secrets, and
   other runtime-owned credentials with required/optional severity.
6. Adapter health cards:
   provider route, last in/out timestamps, queued/failed counts, policy detail,
   sparkline buckets, and action hints. Initial shared renderer shipped in
   PersonaConsole `1.0.8`.
7. Flow chart:
   lightweight bar visualization for inbound/outbound activity with optional
   provider segments.
8. Queue summary:
   status rows with counts and proportional bars.
9. Activity timeline:
   compact linked rows with label, title, timestamp, summary, metadata, and
   tone dot.

## Shell Modules

- Footer status region with live refresh.
- Restart/update banner slot. Flash/action banner primitives shipped in
  PersonaConsole `1.0.16`; lifecycle semantics remain runtime-owned.
- Page refresh and live-refresh controls as configurable shell primitives.
  PersonaConsole `1.0.16` adds `pc-*` class hooks to the existing live-refresh
  shell controls.
- Account menu extension point.
- Runtime lifecycle control slot for private/local deployments.

## Workflow Modules

- Message browser with conversation list, selected thread, platform badges,
  transcript bubbles, attachments, reactions, and audit-link slots.
  Initial public-safe list, transcript, attachment, activity, and media card
  primitives shipped in PersonaConsole `1.0.9`.
- Conversation transcript table for forensic/admin views.
- Review queue cards and tables with summary metrics, tags, decision actions,
  and pending-change integration hooks.
- Generic admin list/table surface with status tabs, filter form fields,
  metric cards, sortable column links, row actions, pagination, mobile cards,
  and owner-private cell fallbacks. Initial typed renderer shipped in
  PersonaConsole `1.0.29`.
- Generic detail/dossier surface for entity overviews, metadata fields,
  summary metrics, narrative sections, source tables, related links, timelines,
  audit rows, and runtime-owned action slots. Initial typed renderer shipped in
  PersonaConsole `1.0.30`.
- Plain-language command preview panel with parsed result, risk tags,
  candidates, confirmation states, queue button, and history list. Initial
  typed renderer shipped in PersonaConsole `1.0.27`.
- Health detail grid for host, network, provider, and model checks.
- Availability/live monitor panels for schedules, workers, queue state, safety
  policy, and scenario/status QA. Initial typed renderer shipped in
  PersonaConsole `1.0.28`.
- Media/artifact cards for generated or uploaded assets with preview,
  classification, sendable status, and action slots. Initial card primitives
  shipped in PersonaConsole `1.0.9`; the richer grid/list library with preview
  dialogs, metadata chips, safety/sendability flags, non-image fallbacks, and
  import/upload action slots shipped in PersonaConsole `1.0.31`.
- Generic task, log, and settings posture panels for reference-console parity.
  Initial public-safe fixture examples shipped in PersonaConsole `1.0.10`; typed
  operations/settings/log renderers shipped in PersonaConsole `1.0.17`.
- Worker/process operations surface for readiness, schedules, run telemetry,
  dead letters, rollback candidates, dry-run candidates, process feed events,
  and review-first action slots. Initial typed renderer shipped in
  PersonaConsole `1.0.32`; consumers still own execution, service managers,
  queue/dead-letter mutations, rollback proposals, database writes, auth, and
  deployment behavior.
- Grouped settings editor with redacted values, validation summaries,
  pending-change preview, restart markers, and runtime-owned action slots.
  Initial typed renderer shipped in PersonaConsole `1.0.23`.
- System health/database/audit surface with runtime check groups, database
  cards, table summaries, secret coverage, readiness probes, and owner-private
  audit rows. Initial typed renderer shipped in PersonaConsole `1.0.24`.
- Persona runtime, continuity, bridge, and agent-session posture panels.
  Initial typed public-safe renderers shipped in PersonaConsole `1.0.17`.
- Persona profile, trait, rule, mutable-state, proposal, and change-history
  editor primitives. Initial typed renderer shipped in PersonaConsole `1.0.25`.
- Read-only terminal/event stream window for agent sessions with a bounded
  current slice, chunked earlier-history hooks, live polling hooks, and no
  command execution. Initial typed renderer shipped in PersonaConsole `1.0.22`.
- People list surface with filter bar, tags, relationship summary, notes
  preview, new-person slot, and owner-private note fallback. Initial typed
  renderer shipped in PersonaConsole `1.0.11`.
- Journal reader surface with calendar rail, default paper page, selectable
  white-paper/script/typewriter/terminal/archive themes, provenance details,
  page turns, and owner-private entry fallback. Initial typed renderer shipped
  in PersonaConsole `1.0.18`.
- Public presence surfaces for public splash/homepage, media hero, login,
  chat, connector choices, social links, legal modals, and admin settings.
  Initial typed renderers and static assets shipped in PersonaConsole `1.0.19`;
  provider truth, auth, callbacks, chat processing, settings persistence, and
  deployment wiring remain outside PersonaConsole.
- Bridge/provider operation panels for webhook posture, queues, heartbeats,
  provider capability rows, delivery claims, documentation links, and action
  slots. Initial typed renderer shipped in PersonaConsole `1.0.26`.
- Command intake preview panel with parsed fields, candidate targets, risk
  checks, confirmation steps, queue posture, and sanitized history. Initial
  typed renderer shipped in PersonaConsole `1.0.27`.

## Implementation Rules

- Keep PersonaConsole inputs generic: dataclasses plus plain dictionaries.
- Treat renderer output as public-safe HTML from escaped data; body HTML remains
  trusted only when explicitly passed by the consumer.
- Do not import runtime databases, auth, private routes, secrets, or deployment
  state.
- Keep optional framework dependencies lazy.
- Add tests for enabled, disabled, empty, missing-data, escaping, and tone
  fallback states.
- Add fixture pages before relying on browser visual QA.
