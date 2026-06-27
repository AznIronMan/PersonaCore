# Reference Console Backlog

PersonaCore should use the best current private admin console as the design and
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
  fuller generic fixture target shipped in PersonaCore `1.0.10`; the typed
  people surface shipped in PersonaCore `1.0.11`.

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
   PersonaCore `1.0.8`.
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
  PersonaCore `1.0.16`; lifecycle semantics remain runtime-owned.
- Page refresh and live-refresh controls as configurable shell primitives.
  PersonaCore `1.0.16` adds `pc-*` class hooks to the existing live-refresh
  shell controls.
- Account menu extension point.
- Runtime lifecycle control slot for private/local deployments.

## Workflow Modules

- Message browser with conversation list, selected thread, platform badges,
  transcript bubbles, attachments, reactions, and audit-link slots.
  Initial public-safe list, transcript, attachment, activity, and media card
  primitives shipped in PersonaCore `1.0.9`.
- Conversation transcript table for forensic/admin views.
- Review queue cards and tables with summary metrics, tags, decision actions,
  and pending-change integration hooks.
- Plain-language command preview panel with parsed result, risk tags,
  candidates, confirmation states, queue button, and history list.
- Health detail grid for host, network, provider, and model checks.
- Availability/live monitor panels for schedules, workers, queue state, safety
  policy, and scenario/status QA.
- Media/artifact cards for generated or uploaded assets with preview,
  classification, sendable status, and action slots.
- Generic task, log, and settings posture panels for reference-console parity.
  Initial public-safe fixture examples shipped in PersonaCore `1.0.10`; typed
  renderers should be extracted only when repeated consumer usage proves the
  shape is stable.
- People list surface with filter bar, tags, relationship summary, notes
  preview, new-person slot, and owner-private note fallback. Initial typed
  renderer shipped in PersonaCore `1.0.11`.

## Implementation Rules

- Keep PersonaCore inputs generic: dataclasses plus plain dictionaries.
- Treat renderer output as public-safe HTML from escaped data; body HTML remains
  trusted only when explicitly passed by the consumer.
- Do not import runtime databases, auth, private routes, secrets, or deployment
  state.
- Keep optional framework dependencies lazy.
- Add tests for enabled, disabled, empty, missing-data, escaping, and tone
  fallback states.
- Add fixture pages before relying on browser visual QA.
