from persona_console import StatusTab, render_status_tabs


def test_status_tabs_render_legacy_and_personacore_classes():
    html = render_status_tabs(
        [
            StatusTab("All", "/review", 12, active=True),
            {"label": "Pending", "href": "/review?status=pending", "count": 3, "tone": "warn"},
            StatusTab("<Done>", "/review?status=<done>", 0, title="<done state>"),
        ],
        aria_label="<Review status>",
    )

    assert 'class="status-tabs pc-status-tabs"' in html
    assert 'aria-label="&lt;Review status&gt;"' in html
    assert html.count("pc-status-tab") >= 3
    assert 'class="status-tab pc-status-tab pc-status-tab-neutral is-active"' in html
    assert 'class="status-tab-count pc-status-tab-count">12</span>' in html
    assert "/review?status=pending" in html
    assert "Pending" in html
    assert "&lt;Done&gt;" in html
    assert 'href="/review?status=&lt;done&gt;"' in html
    assert 'title="&lt;done state&gt;"' in html


def test_status_tabs_empty_without_label_returns_empty_string():
    assert render_status_tabs([]) == ""

    html = render_status_tabs([], empty_label="No filters")
    assert "No filters" in html
    assert "pc-status-tabs" in html
