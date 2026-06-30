# Public Release And Sanitization

Public upstream:

```text
https://github.com/AznIronMan/PersonaConsole.git
```

PersonaConsole is intended to be public. Public release must be treated as a
sanitization boundary, not as a raw mirror of a local working folder.

## Do Not Publish

Do not commit or push:

- Private project names, character names, hostnames, usernames, account IDs, or
  local filesystem paths.
- `.env`, `.private/`, browser profiles, generated media, runtime databases,
  deployment scripts with private state, or private task notes.
- Screenshots or logs from private runtime consoles.
- Private consumer task files or operational handoff details.

## Publishable Content

Public-safe content includes:

- Generic source code for the reusable shell and shared feature modules.
- Generic tests and fixtures.
- Generic examples using placeholder names.
- Public docs that explain architecture, configuration, extension points, and
  sanitized release workflows.

## History Warning

The existing local git history may contain private names and paths from local
handoff work. Do not push that history directly to the public repository.

Safe options:

- Create a fresh public repository state from the sanitized working tree.
- Or perform an intentional history rewrite, audit every commit, and only then
  push.

The preferred path for the first public release is a fresh sanitized v1.0.1
baseline. Its release note should say that prior private development was
sanitized at operator direction on 2026-06-23 and that v1.0.1 marks the start
of public PersonaConsole history.

## Fresh Baseline Export

Use the allowlisted export script from this private/local working tree:

```bash
scripts/export_public_baseline.sh /tmp/personaconsole-public-baseline
```

The script copies only public distribution paths:

- `.gitignore`
- `README.md`
- `pyproject.toml`
- `docs/`
- `examples/`
- `scripts/`
- `src/`
- `tests/`

It rejects local/private path entries such as `AGENTS.md`, `.private/`,
`.tasks/`, `.env*`, sync metadata, caches, and runtime databases. It also runs
a generic content scan for local absolute paths and common secret markers.

After export, review the generated tree manually, then create fresh public
history from that export directory:

```bash
cd /tmp/personaconsole-public-baseline
git init
git add .
git commit -m "Start sanitized PersonaConsole public baseline"
git tag v1.0.3  # use the version printed by the export script
git remote add origin https://github.com/AznIronMan/PersonaConsole.git
```

Push only after reviewing the export and confirming the release checklist.

## Deployment Model

PersonaConsole should be released through versioned Git or package installs, not
raw workstation synchronization.

Recommended host pattern:

- Keep a local checkout of the public PersonaConsole repository on each server or
  build host.
- Pull an explicit tag or commit, such as `v1.0.3`.
- Install the package into the runtime environment, or mount/import its `src`
  directory read-only where containerized consumers already use that pattern.
- Rebuild or restart consumer services according to the owning runtime's
  deployment rules.

Syncthing can still be useful for private runtime source trees that already
depend on it, but it should not be the release mechanism for the public shared
PersonaConsole distro.

## Suggested Release Checklist

1. Confirm `git status` is clean except intended sanitized changes.
2. Run `rg` for private names, paths, hostnames, usernames, IDs, and secret
   patterns.
3. Confirm `.private/`, `.tasks/`, `.env*`, caches, browser profiles, generated
   outputs, runtime databases, and `AGENTS.md` are ignored or absent from the
   exported tree.
4. Run package tests and compile checks.
5. Run `scripts/export_public_baseline.sh` into an empty directory.
6. Manually review the exported tree.
7. Create fresh public history from the export directory.
8. Tag the release, starting with `v1.0.1` for the first public baseline.
9. Publish from sanitized history only.
