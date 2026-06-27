from urllib.parse import parse_qs, urlsplit

from persona_console import FlashBanner, flash_query_params, flash_url, render_flash_banners, StatusTab, render_status_tabs


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


def test_flash_banners_render_legacy_and_personacore_classes():
    html = render_flash_banners(
        [
            FlashBanner(
                "<Saved>",
                tone="success",
                title="<safe title>",
                action_label="Open <item>",
                action_href="/items?status=<saved>",
            ),
            {"message": "Review queued", "tone": "warning", "dismissible": False},
            "Plain update",
        ],
    )

    assert 'class="flash-stack pc-flash-stack"' in html
    assert 'aria-live="polite"' in html
    assert html.count("pc-flash-banner") == 3
    assert 'class="flash-banner pc-flash-banner flash-good pc-flash-good"' in html
    assert 'title="&lt;safe title&gt;"' in html
    assert "&lt;Saved&gt;" in html
    assert 'class="flash-action pc-flash-action"' in html
    assert 'href="/items?status=&lt;saved&gt;"' in html
    assert "Open &lt;item&gt;" in html
    assert 'class="flash-dismiss pc-flash-dismiss" data-dismiss-flash' in html
    assert "flash-warn" in html
    assert "Plain update" in html


def test_flash_url_preserves_query_fragment_and_replaces_existing_flash():
    url = flash_url(
        "/review?tab=all&flash=old&flash_level=bad#queue",
        "Saved item",
        level="warning",
        timestamp=42,
    )
    parsed = urlsplit(url)
    query = parse_qs(parsed.query)

    assert parsed.path == "/review"
    assert parsed.fragment == "queue"
    assert query["tab"] == ["all"]
    assert query["flash"] == ["Saved item"]
    assert query["flash_level"] == ["warn"]
    assert query["flash_ts"] == ["42"]


def test_flash_query_params_sanitizes_level():
    params = flash_query_params("Done", level="not-a-level", timestamp=7)

    assert params == {"flash": "Done", "flash_level": "neutral", "flash_ts": "7"}
