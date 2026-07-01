from personaconsole import (
    ADMIN_ACCESS_FEATURE,
    AdminAccessActionSlot,
    AdminAccessAuditRow,
    AdminAccessPrincipalRow,
    AdminAccessRuleRow,
    AdminAccessSessionRow,
    AdminAccessSurfaceConfig,
    AdminAccessWarningRow,
    AdminPrivacyContext,
    DashboardMetric,
    LiveRefreshConfig,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    admin_access_feature_enabled,
    render_admin_access_surface,
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


def _config() -> AdminAccessSurfaceConfig:
    return AdminAccessSurfaceConfig(
        enabled=True,
        title="Admin Access",
        subtitle="Sessions, principals, block rules, lockouts, and audit posture.",
        status="locked",
        status_tone="bad",
        tabs=[
            StatusTab("All", "/access", 5, active=True),
            StatusTab("Blocked", "/access?status=blocked", 1, tone="bad"),
        ],
        metrics=[DashboardMetric("Active sessions", "2", detail="1 stale", tone="warn")],
        principals=[
            AdminAccessPrincipalRow("operator", "Fixture Operator", "admin", "active", "good", "1m ago", "operator", "Public-safe principal."),
            AdminAccessPrincipalRow(
                "private-principal",
                "Private principal",
                "owner",
                "locked",
                "bad",
                "14m ago",
                "owner_private",
                "raw private access principal",
                "/access/raw-private-principal",
                privacy_scope="owner_private",
                safe_alternate="safe principal summary",
            ),
        ],
        sessions=[
            AdminAccessSessionRow("session", "Current session", "operator", "active", "good", "09:00", "1m ago", "10:00", "browser", "local", "Session is current."),
            AdminAccessSessionRow(
                "private-session",
                "Private session",
                "owner",
                "stale",
                "warn",
                "08:00",
                "14m ago",
                "09:00",
                "raw private access device",
                "raw private access location",
                "raw private access session",
                "/access/raw-private-session",
                privacy_scope="owner_private",
                safe_alternate="safe session summary",
            ),
        ],
        rules=[
            AdminAccessRuleRow("allow", "Operator allow", "allow", "active", "good", "operator", "Public-safe allow rule.", "never", "09:00"),
            AdminAccessRuleRow(
                "block",
                "Blocked source",
                "block",
                "blocked",
                "bad",
                "raw private access target",
                "raw private access block reason",
                "today",
                "09:05",
                "/access/raw-private-rule",
                privacy_scope="owner_private",
                safe_alternate="safe block summary",
            ),
        ],
        warnings=[
            AdminAccessWarningRow("lockout", "Lockout active", "locked", "bad", "A lockout is active for review.", "high", "1m ago"),
        ],
        audits=[
            AdminAccessAuditRow("login", "Login accepted", "accepted", "good", "operator", "login", "admin", "09:00", "Operator login accepted."),
            AdminAccessAuditRow(
                "private-audit",
                "Private audit",
                "denied",
                "bad",
                "owner",
                "login",
                "admin",
                "09:05",
                "raw private access audit",
                "/access/raw-private-audit",
                privacy_scope="owner_private",
                safe_alternate="safe audit summary",
            ),
        ],
        live_refresh=LiveRefreshConfig(enabled=True, key="access", url="/fragments/access", target_id="admin-access"),
        action_slots=[
            AdminAccessActionSlot(
                "handoff",
                "Runtime-owned unlock",
                "Consumer route owns emergency unlock.",
                '<form action="/access/unlock" method="post"></form>',
                "warn",
                actions=[SurfaceAction("Unlock", "", "warn", disabled=True)],
            )
        ],
        actions=[SurfaceAction("Refresh access", "/access/refresh", "info", method="post")],
    )


def test_admin_access_renders_sessions_rules_audit_and_redacts_private_values():
    html = render_admin_access_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-admin-access-surface" in html
    assert "Admin Access" in html
    assert "Fixture Operator" in html
    assert "Current session" in html
    assert "Operator allow" in html
    assert "Lockout active" in html
    assert "Login accepted" in html
    assert "Runtime-owned unlock" in html
    assert 'action="/access/unlock"' in html
    assert "data-pc-live-controls" in html
    assert "safe principal summary" in html
    assert "safe session summary" in html
    assert "safe block summary" in html
    assert "safe audit summary" in html
    assert "Unlock" in html
    assert 'aria-disabled="true"' in html
    assert "raw private access" not in html
    assert "/access/raw-private" not in html


def test_admin_access_owner_can_see_raw_private_values_and_links():
    html = render_admin_access_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private access principal" in html
    assert "raw private access session" in html
    assert "raw private access block reason" in html
    assert "raw private access audit" in html
    assert "/access/raw-private-session" in html
    assert "safe session summary" not in html


def test_admin_access_feature_gate_and_empty_state():
    config = AdminAccessSurfaceConfig(enabled=True)

    assert admin_access_feature_enabled(config, {ADMIN_ACCESS_FEATURE: True}) is True
    assert admin_access_feature_enabled(config, {ADMIN_ACCESS_FEATURE: False}) is False
    assert render_admin_access_surface(config, features={ADMIN_ACCESS_FEATURE: False}) == ""

    html = render_admin_access_surface(config)

    assert "No admin access posture items configured." in html
