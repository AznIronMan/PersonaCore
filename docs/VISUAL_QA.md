# Visual QA

PersonaConsole includes an optional Playwright smoke for the public-safe fixture
admin console. It verifies the shared shell, dashboard primitives, live
controls, the shared people surface, journal surface, operations/persona/agent
workflow surfaces, public presence settings, desktop navigation, mobile
navigation, and the public splash, login, and chat pages, then writes
screenshots.

Install optional tooling:

```bash
python3 -m pip install -e ".[visual]"
python3 -m playwright install chromium
```

Run the smoke:

```bash
PYTHONPATH=src python3 scripts/visual_smoke.py
```

Screenshots are written to:

```text
build/visual-smoke/screenshots/
```

The smoke uses only generic fixture data. Private runtime screenshots,
credentials, authenticated sessions, and deployment paths must stay outside the
public PersonaConsole repo.

The fixture follows the public
[Reference Admin Parity Spec](REFERENCE_ADMIN_PARITY_SPEC.md), so screenshots
are useful for consumer alignment without exposing private runtime details.
