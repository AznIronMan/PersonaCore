from personaconsole import (
    AVAILABILITY_MONITOR_FEATURE,
    AdminPrivacyContext,
    AvailabilityEventRow,
    AvailabilityMonitorRow,
    AvailabilityMonitorSurfaceConfig,
    AvailabilityPolicyRow,
    AvailabilityScenarioRow,
    AvailabilityWindowRow,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    availability_monitor_feature_enabled,
    render_availability_monitor_surface,
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


def _config() -> AvailabilityMonitorSurfaceConfig:
    return AvailabilityMonitorSurfaceConfig(
        enabled=True,
        title="<Availability>",
        subtitle="Schedule and monitor posture",
        tabs=[
            StatusTab("Live", "/availability", 2, active=True, tone="good"),
            StatusTab("Review", "/availability?status=review", 1, tone="warn"),
        ],
        metrics=[
            DashboardMetric("Open windows", 1, "/availability/windows", "active", tone="good"),
            DashboardMetric("Warnings", 1, "/availability/warnings", "needs review", tone="warn"),
        ],
        windows=[
            AvailabilityWindowRow("public", "Public window", "open", "good", "09:00", "17:00", "UTC", "weekday", "chat", "Public summary."),
            AvailabilityWindowRow(
                "private",
                "Private window",
                "held",
                "warn",
                "19:00",
                "21:00",
                "UTC",
                "manual",
                "private",
                "raw private availability window",
                detail="raw private availability detail",
                href="/availability/windows/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe availability window",
            ),
        ],
        monitors=[
            AvailabilityMonitorRow("queue", "Queue latency", "healthy", "good", "12s", "30s", "1m ago", "2m"),
            AvailabilityMonitorRow("worker", "Worker heartbeat", "stale", "warn", "14m", "5m", "14m ago", "1m", actions=[SurfaceAction("Restart", "", disabled=True)]),
        ],
        policies=[
            AvailabilityPolicyRow("review", "Review gate", "active", "good", "operator confirmation", "Required for risky sends."),
        ],
        scenarios=[
            AvailabilityScenarioRow(
                "private-scenario",
                "Private scenario",
                "review",
                "warn",
                "preflight",
                "hold",
                "08:30",
                "10:00",
                "raw private availability scenario",
                href="/availability/scenarios/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe availability scenario",
            )
        ],
        events=[
            AvailabilityEventRow(
                "private-event",
                "Private event",
                "held",
                "warn",
                "09:10",
                "monitor",
                "raw private availability event",
                href="/availability/events/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe availability event",
            )
        ],
        actions=[SurfaceAction("Refresh", "/availability/refresh", "info", method="post")],
    )


def test_availability_monitor_surface_renders_rows_and_redacts_private_text():
    html = render_availability_monitor_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-availability-monitor-surface" in html
    assert "&lt;Availability&gt;" in html
    assert "pc-status-tabs" in html
    assert "pc-availability-metric" in html
    assert "Schedule Windows" in html
    assert "Public window" in html
    assert "Queue latency" in html
    assert "Worker heartbeat" in html
    assert "Review gate" in html
    assert "Private scenario" in html
    assert "Private event" in html
    assert "safe availability window" in html
    assert "safe availability scenario" in html
    assert "safe availability event" in html
    assert 'data-method="POST"' in html
    assert 'aria-disabled="true"' in html
    assert "raw private availability window" not in html
    assert "raw private availability detail" not in html
    assert "raw private availability scenario" not in html
    assert "raw private availability event" not in html
    assert "/availability/windows/raw-private" not in html
    assert "/availability/scenarios/raw-private" not in html
    assert "/availability/events/raw-private" not in html


def test_availability_monitor_owner_can_see_private_links():
    html = render_availability_monitor_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private availability window" in html
    assert "raw private availability scenario" in html
    assert "raw private availability event" in html
    assert "/availability/windows/raw-private" in html
    assert "/availability/scenarios/raw-private" in html
    assert "/availability/events/raw-private" in html
    assert "safe availability window" not in html


def test_availability_monitor_feature_gate_and_empty_state():
    config = AvailabilityMonitorSurfaceConfig(enabled=True)

    assert availability_monitor_feature_enabled(config, {AVAILABILITY_MONITOR_FEATURE: True}) is True
    assert availability_monitor_feature_enabled(config, {AVAILABILITY_MONITOR_FEATURE: False}) is False
    assert render_availability_monitor_surface(config, features={AVAILABILITY_MONITOR_FEATURE: False}) == ""

    html = render_availability_monitor_surface(config)

    assert "No availability monitor items configured." in html
