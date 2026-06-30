from personaconsole import (
    COMMAND_INTAKE_FEATURE,
    AdminPrivacyContext,
    CommandCandidateRow,
    CommandConfirmationStep,
    CommandHistoryRow,
    CommandIntakeSurfaceConfig,
    CommandParsedField,
    CommandQueueRow,
    CommandRiskRow,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    command_intake_feature_enabled,
    render_command_intake_surface,
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


def _config() -> CommandIntakeSurfaceConfig:
    return CommandIntakeSurfaceConfig(
        enabled=True,
        title="<Command Intake>",
        subtitle="Parsed preview and queue posture",
        tabs=[
            StatusTab("Preview", "/commands", 1, active=True, tone="info"),
            StatusTab("Queued", "/commands?status=queued", 2, tone="warn"),
        ],
        metrics=[
            DashboardMetric("Parsed", 1, "/commands", "ready", tone="good"),
            DashboardMetric("Queued", 2, "/commands/queue", "runtime owned", tone="warn"),
        ],
        form_action="/commands/preview",
        input_value="raw private command prompt",
        input_privacy_scope="owner_private",
        input_safe_alternate="safe command prompt",
        submit_label="Preview safely",
        queue_label="Queue command",
        queue_href="/commands/queue",
        parsed_fields=[
            CommandParsedField("intent", "Intent", "adjust schedule", status="parsed", tone="good"),
            CommandParsedField(
                "target",
                "Private target",
                "raw private parsed target",
                privacy_scope="owner_private",
                safe_alternate="safe parsed target",
            ),
        ],
        candidates=[
            CommandCandidateRow(
                "person",
                "Example candidate",
                "person",
                "0.91",
                "matched",
                "info",
                "raw private candidate summary",
                detail="raw private candidate detail",
                href="/commands/candidates/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe candidate summary",
                actions=[SurfaceAction("Use candidate", "/commands/candidates/use", "good", method="post")],
            )
        ],
        risks=[
            CommandRiskRow(
                "policy",
                "Policy check",
                "medium",
                "review",
                "warn",
                "raw private risk summary",
                privacy_scope="owner_private",
                safe_alternate="safe risk summary",
            )
        ],
        confirmations=[
            CommandConfirmationStep(
                "operator",
                "Operator confirmation",
                "pending",
                "warn",
                "Required before queueing.",
                actions=[SurfaceAction("Confirm", "/commands/confirm", "good", method="post")],
            ),
            CommandConfirmationStep("disabled", "Disabled confirmation", "missing", "warn", actions=[SurfaceAction("Unavailable", "", disabled=True)]),
        ],
        queue=[
            CommandQueueRow(
                "queued",
                "Queued command",
                "queued",
                "info",
                "raw private queued command",
                "operator",
                "Example target",
                "09:10",
                "raw private queue detail",
                href="/commands/queue/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe queued command",
            )
        ],
        history=[
            CommandHistoryRow(
                "history",
                "Previous command",
                "completed",
                "good",
                "raw private command history",
                "operator",
                "Example target",
                "08:40",
                "2s",
                "raw private history detail",
                href="/commands/history/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe command history",
            )
        ],
        actions=[SurfaceAction("Open docs", "/commands/docs", "info")],
    )


def test_command_intake_surface_renders_preview_and_redacts_private_text():
    html = render_command_intake_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-command-intake-surface" in html
    assert "&lt;Command Intake&gt;" in html
    assert "pc-status-tabs" in html
    assert "pc-command-intake-metric" in html
    assert 'action="/commands/preview"' in html
    assert "Preview safely" in html
    assert "Queue command" in html
    assert "Parsed Preview" in html
    assert "Intent" in html
    assert "safe command prompt" in html
    assert "safe parsed target" in html
    assert "Example candidate" in html
    assert "safe candidate summary" in html
    assert "safe risk summary" in html
    assert "Operator confirmation" in html
    assert "safe queued command" in html
    assert "safe command history" in html
    assert 'data-method="POST"' in html
    assert 'aria-disabled="true"' in html
    assert "raw private command prompt" not in html
    assert "raw private parsed target" not in html
    assert "raw private candidate summary" not in html
    assert "raw private candidate detail" not in html
    assert "raw private risk summary" not in html
    assert "raw private queued command" not in html
    assert "raw private queue detail" not in html
    assert "raw private command history" not in html
    assert "raw private history detail" not in html
    assert "/commands/queue/raw-private" not in html
    assert "/commands/history/raw-private" not in html


def test_command_intake_owner_can_see_private_command_links():
    html = render_command_intake_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private command prompt" in html
    assert "raw private parsed target" in html
    assert "raw private queued command" in html
    assert "raw private command history" in html
    assert "/commands/queue/raw-private" in html
    assert "/commands/history/raw-private" in html
    assert "safe queued command" not in html


def test_command_intake_feature_gate_and_empty_state():
    config = CommandIntakeSurfaceConfig(enabled=True)

    assert command_intake_feature_enabled(config, {COMMAND_INTAKE_FEATURE: True}) is True
    assert command_intake_feature_enabled(config, {COMMAND_INTAKE_FEATURE: False}) is False
    assert render_command_intake_surface(config, features={COMMAND_INTAKE_FEATURE: False}) == ""

    html = render_command_intake_surface(config)

    assert "No command preview data configured." in html
    assert "Queue command" in html
