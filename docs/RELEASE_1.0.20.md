# Release 1.0.20

`1.0.20` polishes public presence visual defaults and clarifies split
deployment support.

## Changes

- Fixed public connector options rendered as `<button>` elements so they keep
  connector-card styling instead of inheriting primary action button styling.
- Fixed fallback large-logo and wordmark rendering so text fallback logos keep
  stable square dimensions instead of collapsing into narrow vertical pills.
- Clarified that public presence surfaces are deployment-agnostic: consumers can
  export a splash/home page to a static host or CDN while serving login and chat
  from separate runtime-owned app servers.
- Added regression coverage for connector button styling hooks and large-logo
  fallback CSS hooks.

## Consumer Boundary

PersonaConsole still owns only public-safe render models, escaped markup, and
shared CSS/JS. Consumers own hosting topology, auth, cookies, OAuth callbacks,
provider secrets, chat processing, settings persistence, uploads, and
deployment.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.20
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.20.html
PYTHONPATH=src python3 -m compileall src
```
