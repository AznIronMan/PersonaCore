from personaconsole import (
    WORKER_OPERATIONS_FEATURE,
    AdminPrivacyContext,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    SurfaceAction,
    SurfaceBadge,
    WorkerControlActionSlot,
    WorkerDeadLetterRow,
    WorkerDryRunCandidate,
    WorkerOperationsSurfaceConfig,
    WorkerProcessEvent,
    WorkerReadinessRow,
    WorkerRollbackCandidate,
    WorkerRunTelemetryRow,
    WorkerScheduleRow,
    render_worker_operations_surface,
    worker_operations_surface_feature_enabled,
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


def test_worker_operations_surface_renders_all_sections_and_review_slots():
    html = render_worker_operations_surface(
        WorkerOperationsSurfaceConfig(
            enabled=True,
            title="<Worker Ops>",
            metrics=[DashboardMetric("Ready", 2, "/workers?status=ready", "enabled", tone="good")],
            readiness=[
                WorkerReadinessRow(
                    "reflection",
                    "Reflection worker",
                    "ready",
                    "good",
                    control_state="resume",
                    schedule_status="due soon",
                    next_run="2m",
                    last_run="13m",
                    summary="<safe summary>",
                    href="/workers/reflection",
                    badges=[SurfaceBadge("review-first", "info")],
                    actions=[SurfaceAction("Inspect", "/workers/reflection")],
                )
            ],
            schedules=[WorkerScheduleRow("reflection-schedule", "reflection", "Reflection schedule", status="enabled", cadence="15m")],
            runs=[WorkerRunTelemetryRow("run-1", "reflection", "succeeded", "due", "09:40", output="2 summaries refreshed")],
            dead_letters=[WorkerDeadLetterRow("dead-1", "media", "open", "provider", "retry queued", retries=1)],
            rollback_candidates=[WorkerRollbackCandidate("rollback-1", "media", "dry_run", "resume", audit_id=42, reason="review rollback")],
            dry_run_candidates=[WorkerDryRunCandidate("dry-1", "self_learn", "worker_dry_run", "reflection", "recorded", summary="candidate captured")],
            process_events=[WorkerProcessEvent("event-1", "reflection", "run", "succeeded", "tick completed")],
            action_slots=[
                WorkerControlActionSlot(
                    "control",
                    "Queue Control Proposal",
                    "Runtime-owned action target.",
                    '<form action="/workers/proposals" method="post"><button>Queue</button></form>',
                )
            ],
            actions=[SurfaceAction("Open Workers", "/workers")],
        )
    )

    assert "pc-worker-ops-surface" in html
    assert "&lt;Worker Ops&gt;" in html
    assert "Reflection worker" in html
    assert "&lt;safe summary&gt;" in html
    assert "Reflection schedule" in html
    assert "2 summaries refreshed" in html
    assert "retry queued" in html
    assert "review rollback" in html
    assert "candidate captured" in html
    assert "tick completed" in html
    assert "Queue Control Proposal" in html
    assert 'action="/workers/proposals"' in html
    assert 'href="/workers/reflection"' in html
    assert 'href="/workers"' in html


def test_worker_operations_surface_redacts_private_rows_for_operator_and_owner_can_see_raw():
    config = WorkerOperationsSurfaceConfig(
        enabled=True,
        runs=[
            WorkerRunTelemetryRow(
                "run-private",
                "media",
                "failed",
                "dry_run",
                "09:31",
                error="raw private worker failure",
                href="/workers/raw-run",
                privacy_scope="owner_private",
                safe_alternate="safe worker failure",
                actions=[SurfaceAction("Open raw run", "/workers/raw-run")],
            )
        ],
        dead_letters=[
            WorkerDeadLetterRow(
                "dead-private",
                "media",
                "open",
                "provider",
                "raw private dead letter",
                href="/workers/raw-dead-letter",
                privacy_scope="owner_private",
                safe_alternate="safe dead letter",
            )
        ],
        dry_run_candidates=[
            WorkerDryRunCandidate(
                "dry-private",
                "self_learn",
                "capture",
                "reflection",
                "recorded",
                summary="raw private dry run",
                href="/workers/raw-dry-run",
                privacy_scope="owner_private",
                safe_alternate="safe dry run",
            )
        ],
        process_events=[
            WorkerProcessEvent(
                "event-private",
                "media",
                "dead_letter",
                "open",
                "raw private process event",
                href="/workers/raw-event",
                privacy_scope="owner_private",
                safe_alternate="safe process event",
            )
        ],
    )

    operator_html = render_worker_operations_surface(config, privacy_policy=_policy(), privacy_context=_operator())

    assert "safe worker failure" in operator_html
    assert "safe dead letter" in operator_html
    assert "safe dry run" in operator_html
    assert "safe process event" in operator_html
    assert "raw private" not in operator_html
    assert "/workers/raw-run" not in operator_html
    assert "/workers/raw-dead-letter" not in operator_html
    assert "/workers/raw-dry-run" not in operator_html
    assert "/workers/raw-event" not in operator_html

    owner_html = render_worker_operations_surface(config, privacy_policy=_policy(), privacy_context=_owner())

    assert "raw private worker failure" in owner_html
    assert "raw private dead letter" in owner_html
    assert "raw private dry run" in owner_html
    assert "raw private process event" in owner_html
    assert "/workers/raw-run" in owner_html


def test_worker_operations_feature_flags_and_empty_state():
    config = WorkerOperationsSurfaceConfig(enabled=True)

    assert worker_operations_surface_feature_enabled(config, {WORKER_OPERATIONS_FEATURE: True}) is True
    assert render_worker_operations_surface(config, features={WORKER_OPERATIONS_FEATURE: False}) == ""

    html = render_worker_operations_surface(config)

    assert "pc-worker-ops-surface" in html
    assert "No worker operation items configured." in html
