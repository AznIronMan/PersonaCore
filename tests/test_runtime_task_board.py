from personaconsole import (
    RUNTIME_TASK_BOARD_FEATURE,
    AdminListPagination,
    AdminPrivacyContext,
    DashboardFilter,
    DashboardMetric,
    LiveRefreshConfig,
    OwnerPrivateScopePolicy,
    RuntimeTaskActionSlot,
    RuntimeTaskBoardSurfaceConfig,
    RuntimeTaskHistoryRow,
    RuntimeTaskLinkedRecord,
    RuntimeTaskRow,
    StatusTab,
    SurfaceAction,
    runtime_task_board_feature_enabled,
    render_runtime_task_board_surface,
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


def _private_task() -> RuntimeTaskRow:
    return RuntimeTaskRow(
        "private-task",
        "raw private task title",
        "blocked",
        "bad",
        "high",
        "critical",
        "operator",
        "today",
        "09:10",
        "raw private task summary",
        "/tasks/raw-private",
        detail="raw private task detail",
        privacy_scope="owner_private",
        safe_alternate="safe task summary",
        linked_records=[
            RuntimeTaskLinkedRecord(
                "private-record",
                "Private record",
                "issue",
                "held",
                "warn",
                "/tasks/raw-private-record",
                "raw private linked record",
                privacy_scope="owner_private",
                safe_alternate="safe linked record",
            )
        ],
        history=[
            RuntimeTaskHistoryRow(
                "private-history",
                "Private update",
                "held",
                "warn",
                "operator",
                "09:15",
                "raw private task history",
                "/tasks/raw-private-history",
                privacy_scope="owner_private",
                safe_alternate="safe task history",
            )
        ],
        actions=[SurfaceAction("Escalate", "", "warn", disabled=True)],
    )


def _config() -> RuntimeTaskBoardSurfaceConfig:
    selected = RuntimeTaskRow(
        "selected",
        "Review profile migration",
        "review",
        "warn",
        "medium",
        "normal",
        "operator",
        "tomorrow",
        "09:00",
        "Confirm the shared surface migration path.",
        "/tasks/selected",
        "Task Detail",
        "Selected task detail.",
        linked_records=[RuntimeTaskLinkedRecord("surface", "Shared surface", "route", "ready", "good", "/tasks/surface", "Route ready.")],
        history=[RuntimeTaskHistoryRow("created", "Created", "open", "info", "operator", "08:00", "Task opened.")],
        actions=[SurfaceAction("Mark reviewed", "/tasks/selected/reviewed", "good", method="post")],
    )
    return RuntimeTaskBoardSurfaceConfig(
        enabled=True,
        title="Runtime Task Board",
        subtitle="Adapter-fed task status, detail, and history.",
        status="stale",
        status_tone="warn",
        tabs=[
            StatusTab("All", "/tasks", 3, active=True),
            StatusTab("Blocked", "/tasks?status=blocked", 1, tone="bad"),
        ],
        filters=[
            DashboardFilter("Mine", "/tasks?owner=operator", "owner", active=True),
            DashboardFilter("High", "/tasks?priority=high", "priority"),
        ],
        metrics=[DashboardMetric("Open", "3", detail="1 blocked", tone="warn")],
        tasks=[
            RuntimeTaskRow(
                "profile",
                "Review profile migration",
                "review",
                "warn",
                "medium",
                "normal",
                "operator",
                "tomorrow",
                "09:00",
                "Confirm the shared surface migration path.",
                "/tasks/profile",
                actions=[SurfaceAction("Open task", "/tasks/profile")],
            ),
            _private_task(),
        ],
        selected_task=selected,
        pagination=AdminListPagination(count=2, page=1, page_count=1, summary="Showing 2 runtime tasks"),
        live_refresh=LiveRefreshConfig(enabled=True, key="tasks", url="/fragments/tasks", target_id="runtime-task-board"),
        action_slots=[
            RuntimeTaskActionSlot(
                "handoff",
                "Runtime-owned update",
                "Consumer endpoint owns mutation.",
                '<form action="/tasks/update" method="post"></form>',
                "info",
                actions=[SurfaceAction("Disabled update", "", "warn", disabled=True)],
            )
        ],
        actions=[SurfaceAction("Refresh tasks", "/tasks/refresh", "info", method="post")],
    )


def test_runtime_task_board_renders_filters_detail_slots_and_redacts_private_values():
    html = render_runtime_task_board_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-runtime-task-board-surface" in html
    assert "Runtime Task Board" in html
    assert "Review profile migration" in html
    assert "Mine" in html
    assert "Open" in html
    assert "Showing 2 runtime tasks" in html
    assert "Task Detail" in html
    assert "Shared surface" in html
    assert "Task opened." in html
    assert "Runtime-owned update" in html
    assert 'action="/tasks/update"' in html
    assert "data-pc-live-controls" in html
    assert "safe task summary" in html
    assert "Escalate" in html
    assert 'aria-disabled="true"' in html
    assert "raw private task" not in html
    assert "raw private linked record" not in html
    assert "raw private task history" not in html
    assert "/tasks/raw-private" not in html


def test_runtime_task_board_owner_can_see_private_values_and_links():
    html = render_runtime_task_board_surface(
        RuntimeTaskBoardSurfaceConfig(enabled=True, tasks=[_private_task()], selected_task=_private_task()),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private task title" in html
    assert "raw private task summary" in html
    assert "raw private task detail" in html
    assert "raw private linked record" in html
    assert "raw private task history" in html
    assert "/tasks/raw-private" in html
    assert "safe task summary" not in html


def test_runtime_task_board_feature_gate_and_empty_state():
    config = RuntimeTaskBoardSurfaceConfig(enabled=True)

    assert runtime_task_board_feature_enabled(config, {RUNTIME_TASK_BOARD_FEATURE: True}) is True
    assert runtime_task_board_feature_enabled(config, {RUNTIME_TASK_BOARD_FEATURE: False}) is False
    assert render_runtime_task_board_surface(config, features={RUNTIME_TASK_BOARD_FEATURE: False}) == ""

    html = render_runtime_task_board_surface(config)

    assert "No runtime tasks configured." in html
