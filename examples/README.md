# PersonaConsole Fixture App

This directory contains a public-safe fixture admin console using generic data.
It is intended for examples, browser smoke tests, and visual regression targets.

Render a static HTML file:

```bash
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture.html
```

Run as a FastAPI app when optional dependencies are installed:

```bash
python3 -m pip install -e ".[fastapi]" uvicorn
PYTHONPATH=src python3 -m uvicorn examples.fixture_app:create_app --factory --reload
```

Open `http://127.0.0.1:8000/` for the admin fixture. Public presence fixture
routes are available at `/public/splash`, `/public/login`, `/public/chat`, and
`/settings/public-presence`.
