# Release 1.0.26

`1.0.26` adds reusable bridge operation panels for consumer admin consoles that
need provider-neutral webhook, queue, heartbeat, provider capability, and
delivery-claim views.

## Changes

- Added `BridgeOpsSurfaceConfig`, `BridgeWebhookRow`, `BridgeQueueRow`,
  `BridgeHeartbeatRow`, `BridgeProviderCapabilityRow`, and
  `BridgeDeliveryRow`.
- Added `BRIDGE_OPS_FEATURE`, `render_bridge_ops_surface(...)`, and
  `bridge_ops_feature_enabled(...)`.
- Renders bridge status cards, webhook rows, queue rows, heartbeat rows,
  provider capability rows, delivery claims, metric strips, status tabs,
  documentation links, disabled actions, and action slots.
- Supports owner-private redaction for delivery details and private delivery
  hrefs.
- Added fixture, static CSS, doctor, import, compatibility shim, and focused
  renderer test coverage.

## Boundaries

PersonaConsole does not verify webhooks, send messages, claim queue work, call
provider APIs, access browser profiles, manage OAuth, read credentials, or
perform deployments. Consumers own adapter execution, delivery queues,
credentials, callback routes, provider policy, browser/container state, and
deployment wiring.

## Verification

```bash
PYTHONPATH=src python3 -m pytest tests
PYTHONPATH=src python3 scripts/consumer_integration_doctor.py --expected-version 1.0.26
PYTHONPATH=src python3 examples/fixture_app.py --output /tmp/personaconsole-fixture-1.0.26.html
```
