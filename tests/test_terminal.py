from personaconsole import (
    TERMINAL_STREAM_FEATURE,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    TerminalStreamConfig,
    TerminalStreamEvent,
    render_terminal_stream,
    terminal_stream_feature_enabled,
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


def test_terminal_stream_renders_current_bounded_window_with_history_and_live_cursors():
    html = render_terminal_stream(
        TerminalStreamConfig(
            enabled=True,
            title="<Terminal>",
            subtitle="Read-only current window",
            status="streaming",
            status_tone="good",
            window_label="Latest event window",
            before_cursor="before-1",
            after_cursor="after-4",
            history_url="/agent/events/history",
            stream_url="/agent/events/live",
            max_rendered_events=3,
            has_more_before=True,
            events=[
                TerminalStreamEvent("evt-1", "old event"),
                TerminalStreamEvent("evt-2", "command <safe>", role="cmd", label="input", sequence=2),
                TerminalStreamEvent("evt-3", "tool output", role="tool", sequence=3),
                TerminalStreamEvent("evt-4", "latest event", role="stdout", sequence=4),
            ],
        )
    )

    assert "pc-terminal-stream" in html
    assert 'data-readonly="true"' in html
    assert 'data-history-url="/agent/events/history"' in html
    assert 'data-stream-url="/agent/events/live"' in html
    assert 'data-before-cursor="before-1"' in html
    assert 'data-after-cursor="after-4"' in html
    assert 'data-max-events="3"' in html
    assert "older history is buffered" in html
    assert "Load earlier" in html
    assert "&lt;Terminal&gt;" in html
    assert "old event" not in html
    assert "command &lt;safe&gt;" in html
    assert "tool output" in html
    assert "latest event" in html
    assert "pc-terminal-role-input" in html
    assert "pc-terminal-role-tool" in html


def test_terminal_stream_redacts_private_events_for_operators_and_raw_for_owner():
    config = TerminalStreamConfig(
        enabled=True,
        events=[
            TerminalStreamEvent(
                "private-terminal",
                "raw private terminal output",
                privacy_scope="owner_private",
                safe_alternate="safe terminal summary",
            )
        ],
    )

    operator_html = render_terminal_stream(
        config,
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )
    owner_html = render_terminal_stream(
        config,
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "safe terminal summary" in operator_html
    assert "raw private terminal output" not in operator_html
    assert "raw private terminal output" in owner_html
    assert "safe terminal summary" not in owner_html


def test_terminal_stream_feature_gate_and_empty_state():
    config = TerminalStreamConfig(enabled=True)

    assert terminal_stream_feature_enabled(config, {TERMINAL_STREAM_FEATURE: True}) is True
    assert terminal_stream_feature_enabled(config, {TERMINAL_STREAM_FEATURE: False}) is False
    assert render_terminal_stream(config, features={TERMINAL_STREAM_FEATURE: False}) == ""

    html = render_terminal_stream(config)

    assert "No terminal events in the current window." in html
