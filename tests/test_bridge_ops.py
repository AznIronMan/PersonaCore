from personaconsole import (
    BRIDGE_OPS_FEATURE,
    AdminPrivacyContext,
    BridgeDeliveryRow,
    BridgeHeartbeatRow,
    BridgeOpsSurfaceConfig,
    BridgeProviderCapabilityRow,
    BridgeQueueRow,
    BridgeStatusCard,
    BridgeWebhookRow,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    bridge_ops_feature_enabled,
    render_bridge_ops_surface,
)


def _policy() -> OwnerPrivateScopePolicy:
    return OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})


def _operator() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )


def _owner() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="owner_private",
        viewer_person_key="owner",
        allowed_scopes=("public", "operator", "owner_private"),
    )


def _config() -> BridgeOpsSurfaceConfig:
    return BridgeOpsSurfaceConfig(
        enabled=True,
        title="<Bridge Ops>",
        subtitle="Webhook, queue, provider, and delivery posture",
        tabs=[
            StatusTab("All", "/bridge", 8, active=True),
            StatusTab("Failed", "/bridge?status=failed", 1, tone="bad"),
        ],
        metrics=[
            DashboardMetric("Queues", 3, "/bridge/queues", "active queues", tone="info"),
            DashboardMetric("Failed", 1, "/bridge/failed", "needs review", tone="bad"),
        ],
        bridges=[
            BridgeStatusCard("Webhook", "healthy", "/bridge/webhook", "verify/reply", "Bridge responds.", "2m ago", "good", counts=[{"label": "0 failed", "tone": "good"}]),
            BridgeStatusCard("SMS bridge", "paused", detail="Inbound paused for review.", tone="warn", actions=[SurfaceAction("Inspect", "/bridge/sms")]),
        ],
        webhooks=[
            BridgeWebhookRow("verify", "Verify endpoint", "healthy", "good", "POST", "/webhooks/example", "ok", "2m ago", "Verification route responds."),
            BridgeWebhookRow("missing", "Optional callback", "missing", "warn", "POST", "/webhooks/optional", "not configured", actions=[SurfaceAction("Configure", "/bridge/webhooks/configure", "warn")]),
        ],
        queues=[
            BridgeQueueRow("inbound", "Inbound queue", "degraded", "warn", queued=4, failed=1, claimed=2, last_in="1m ago", last_out="5m ago", policy="retry on failure"),
            BridgeQueueRow("disabled", "Disabled queue", "disabled", "neutral", queued=0, failed=0, actions=[SurfaceAction("Resume", "", disabled=True)]),
        ],
        heartbeats=[
            BridgeHeartbeatRow("worker", "Worker heartbeat", "stale", "warn", "worker-loop", "420ms", "14m ago", "Heartbeat is older than target."),
        ],
        providers=[
            BridgeProviderCapabilityRow("chat", "Chat provider", "example-chat", "messages", "ready", "good", configured=True, enabled=True, docs_href="/docs/chat"),
            BridgeProviderCapabilityRow("email", "Email provider", "example-email", "email", "missing", "warn", configured=False, enabled=False, docs_href="/docs/email"),
        ],
        deliveries=[
            BridgeDeliveryRow("public", "Public delivery", "sent", "good", "outbound", "example-chat", "thread-1", 1, "09:00", "Delivered successfully."),
            BridgeDeliveryRow(
                "private",
                "Private delivery",
                "failed",
                "bad",
                "outbound",
                "example-chat",
                "private-target",
                3,
                "09:05",
                "raw private delivery failure",
                href="/bridge/deliveries/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe delivery failure",
            ),
        ],
        actions=[SurfaceAction("Refresh", "/bridge/refresh", "info", method="post")],
    )


def test_bridge_ops_surface_renders_provider_neutral_rows_and_redacts_delivery():
    html = render_bridge_ops_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-bridge-ops-surface" in html
    assert "&lt;Bridge Ops&gt;" in html
    assert "pc-status-tabs" in html
    assert "pc-bridge-ops-metric" in html
    assert "Webhook" in html
    assert "SMS bridge" in html
    assert "Verify endpoint" in html
    assert "Optional callback" in html
    assert "Inbound queue" in html
    assert "Disabled queue" in html
    assert 'aria-disabled="true"' in html
    assert "Worker heartbeat" in html
    assert "Chat provider" in html
    assert "Email provider" in html
    assert "not configured" in html
    assert 'href="/docs/chat"' in html
    assert "Public delivery" in html
    assert "safe delivery failure" in html
    assert "raw private delivery failure" not in html
    assert "/bridge/deliveries/raw-private" not in html
    assert 'data-method="POST"' in html


def test_bridge_ops_owner_can_see_private_delivery_link():
    html = render_bridge_ops_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private delivery failure" in html
    assert "/bridge/deliveries/raw-private" in html
    assert "safe delivery failure" not in html


def test_bridge_ops_feature_gate_and_empty_state():
    config = BridgeOpsSurfaceConfig(enabled=True)

    assert bridge_ops_feature_enabled(config, {BRIDGE_OPS_FEATURE: True}) is True
    assert bridge_ops_feature_enabled(config, {BRIDGE_OPS_FEATURE: False}) is False
    assert render_bridge_ops_surface(config, features={BRIDGE_OPS_FEATURE: False}) == ""

    html = render_bridge_ops_surface(config)

    assert "No bridge operation items configured." in html
