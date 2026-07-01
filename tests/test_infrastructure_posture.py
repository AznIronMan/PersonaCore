from personaconsole import (
    INFRASTRUCTURE_POSTURE_FEATURE,
    AdminPrivacyContext,
    DashboardMetric,
    InfrastructureActionSlot,
    InfrastructureCertificateRow,
    InfrastructureCheckRow,
    InfrastructureDnsRecordRow,
    InfrastructureEndpointRow,
    InfrastructurePostureSurfaceConfig,
    InfrastructureWarningRow,
    LiveRefreshConfig,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    infrastructure_posture_feature_enabled,
    render_infrastructure_posture_surface,
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


def _config() -> InfrastructurePostureSurfaceConfig:
    return InfrastructurePostureSurfaceConfig(
        enabled=True,
        title="Infrastructure Posture",
        subtitle="DNS, certificates, endpoints, propagation, and warnings.",
        status="degraded",
        status_tone="warn",
        tabs=[
            StatusTab("All", "/infra", 5, active=True),
            StatusTab("Warnings", "/infra?status=warn", 2, tone="warn"),
        ],
        metrics=[DashboardMetric("Expiring", "1", detail="certificate window", tone="warn")],
        dns_records=[
            InfrastructureDnsRecordRow("apex", "Apex A", "A", "example.com", "203.0.113.10", "203.0.113.10", "verified", "good", 300, "generic dns", "1m ago"),
            InfrastructureDnsRecordRow(
                "private-dns",
                "Private DNS",
                "CNAME",
                "raw private infra name",
                "raw private infra value",
                "raw private infra expected",
                "stale",
                "warn",
                60,
                "provider",
                "14m ago",
                "raw private infra detail",
                "/infra/raw-private-dns",
                privacy_scope="owner_private",
                safe_alternate="safe dns summary",
            ),
        ],
        certificates=[
            InfrastructureCertificateRow("edge", "Edge certificate", "example.com", "Example CA", "expiring", "warn", "2026-08-01", 31, "managed", "1m ago", "Renewal is scheduled."),
            InfrastructureCertificateRow(
                "private-cert",
                "Private certificate",
                "raw private infra subject",
                "raw private infra issuer",
                "failed",
                "bad",
                "2026-07-10",
                9,
                "manual",
                "14m ago",
                "raw private infra cert detail",
                "/infra/raw-private-cert",
                privacy_scope="owner_private",
                safe_alternate="safe certificate summary",
            ),
        ],
        endpoints=[
            InfrastructureEndpointRow("home", "Public homepage", "https://example.com", "healthy", "good", "GET", 200, "84ms", "1m ago", "Edge returned ok."),
        ],
        checks=[
            InfrastructureCheckRow("propagation", "DNS propagation", "propagating", "warn", "resolver", "Apex A", "2/3", "3/3", "1m ago", "One resolver still has the old value."),
        ],
        warnings=[
            InfrastructureWarningRow("expiry", "Certificate expiry", "warning", "warn", "Certificate enters renewal window soon.", "medium", "1m ago"),
            InfrastructureWarningRow(
                "private-warning",
                "Private warning",
                "warning",
                "bad",
                "raw private infra warning",
                "high",
                "1m ago",
                "/infra/raw-private-warning",
                privacy_scope="owner_private",
                safe_alternate="safe warning summary",
            ),
        ],
        live_refresh=LiveRefreshConfig(enabled=True, key="infra", url="/fragments/infra", target_id="infrastructure-posture"),
        action_slots=[
            InfrastructureActionSlot(
                "handoff",
                "Provider handoff",
                "Consumer owns provider actions.",
                '<form action="/infra/handoff" method="post"></form>',
                "info",
                actions=[SurfaceAction("Renew now", "", "warn", disabled=True)],
            )
        ],
        actions=[SurfaceAction("Refresh checks", "/infra/refresh", "info", method="post")],
    )


def test_infrastructure_posture_renders_diagnostics_and_redacts_private_values():
    html = render_infrastructure_posture_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-infra-posture-surface" in html
    assert "Infrastructure Posture" in html
    assert "Apex A" in html
    assert "Edge certificate" in html
    assert "Public homepage" in html
    assert "DNS propagation" in html
    assert "Certificate expiry" in html
    assert "Provider handoff" in html
    assert 'action="/infra/handoff"' in html
    assert "data-pc-live-controls" in html
    assert "safe dns summary" in html
    assert "safe certificate summary" in html
    assert "safe warning summary" in html
    assert "Renew now" in html
    assert 'aria-disabled="true"' in html
    assert "raw private infra" not in html
    assert "/infra/raw-private" not in html


def test_infrastructure_posture_owner_can_see_raw_private_values_and_links():
    html = render_infrastructure_posture_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private infra name" in html
    assert "raw private infra cert detail" in html
    assert "raw private infra warning" in html
    assert "/infra/raw-private-dns" in html
    assert "safe dns summary" not in html


def test_infrastructure_posture_feature_gate_and_empty_state():
    config = InfrastructurePostureSurfaceConfig(enabled=True)

    assert infrastructure_posture_feature_enabled(config, {INFRASTRUCTURE_POSTURE_FEATURE: True}) is True
    assert infrastructure_posture_feature_enabled(config, {INFRASTRUCTURE_POSTURE_FEATURE: False}) is False
    assert render_infrastructure_posture_surface(config, features={INFRASTRUCTURE_POSTURE_FEATURE: False}) == ""

    html = render_infrastructure_posture_surface(config)

    assert "No infrastructure posture items configured." in html
