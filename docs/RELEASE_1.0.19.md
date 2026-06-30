# Release 1.0.19

`1.0.19` adds reusable public presence surfaces for persona runtimes.

## Changes

- Added public-safe dataclasses for brand assets, public media sources, public
  media config, social links, legal notices, public theme options, connector
  options, connector groups, splash page config, login page config, chat page
  config, and the admin public settings surface.
- Added full-page renderers:
  `render_public_splash_page(...)`, `render_login_page(...)`, and
  `render_chat_page(...)`.
- Added `render_public_settings_surface(...)` for the authenticated admin
  settings page that controls logos, splash/login/chat media, connector display
  state, social links, and public themes.
- Added `persona-public.css` and `persona-public.js` for public page layout,
  slideshows, video/audio sound controls, legal/settings modals, signup hooks,
  chat hooks, and no-JS-safe form fallbacks.
- Added optional `brand_assets` support to `PersonaConsoleConfig` so the admin
  shell can use small logos, large logos, and wordmarks while preserving the
  existing `icon_url` fallback.
- Added `personaconsole.public_presence` as a public re-export module.
- Updated the fixture app with generic public splash, login, chat, and public
  settings routes.
- Updated the consumer integration doctor to verify public presence exports,
  escaped generic data, connector status rendering, muted media controls, and
  absence of private default hosts.

## Consumer Boundary

PersonaConsole owns rendering and public-safe configuration models only. Consumer
runtimes own auth, cookies, login codes, OAuth callbacks, provider secrets,
chat processing, uploads, settings persistence, legal copy, and deployment
wiring.

PersonaEngine can later provide provider-neutral connector/capability metadata
that consumers pass into PersonaConsole. PersonaConsole should not call providers,
store secrets, decide connector truth, or implement private runtime routes.

Public media starts muted by default. Consumers can configure video sources,
poster images, optional separate audio files, focus position, overlays, and
whether the rendered page should expose sound controls.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.19
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.19.html
PYTHONPATH=src python3 -m compileall src
```
