# Consumer Release Propagation

PersonaConsole releases can affect multiple consumer runtimes. Keep the public
package generic, then propagate each approved update through the consumer repos
that opted into that release.

## Public/Private Boundary

Tracked PersonaConsole files may describe the workflow and generic roster
schema. They must not contain private consumer names, hosts, local paths,
restart commands, smoke URLs, screenshots, credentials, or deployment notes.

Keep the real roster in `.private/consumer-release-roster.json` or in each
consumer repo's own private runbook. `.private/` is ignored.

## Release Checklist

For each consumer:

1. Read that consumer repo's `AGENTS.md`.
2. Open or continue the consumer-owned task before code, deploy, or runtime
   state changes.
3. Update the PersonaConsole package version, source checkout, or approved
   local source mount.
4. Refresh vendored static assets if that runtime serves copied assets.
5. Run PersonaConsole package tests for the shared checkout when the release
   changes shared renderers.
6. Run the consumer's focused admin/render tests.
7. Run `scripts/consumer_integration_doctor.py --expected-version <version>`
   where the consumer can import the updated package.
8. Smoke admin login plus representative migrated routes.
9. Restart or rebuild only the services that import PersonaConsole.
10. Record verification, restart result, rollback posture, and watch items in
    the consumer task system.

## Local Roster

Create an ignored local roster:

```bash
python3 scripts/consumer_release_plan.py --print-template > .private/consumer-release-roster.json
```

Edit that private file for real consumers. Keep any private details out of
tracked docs and commits.

Generate a checklist to stdout:

```bash
python3 scripts/consumer_release_plan.py \
  --roster .private/consumer-release-roster.json \
  --version 1.0.41 \
  --source "public tag v1.0.41"
```

Write a generated plan only under `.private/`:

```bash
python3 scripts/consumer_release_plan.py \
  --roster .private/consumer-release-roster.json \
  --version 1.0.41 \
  --output .private/release-plans/personaconsole-1.0.41.md
```

The helper refuses output paths outside `.private/` so private runtime names are
not accidentally written into tracked files.

## Roster Fields

- `key`: stable local identifier.
- `label`: display label for the generated private checklist.
- `repo_path`: private consumer repo/root path.
- `task_system`: reminder for the consumer's task tracker.
- `persona_console_source`: how this consumer receives PersonaConsole.
- `update_steps`: package/source/static update actions.
- `tests`: required focused tests or doctor checks.
- `smokes`: browser, route, or render smokes.
- `restart_steps`: restart, rebuild, or container rollout actions.
- `rollback`: exact rollback posture for that consumer.
- `notes`: private reminders or watch items.
