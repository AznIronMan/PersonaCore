# Reference Admin Parity Spec

PersonaCore consumers should be able to feel like one admin family while still
owning their private auth, routes, data, deployment, and business logic. This
spec defines the shared public target for that consistency.

The reference is not a copied private console. It is a reusable composition
model: one shell, dense operational navigation, first-screen status, feature
modules, and shared privacy behavior that each runtime enables and labels
through configuration.

## Goals

- Make consumer admins feel familiar across runtimes.
- Keep feature availability driven by `PersonaCoreConfig.features`,
  navigation groups, badges, status pills, theme tokens, and consumer-owned
  body data.
- Keep raw private data, credentials, database access, deployment state, and
  mutation policy out of PersonaCore.
- Preserve server-side privacy enforcement. UI hiding is only presentation.

## Shell Contract

Each consumer should map its admin shell into the same core regions:

- Fixed top bar with brand label, grouped navigation, status pills, and user
  pill.
- Mobile navigation that exposes the same grouped route structure as desktop.
- Page head with title, subtitle, refresh control, and optional live-refresh
  interval.
- Body composed from shared dashboard, surface, and panel primitives where
  possible.
- Footer or low-priority status region only for runtime-safe information.

Consumers may change labels, route paths, badges, active state, theme tokens,
and available groups. They should not fork shell markup unless the behavior is
truly runtime-specific.

## First Viewport Contract

The first viewport should answer:

- What needs operator attention?
- Are the core services healthy?
- Which routes have active work?
- Which conversations, people, tasks, workers, media, logs, or settings need a
  quick glance?

Use the shared dashboard primitives for:

- Attention overview and attention cards.
- Filter chips.
- Metric cards.
- Route cards.
- Runtime health strip.
- Token/credential health.
- Adapter/provider health.
- Flow visualization.
- Queue rows.
- Activity rows.

This keeps consumer dashboards dense and scan-friendly without duplicating the
HTML/CSS shape per runtime.

## Navigation Contract

Use grouped navigation with the same default mental model:

- `Overview`: overview and activity.
- `Conversations`: messages, people, and media/artifacts.
- `Operations`: review queue, tasks, workers, and runtime work queues.
- `System`: logs, settings, health, and configuration surfaces.

Runtime-specific labels are fine. Missing capabilities should be disabled or
hidden with feature flags instead of leaving dead links.

## Module Surface Contract

PersonaCore should supply reusable primitives for common module surfaces:

- `messages`: platform/filter chips, selected-thread metrics, action links,
  conversation list, selected thread, transcript bubbles, attachments, badges,
  and redacted owner-private fallbacks. PersonaCore `1.0.12` supplies the
  typed browser controls and two-column message surface; consumers still own
  lookups, auth, pagination, and private scope mapping.
- `activity`: public/group/social activity rows and timeline events.
- `media`: artifact cards, preview placeholders, status labels, and redacted
  owner-private fallbacks.
- `people`: profile and relationship summaries rendered from consumer-owned
  data. PersonaCore `1.0.11` supplies the typed filter/table/notes surface;
  consumers still own lookups, auth, edits, and private scope mapping.
- `review`: queue metrics, pending rows, decision context, and action slots.
  PersonaCore `1.0.14` supplies the typed review-board, agenda, and queue-card
  primitives. PersonaCore `1.0.15` supplies the shared status-tab control for
  filtered queue/list pages; consumers still own queries, auth, mutations, and
  private scope mapping.
- `flash`: transient success/warning/error banners and optional action links.
  PersonaCore `1.0.16` supplies shared flash/action banner markup plus redirect
  query helpers; consumers still own POST handlers, permissions, and target
  routes.
- `tasks`: task status tables and operator next actions.
- `workers`: queue latency, retry state, and adapter/runtime cards.
- `logs`: sanitized runtime events and warning summaries.
- `settings`: feature flags, integration posture, and safe configuration
  status.
- `health`: service, credential, adapter, and runtime checks.

If a module is not yet a typed PersonaCore renderer, consumers can still match
the shared shell by composing generic panels, cards, tables, tags, and status
pills while the reusable primitive is extracted.

## Privacy Contract

Owner-private protection is always server-enforced by the consuming runtime.
The PersonaCore UI helpers can render safe alternates or withheld placeholders,
but they do not replace route authorization.

Required behavior:

- The linked owner context can see raw owner-private content for its own scope.
- Operators and moderators can administer normal runtime state but cannot see
  raw owner-private DMs, DM media, private notes, private thoughts, private
  journals, or private artifacts.
- Admin/system tier does not override owner privacy unless it is also the
  linked owner context.
- Public posts, group messages, chatroom messages, comments, likes, and public
  engagement remain visible according to normal public/group/operator policy.
- HTML pages, JSON routes, query/snapshot builders, and artifact/media byte
  routes must call the same runtime policy before returning raw owner-private
  data.

The `owner_private_admin` feature flag only controls whether owner-private admin
panels appear. It never disables raw content protection.

## Consumer Mapping

For each consuming runtime:

1. Read that runtime's local instructions and open its required task.
2. Identify which shared feature modules are available.
3. Map local routes into the grouped navigation model.
4. Pass runtime-safe counts, labels, hrefs, tones, and summaries into shared
   render primitives.
5. Keep auth, database queries, mutation routes, restart controls, secrets,
   and private deployment state in the consumer repo.
6. Run the PersonaCore doctor, the runtime's focused admin tests, and a render
   or login smoke before release.

## Acceptance Checklist

- Desktop and mobile shells use the shared top bar, grouped navigation, user
  pill, status pills, and live-refresh controls.
- First viewport includes attention, metrics, route cards, health, and at
  least one activity or workflow summary.
- Conversations, people, tasks, workers, logs, settings, media, and health are
  either implemented, intentionally hidden by feature flags, or represented by
  safe placeholders.
- Raw owner-private content is blocked for non-owner contexts in HTML, JSON,
  snapshot/query builders, and byte-serving routes.
- Public/group/social engagement remains visible under normal policy.
- Consumer-specific route names, private scope aliases, hosts, paths,
  usernames, credentials, screenshots, and deployment state are not committed
  to PersonaCore.

## Fixture Target

`examples/fixture_app.py` is the public-safe reference fixture. It demonstrates
the shared composition target with generic labels and fake data:

- Overview, conversations, operations, and system navigation groups.
- Attention, metrics, routes, health, token health, adapter health, flow,
  queue, and activity sections.
- Message, activity, and media surfaces with owner-private safe alternates.
- People surface with tags, relationship summary, and owner-private note
  fallback.
- Generic task, log, and settings posture panels.

Use the fixture for visual QA and consumer alignment discussions. It should
remain sanitized and must not include private runtime names, hosts, paths,
screenshots, account identifiers, or secrets.
