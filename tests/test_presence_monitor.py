from personaconsole import (
    PRESENCE_MONITOR_FEATURE,
    AdminPrivacyContext,
    DashboardMetric,
    LiveRefreshConfig,
    OwnerPrivateScopePolicy,
    PresenceChannelRow,
    PresenceMonitorSurfaceConfig,
    PresencePolicyNotice,
    PresenceScheduleWindow,
    PresenceSourceFreshnessRow,
    PresenceStateCard,
    PresenceTransitionRow,
    StatusTab,
    SurfaceAction,
    presence_monitor_feature_enabled,
    render_presence_monitor_surface,
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


def _config() -> PresenceMonitorSurfaceConfig:
    return PresenceMonitorSurfaceConfig(
        enabled=True,
        title="Presence Monitor",
        subtitle="Presence state, channel posture, schedule, freshness, and transitions.",
        status="degraded",
        status_tone="warn",
        tabs=[
            StatusTab("All", "/presence", 5, active=True),
            StatusTab("Stale", "/presence?status=stale", 1, tone="warn"),
        ],
        metrics=[DashboardMetric("Online channels", "2", detail="1 stale", tone="warn")],
        states=[
            PresenceStateCard(
                "runtime",
                "Runtime Presence",
                "online",
                "good",
                "available",
                "web",
                "Public-safe state detail.",
                "1m ago",
                "quiet hours",
            ),
            PresenceStateCard(
                "private-state",
                "Owner-private state",
                "held",
                "warn",
                detail="raw private presence state",
                href="/presence/raw-private-state",
                privacy_scope="owner_private",
                safe_alternate="safe presence state",
            ),
        ],
        channels=[
            PresenceChannelRow("web", "Web chat", "web", "online", "good", "available", "public", "1m ago", "fresh"),
            PresenceChannelRow(
                "private-channel",
                "Private channel",
                "private",
                "stale",
                "warn",
                detail="raw private presence channel",
                href="/presence/raw-private-channel",
                privacy_scope="owner_private",
                safe_alternate="safe channel summary",
            ),
        ],
        schedule=[
            PresenceScheduleWindow("day", "Daytime", "active", "good", "08:00", "18:00", "UTC", "daily", "web", "Public schedule."),
            PresenceScheduleWindow(
                "private-window",
                "Private window",
                "scheduled",
                "warn",
                "20:00",
                "22:00",
                "UTC",
                "manual",
                "private",
                "raw private schedule policy",
                href="/presence/raw-private-window",
                privacy_scope="owner_private",
                safe_alternate="safe schedule summary",
            ),
        ],
        sources=[
            PresenceSourceFreshnessRow("adapter", "Adapter heartbeat", "adapter", "fresh", "good", "1m ago", "8s", "30s"),
            PresenceSourceFreshnessRow(
                "private-source",
                "Private source",
                "adapter",
                "stale",
                "warn",
                detail="raw private source detail",
                href="/presence/raw-private-source",
                privacy_scope="owner_private",
                safe_alternate="safe source summary",
            ),
        ],
        policies=[
            PresencePolicyNotice("quiet", "Quiet hours", "active", "info", "Public policy summary."),
            PresencePolicyNotice(
                "private-policy",
                "Private policy",
                "held",
                "warn",
                "raw private policy",
                href="/presence/raw-private-policy",
                privacy_scope="owner_private",
                safe_alternate="safe policy summary",
            ),
        ],
        transitions=[
            PresenceTransitionRow("online", "Went online", "offline", "online", "applied", "good", "operator", "09:00", "Public transition."),
            PresenceTransitionRow(
                "private-transition",
                "Private transition",
                "hidden",
                "available",
                "held",
                "warn",
                "operator",
                "09:05",
                "raw private transition",
                href="/presence/raw-private-transition",
                privacy_scope="owner_private",
                safe_alternate="safe transition summary",
            ),
        ],
        live_refresh=LiveRefreshConfig(
            enabled=True,
            key="presence",
            url="/fragments/presence",
            target_id="presence-monitor",
            controls_id="presence-live-controls",
            interval_seconds=30,
        ),
        actions=[
            SurfaceAction("Refresh", "/presence/refresh", "info", method="post"),
            SurfaceAction("Apply state", "", "warn", disabled=True),
        ],
    )


def test_presence_monitor_renders_state_channels_schedule_and_redacts_private_values():
    html = render_presence_monitor_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-presence-monitor-surface" in html
    assert "Presence Monitor" in html
    assert "Runtime Presence" in html
    assert "Web chat" in html
    assert "Daytime" in html
    assert "Adapter heartbeat" in html
    assert "Quiet hours" in html
    assert "Went online" in html
    assert "safe presence state" in html
    assert "safe channel summary" in html
    assert "safe schedule summary" in html
    assert "safe source summary" in html
    assert "safe policy summary" in html
    assert "safe transition summary" in html
    assert "data-pc-live-controls" in html
    assert "Apply state" in html
    assert 'aria-disabled="true"' in html
    assert "raw private presence" not in html
    assert "raw private schedule policy" not in html
    assert "raw private source detail" not in html
    assert "raw private policy" not in html
    assert "raw private transition" not in html
    assert "/presence/raw-private" not in html


def test_presence_monitor_owner_can_see_raw_private_values_and_links():
    html = render_presence_monitor_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private presence state" in html
    assert "raw private presence channel" in html
    assert "raw private schedule policy" in html
    assert "raw private source detail" in html
    assert "raw private policy" in html
    assert "raw private transition" in html
    assert "/presence/raw-private-state" in html
    assert "safe presence state" not in html


def test_presence_monitor_feature_gate_and_empty_state():
    config = PresenceMonitorSurfaceConfig(enabled=True)

    assert presence_monitor_feature_enabled(config, {PRESENCE_MONITOR_FEATURE: True}) is True
    assert presence_monitor_feature_enabled(config, {PRESENCE_MONITOR_FEATURE: False}) is False
    assert render_presence_monitor_surface(config, features={PRESENCE_MONITOR_FEATURE: False}) == ""

    html = render_presence_monitor_surface(config)

    assert "No presence monitor items configured." in html
