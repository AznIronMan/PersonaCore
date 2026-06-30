from personaconsole import (
    LiveRefreshConfig,
    NavGroup,
    NavItem,
    PersonaConsoleConfig,
    StatusPill,
    UserPill,
    active_nav_label,
    live_refresh_attributes,
    render_live_controls,
    render_live_region,
    render_live_status,
    render_nav_groups,
    render_shell_html,
    render_status_pill,
    render_user_pill,
)


def test_nav_renders_active_item_and_badge():
    html = render_nav_groups(
        [
            NavGroup(
                "Review",
                [
                    NavItem("Inbox", "/review", active="review", badge="review"),
                    NavItem("Done", "/done", active="done"),
                ],
                key="review-group",
            )
        ],
        active="review",
        badges={"review": 3},
    )

    assert "admin-nav-summary is-active" in html
    assert 'href="/review"' in html
    assert ">3</span>" in html


def test_shell_escapes_config_text_and_includes_assets():
    html = render_shell_html(
        PersonaConsoleConfig(
            brand_name="<Persona>",
            page_title="Dashboard",
            page_subtitle="<unsafe>",
            active="dashboard",
            nav_groups=[{"label": "Core", "items": [{"label": "Dashboard", "href": "/", "active": "dashboard"}]}],
            status_pills=[StatusPill("ok", "good")],
        ),
        "<section>body is trusted html</section>",
    )

    assert "&lt;Persona&gt;" in html
    assert "&lt;unsafe&gt;" in html
    assert "persona-console.css" in html
    assert "persona-console.js" in html
    assert "<section>body is trusted html</section>" in html


def test_active_nav_label_falls_back_to_humanized_active_key():
    assert active_nav_label([], "worker_queue") == "Worker Queue"


def test_nav_matches_current_path_and_renders_external_large_badge():
    html = render_nav_groups(
        [
            {
                "label": "Operations",
                "items": [
                    {"label": "Workers", "href": "/workers", "badge": 1000, "external": True},
                    {"label": "Review", "href": "/review", "badge": -4},
                ],
            }
        ],
        active="missing",
        current_path="/workers/retries",
    )

    assert 'href="/workers" target="_blank" rel="noopener noreferrer"' in html
    assert "admin-nav-item is-active" in html
    assert ">999+</span>" in html
    assert ">-4</span>" not in html


def test_nav_accepts_numeric_string_badges_and_missing_badge_map():
    html = render_nav_groups(
        [{"label": "Core", "items": [{"label": "Messages", "href": "/messages", "badge": "7"}]}],
        active="messages",
    )

    assert ">7</span>" in html


def test_status_pill_sanitizes_tone_title_and_label():
    html = render_status_pill({"label": "<ready>", "tone": "unknown", "title": 'state "raw"'})

    assert "status-neutral" in html
    assert "&lt;ready&gt;" in html
    assert "state &quot;raw&quot;" in html


def test_user_pill_uses_fallback_initials_and_escapes_text():
    html = render_user_pill(UserPill(display_name="<Example Operator>", tier="admin", source="fixture"))

    assert "&lt;Example Operator&gt;" in html
    assert ">EO</span>" in html
    assert "admin" in html
    assert "fixture" in html


def test_live_controls_render_only_when_configured():
    disabled = PersonaConsoleConfig(brand_name="Example", page_title="Dashboard")
    enabled = PersonaConsoleConfig(brand_name="Example", page_title="Dashboard", active="workers", live_interval=15)

    assert render_live_controls(disabled) == ""
    assert 'data-default-interval="15"' in render_live_controls(enabled)
    assert 'data-storage-key="live:workers"' in render_live_controls(enabled)
    assert 'class="live-pill pc-live-pill"' in render_live_controls(enabled)
    assert "data-pc-live-controls" in render_live_controls(enabled)
    assert "data-pc-live-toggle" in render_live_controls(enabled)


def test_live_refresh_helpers_render_partial_contract_and_no_js_fallback():
    config = LiveRefreshConfig(
        enabled=True,
        key="<review>",
        url="/fragments/review?q=<unsafe>",
        interval_seconds=20,
        interval_options=(10, 20),
        target_id="review target",
        controls_id="review controls",
        status_id="review status",
        hold_selector="[data-live-hold]",
        stale_after_seconds=45,
        paused=True,
        fallback_href="/review",
    )

    attrs = live_refresh_attributes(config)
    controls = render_live_controls(config)
    region = render_live_region("<section>trusted partial</section>", config)
    status = render_live_status(config)

    assert 'id="review-target"' in attrs
    assert 'data-pc-live-key="review"' in attrs
    assert 'data-pc-live-url="/fragments/review?q=&lt;unsafe&gt;"' in attrs
    assert 'data-pc-live-hold-when="[data-live-hold]"' in attrs
    assert 'data-pc-live-stale-after="45"' in attrs
    assert 'id="review-controls"' in controls
    assert 'data-pc-live-for="#review-target"' in controls
    assert 'data-pc-live-paused="true"' in controls
    assert 'aria-pressed="false"' in controls
    assert '<option value="20" selected>20s</option>' in controls
    assert 'class="pc-live-noscript"' in controls
    assert '<div id="review-target"' in region
    assert "<section>trusted partial</section>" in region
    assert 'id="review-status"' in status


def test_shell_normalizes_static_url_and_live_target_attributes():
    html = render_shell_html(
        PersonaConsoleConfig(
            brand_name="Example",
            page_title="Dashboard",
            static_base_url="/assets/",
            live_url="/fragments/dashboard",
            live_interval=30,
            live_hold_selector="[data-live-hold]",
            legacy_refresh_global="bad-name();alert",
        ),
        "<section>body</section>",
    )

    assert 'href="/assets/persona-console.css"' in html
    assert 'src="/assets/persona-console.js"' in html
    assert 'id="live-target"' in html
    assert 'data-pc-live-target' in html
    assert 'data-pc-live-url="/fragments/dashboard"' in html
    assert 'data-live-url="/fragments/dashboard"' in html
    assert 'data-live-hold-when="[data-live-hold]"' in html
    assert 'data-pc-live-manual' in html
    assert 'class="flash-stack pc-flash-stack"' in html
    assert 'class="page-refresh-button pc-page-refresh-button"' in html
    assert "window.badnamealert = function" in html


def test_shell_accepts_explicit_live_refresh_config_mapping():
    html = render_shell_html(
        PersonaConsoleConfig(
            brand_name="Example",
            page_title="Review",
            live_refresh={
                "enabled": True,
                "key": "review",
                "endpoint": "/fragments/review",
                "target_id": "review-fragment",
                "controls_id": "review-live",
                "status_id": "review-status",
                "interval": 10,
                "interval_options": [10, 30],
                "stale_after": 90,
                "paused": True,
                "fallback_href": "/review",
            },
        ),
        "<section>review partial</section>",
    )

    assert 'id="review-fragment"' in html
    assert 'data-pc-live-url="/fragments/review"' in html
    assert 'data-pc-live-stale-after="90"' in html
    assert 'id="review-live"' in html
    assert 'id="review-status"' in html
    assert 'aria-pressed="false"' in html
    assert 'href="/review"' in html
