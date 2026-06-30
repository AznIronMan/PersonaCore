# Release 1.0.34

`1.0.34` adds reusable admin authentication page renderers for consumer
runtimes.

## Added

- `AdminLoginPageConfig` and `AdminPasswordChangePageConfig` for runtime-branded
  operator login and password-change pages.
- `AdminAuthLink` and `AdminAuthSummaryItem` display models for help/legal links
  and auth-state summaries.
- `render_admin_login_page(...)` and
  `render_admin_password_change_page(...)`.
- Shared CSS for dense admin auth shells, form controls, status summaries, and
  no-JS-safe form behavior.
- Fixture and visual-smoke routes for `/admin/login` and
  `/admin/password-change`.
- Doctor/export checks for the new auth page contract.

## Safety

The renderers only emit same-origin root-relative form actions, hidden next
paths, static asset URLs, help/legal links, and logo URLs. Unsafe absolute,
protocol-relative, malformed, or blocked auth-loop paths fall back to safe
defaults. Consumers still own password checks, sessions, cookies, CSRF, device
trust, lockout policy, audit writes, and persistence.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.34
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.34.html
python3 scripts/visual_smoke.py
```
