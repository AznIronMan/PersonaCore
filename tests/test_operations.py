from personaconsole import (
    AGENT_OPS_FEATURE,
    OPERATIONS_FEATURE,
    PERSONA_RUNTIME_FEATURE,
    AgentOpsSurfaceConfig,
    AgentSessionRow,
    AdminPrivacyContext,
    BridgeStatusCard,
    ContinuityItem,
    OperationsSurfaceConfig,
    OpsLogEvent,
    OpsSettingItem,
    OpsStatusCard,
    OpsTableRow,
    OwnerPrivateScopePolicy,
    PersonaPanel,
    PersonaRuntimeSurfaceConfig,
    SurfaceAction,
    TerminalStreamConfig,
    TerminalStreamEvent,
    agent_ops_surface_feature_enabled,
    operations_surface_feature_enabled,
    persona_runtime_surface_feature_enabled,
    render_agent_ops_surface,
    render_operations_surface,
    render_persona_runtime_surface,
    render_workflow_sections,
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


def test_operations_surface_renders_runtime_rows_logs_actions_and_masks_secret_values():
    html = render_operations_surface(
        OperationsSurfaceConfig(
            enabled=True,
            status_cards=[
                OpsStatusCard(
                    "<Workers>",
                    "lagging",
                    "/workers?queue=<main>",
                    detail="Queue above target",
                    tone="warn",
                    actions=[SurfaceAction("<Inspect>", "/workers/inspect", method="post")],
                )
            ],
            tasks=[OpsTableRow("task", "Refresh summaries", "running", detail="Runtime-owned task")],
            logs=[
                OpsLogEvent(
                    "Privacy",
                    "raw private log line",
                    href="/logs/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="safe log line",
                )
            ],
            settings=[
                OpsSettingItem("Webhook secret", "raw-secret-value", "configured", secret=True),
                OpsSettingItem("Feature flag", True, "enabled", changed=True),
            ],
        ),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert 'id="operations"' in html
    assert "&lt;Workers&gt;" in html
    assert "Refresh summaries" in html
    assert "safe log line" in html
    assert "raw private log line" not in html
    assert "/logs/raw-private" not in html
    assert "raw-secret-value" not in html
    assert "configured" in html
    assert "changed" in html
    assert 'data-method="POST"' in html
    assert '<article class="pc-ops-card' in html
    assert '<a class="pc-ops-card' not in html


def test_operations_surface_owner_can_see_raw_private_logs_and_links():
    html = render_operations_surface(
        OperationsSurfaceConfig(
            enabled=True,
            logs=[
                OpsLogEvent(
                    "Privacy",
                    "raw private log line",
                    href="/logs/raw-private",
                    privacy_scope="owner_private",
                    safe_alternate="safe log line",
                )
            ],
        ),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private log line" in html
    assert "/logs/raw-private" in html
    assert "safe log line" not in html


def test_persona_runtime_surface_redacts_private_continuity():
    html = render_persona_runtime_surface(
        PersonaRuntimeSurfaceConfig(
            enabled=True,
            panels=[
                PersonaPanel("Traits", 8, summary="Active traits"),
                PersonaPanel(
                    "raw private panel",
                    summary="raw private panel summary",
                    privacy_scope="owner_private",
                    safe_alternate="safe panel summary",
                ),
            ],
            continuity=[
                ContinuityItem(
                    "Memory",
                    "raw private memory",
                    "raw private memory summary",
                    "/persona/raw-memory",
                    privacy_scope="owner_private",
                    safe_alternate="safe memory summary",
                )
            ],
        ),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-persona-surface" in html
    assert "Traits" in html
    assert "safe panel summary" in html
    assert "safe memory summary" in html
    assert "raw private memory" not in html
    assert "/persona/raw-memory" not in html


def test_agent_ops_surface_renders_bridge_status_and_redacts_private_sessions():
    html = render_agent_ops_surface(
        AgentOpsSurfaceConfig(
            enabled=True,
            bridges=[BridgeStatusCard("Webhook", "healthy", route="verify", counts=[{"label": "0 failed", "tone": "good"}])],
            statuses=[OpsStatusCard("Preflight", "ready", detail="Read-only posture")],
            sessions=[
                AgentSessionRow(
                    "one",
                    "raw private session",
                    "held",
                    "/agent/raw",
                    objective="raw private objective",
                    privacy_scope="owner_private",
                    safe_alternate="safe session summary",
                )
            ],
            terminal_stream=TerminalStreamConfig(
                enabled=True,
                events=[
                    TerminalStreamEvent(
                        "terminal-one",
                        "raw private terminal line",
                        privacy_scope="owner_private",
                        safe_alternate="safe terminal summary",
                    )
                ],
            ),
        ),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-agent-ops-surface" in html
    assert "Webhook" in html
    assert "0 failed" in html
    assert "Preflight" in html
    assert "safe session summary" in html
    assert "pc-terminal-stream" in html
    assert "safe terminal summary" in html
    assert "raw private session" not in html
    assert "raw private objective" not in html
    assert "raw private terminal line" not in html
    assert "/agent/raw" not in html


def test_workflow_feature_flags_and_empty_states():
    operations = OperationsSurfaceConfig(enabled=True)
    persona = PersonaRuntimeSurfaceConfig(enabled=True)
    agent_ops = AgentOpsSurfaceConfig(enabled=True)

    assert operations_surface_feature_enabled(operations, {OPERATIONS_FEATURE: True}) is True
    assert persona_runtime_surface_feature_enabled(persona, {PERSONA_RUNTIME_FEATURE: True}) is True
    assert agent_ops_surface_feature_enabled(agent_ops, {AGENT_OPS_FEATURE: True}) is True

    assert render_operations_surface(operations, features={OPERATIONS_FEATURE: False}) == ""
    assert render_persona_runtime_surface(persona, features={PERSONA_RUNTIME_FEATURE: False}) == ""
    assert render_agent_ops_surface(agent_ops, features={AGENT_OPS_FEATURE: False}) == ""

    html = render_workflow_sections(operations=operations, persona=persona, agent_ops=agent_ops)

    assert "No operational items found." in html
    assert "No persona runtime items found." in html
    assert "No bridge or agent operations found." in html
