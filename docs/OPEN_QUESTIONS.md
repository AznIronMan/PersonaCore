# Settled Direction And Open Questions

These decisions set the direction for the first public PersonaConsole baseline.

## Settled Direction

1. Public imports should move toward `personaconsole`. The existing
   `personaconsole` import path should remain as a compatibility alias through
   the v1.x transition so existing private consumers do not need a lockstep
   migration.
2. Public package distribution uses the `personaconsole` project name starting at
   the fresh sanitized `v1.0.1` baseline. The internal `personaconsole`
   package remains available as the v1.x compatibility implementation path.
3. Public GitHub should start from a fresh sanitized v1.0.1 baseline. The
   release note should state that prior private development was sanitized at
   operator direction on 2026-06-23 and that v1.0.1 marks the beginning of the
	   public PersonaConsole history.
4. Configuration should prioritize fastest and broadest runtime compatibility:
   typed Python dataclasses and plain dictionaries first, optional JSON loading
   through the standard library, and no mandatory YAML or heavy validation
   dependency in the core path.
5. Feature extraction should start from the best current private console as the
   reference implementation, then compare other private consoles and attempted
   next-generation admin work to build the shared feature backlog.
6. The public example should be a generic base runtime with a normal stock set
   of features enabled. All shared features should be toggleable in settings or
   config, but the example should not attempt to expose private or exhaustive
   real-world behavior.

## Remaining Questions

1. What exact compatibility timeline should `personaconsole` have after the
   `personaconsole` import path exists?
2. How much release automation should be added after the first allowlisted
   export script: GitHub Actions, package build checks, or manual release notes?
