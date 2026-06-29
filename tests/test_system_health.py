from personaconsole import (
    SYSTEM_HEALTH_FEATURE,
    AdminPrivacyContext,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    SurfaceBadge,
    SystemAuditFilterState,
    SystemAuditRow,
    SystemDatabaseCard,
    SystemHealthCheck,
    SystemHealthGroup,
    SystemHealthSurfaceConfig,
    SystemPaginationState,
    SystemReadinessProbe,
    SystemSecretCoverageRow,
    SystemSecretFilterState,
    SystemSecretInventoryRow,
    SystemTableSummary,
    render_system_health_surface,
    system_health_surface_feature_enabled,
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


def _config() -> SystemHealthSurfaceConfig:
    return SystemHealthSurfaceConfig(
        enabled=True,
        title="<System Health>",
        subtitle="Database, audit, and readiness posture",
        tabs=[
            StatusTab("All", "/health", 12, active=True),
            StatusTab("Blocked", "/health?status=blocked", 2, tone="bad"),
        ],
        metrics=[
            DashboardMetric("Runtime", "ok", "/health/runtime", "all services reachable", tone="good"),
            DashboardMetric("Database", "degraded", "/health/database", "one stale table", tone="warn"),
        ],
        health_groups=[
            SystemHealthGroup(
                "runtime",
                "Runtime Checks",
                "Current runtime probes",
                status="degraded",
                tone="warn",
                badges=[SurfaceBadge("sampled", "info")],
                checks=[
                    SystemHealthCheck("admin", "Admin", "healthy", "good", "200", "Admin responds.", updated="1m ago", required=True),
                    SystemHealthCheck("worker", "Worker", "blocked", "bad", "held", "Manual pass required.", updated="4m ago", required=True, blocked=True),
                    {"key": "storage", "label": "Storage", "status": "unknown", "summary": "Not sampled yet."},
                ],
            )
        ],
        databases=[
            SystemDatabaseCard(
                "runtime-db",
                "Runtime DB",
                "degraded",
                "warn",
                database="runtime_db",
                user="runtime_user",
                host="internal",
                schema_version="2026.06",
                tables=12,
                records="4.2k",
                latency="42ms",
                summary="Connection works; freshness needs review.",
                actions=[SurfaceAction("Inspect", "/health/database")],
            )
        ],
        tables=[
            SystemTableSummary("messages", "healthy", "good", "current", 128, "runtime", "2m ago", "conversation rows current"),
            SystemTableSummary("audit_events", "stale", "warn", "current", 41, "admin", "1h ago", "freshness threshold exceeded"),
        ],
        secret_coverage=[
            SystemSecretCoverageRow(
                "providers",
                "Provider secrets",
                "configured",
                "good",
                section="providers",
                source="runtime",
                configured=3,
                present=3,
                missing=0,
                required=3,
                import_status="imported",
                last_checked="1m ago",
            ),
            SystemSecretCoverageRow(
                "webhooks",
                "Webhook secrets",
                "missing",
                "warn",
                section="webhooks",
                source="private file",
                present=2,
                missing=1,
                required=2,
                optional=2,
                import_status="needs import",
                last_checked="4m ago",
            ),
        ],
        secret_filters=SystemSecretFilterState(
            query="provider",
            section="providers",
            source="runtime",
            present="true",
            result_count=1,
            total_count=2,
            clear_href="/health/secrets",
            summary="Secret values stay out of the shared surface.",
        ),
        secret_rows=[
            SystemSecretInventoryRow(
                "provider-token",
                "Provider token",
                section="providers",
                source="runtime",
                status="configured",
                tone="good",
                value_kind="secret",
                present=True,
                active=True,
                import_status="imported",
                last_checked="1m ago",
                summary="Key name only.",
                href="/health/secrets?scope=providers",
            ),
            SystemSecretInventoryRow(
                "webhook-token",
                "Webhook token",
                section="webhooks",
                source="private file",
                status="missing",
                tone="warn",
                value_kind="secret",
                present=False,
                active=True,
                import_status="pending",
                last_checked="4m ago",
            ),
        ],
        secret_pagination=SystemPaginationState(page=1, page_count=2, total=2, limit=1, next_href="/health/secrets?page=2"),
        readiness=[
            SystemReadinessProbe("launch", "Launch preflight", "ready", "good", "Required checks passed.", checked_at="09:00"),
            SystemReadinessProbe("token-scan", "Token scan", "blocked", "bad", "Manual pass required.", checked_at="09:05"),
        ],
        audit_rows=[
            SystemAuditRow(
                "normal",
                "Settings update",
                "changed",
                "operator",
                "applied",
                "09:10",
                "Interval changed.",
                tone="info",
                entity="persona_state",
                source="admin_console",
            ),
            SystemAuditRow(
                "private-audit",
                "Owner-private audit",
                "held",
                "runtime",
                "private",
                "09:12",
                "raw private system audit",
                tone="warn",
                href="/audit/private-raw",
                privacy_scope="owner_private",
                safe_alternate="safe system audit summary",
                entity="owner-private-state",
                source="admin_console",
            ),
        ],
        audit_filters=SystemAuditFilterState(
            query="settings",
            actor="operator",
            action="changed",
            entity="persona_state",
            source="admin_console",
            status="applied",
            date_from="2026-06-01",
            date_to="2026-06-29",
            result_count=2,
            total_count=41,
            clear_href="/health/audit",
            summary="Payload values stay hidden.",
        ),
        audit_pagination=SystemPaginationState(page=1, page_count=3, total=41, limit=20, next_href="/health/audit?page=2"),
        actions=[SurfaceAction("Refresh", "/health/refresh", "info", method="post")],
    )


def test_system_health_surface_renders_dense_public_safe_posture():
    html = render_system_health_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-system-health-surface" in html
    assert "&lt;System Health&gt;" in html
    assert "pc-status-tabs" in html
    assert "Runtime Checks" in html
    assert "required" in html
    assert "blocked" in html
    assert "Runtime DB" in html
    assert "runtime_db" in html
    assert "internal" in html
    assert "Schema And Tables" in html
    assert "audit_events" in html
    assert "Secret Coverage" in html
    assert "Webhook secrets" in html
    assert "Values are never rendered here." in html
    assert "Secret Rows" in html
    assert "Provider token" in html
    assert "Showing 1 of 2 secret rows" in html
    assert "Readiness" in html
    assert "Token scan" in html
    assert "Audit Events" in html
    assert "persona_state" in html
    assert "Showing 2 of 41 audit events" in html
    assert "Payload values stay hidden." in html
    assert "pc-system-mobile-cards" in html
    assert "safe system audit summary" in html
    assert "raw private system audit" not in html
    assert "/audit/private-raw" not in html


def test_system_health_owner_private_audit_can_render_raw_for_owner():
    html = render_system_health_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private system audit" in html
    assert "safe system audit summary" not in html
    assert "/audit/private-raw" in html


def test_system_health_feature_gate_and_empty_state():
    config = SystemHealthSurfaceConfig(enabled=True)

    assert system_health_surface_feature_enabled(config, {SYSTEM_HEALTH_FEATURE: True}) is True
    assert system_health_surface_feature_enabled(config, {SYSTEM_HEALTH_FEATURE: False}) is False
    assert render_system_health_surface(config, features={SYSTEM_HEALTH_FEATURE: False}) == ""

    html = render_system_health_surface(config)

    assert "No system posture data configured." in html
