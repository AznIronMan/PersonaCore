from html import escape
from urllib.parse import parse_qs, urlsplit

from personaconsole import (
    DiagnosticActionCard,
    DiagnosticTableColumn,
    FlashBanner,
    StatusTab,
    flash_query_params,
    flash_url,
    render_diagnostic_action_card,
    render_diagnostic_action_cards,
    render_diagnostic_table,
    render_flash_banners,
    render_sortable_diagnostic_table,
    render_status_tabs,
    render_surface_unavailable,
)


def test_status_tabs_render_legacy_and_personaconsole_classes():
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


def test_flash_banners_render_legacy_and_personaconsole_classes():
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


def test_diagnostic_action_cards_render_safe_legacy_markup():
    html = render_diagnostic_action_cards(
        [
            DiagnosticActionCard(
                "<Queue>",
                kicker="<diagnostic>",
                status="<warn>",
                summary="<Shared output>",
                href="/review?state=<pending>",
                tone="warning",
                pairs=[("<Rows>", "<7>")],
            ),
            {"title": "Plain", "tone": "success"},
        ]
    )

    assert 'class="action-card-list pc-diagnostic-card-list"' in html
    assert "pc-diagnostic-card-warn" in html
    assert "action-card-head" in html
    assert "&lt;Queue&gt;" in html
    assert "&lt;diagnostic&gt;" in html
    assert "&lt;Shared output&gt;" in html
    assert 'href="/review?state=&lt;pending&gt;"' in html
    assert "&lt;Rows&gt;" in html
    assert "&lt;7&gt;" in html
    assert "pc-diagnostic-card-good" in html


def test_surface_unavailable_uses_generic_public_safe_wording():
    html = render_surface_unavailable(
        "<Review>",
        status="<renderer unavailable>",
        summary="<Runtime-owned diagnostics>",
        pairs=[{"label": "<Rows>", "value": "2"}],
    )

    assert "pc-diagnostic-card" in html
    assert "&lt;Review&gt;" in html
    assert "&lt;renderer unavailable&gt;" in html
    assert "&lt;Runtime-owned diagnostics&gt;" in html
    assert "PersonaConsole" not in html


def test_diagnostic_table_renders_safe_cells_and_empty_state():
    html = render_diagnostic_table(
        [{"name": "<Item>", "count": 3}],
        [DiagnosticTableColumn("name", "Name"), "count"],
    )

    assert 'class="table-wrap"' in html
    assert 'class="compact-table"' in html
    assert "<th>Name</th>" in html
    assert "<th>count</th>" in html
    assert "&lt;Item&gt;" in html
    assert "<td>3</td>" in html

    empty = render_diagnostic_table([], ["name"], empty_label="<No rows>")
    assert "pc-diagnostic-empty" in empty
    assert "&lt;No rows&gt;" in empty


def test_sortable_diagnostic_table_supports_links_classes_and_custom_renderer():
    html = render_sortable_diagnostic_table(
        [{"name": "<Item>", "count": 3, "ok": True}],
        [("name", "Name"), ("count", "Count"), ("ok", "OK")],
        sortable_columns=("name", "count"),
        sort_key="name",
        direction="asc",
        sort_href_builder=lambda key, direction: f"/items?sort={key}&direction={direction}",
        link_columns={"name": lambda row: "/items/1?name=<item>"},
        numeric_columns=("count",),
        boolean_columns=("ok",),
        primary_columns=("name",),
        cell_renderer=lambda value, _row, _key: f"[{escape(str(value))}]",
    )

    assert 'class="list-table"' in html
    assert 'href="/items?sort=name&amp;direction=desc"' in html
    assert "sort-marker" in html
    assert 'href="/items/1?name=&lt;item&gt;"' in html
    assert 'class="row-primary"' in html
    assert 'class="numeric"' in html
    assert 'class="boolean"' in html
    assert "[&lt;Item&gt;]" in html
