from personaconsole import (
    ADMIN_LIST_FEATURE,
    AdminListCell,
    AdminListColumn,
    AdminListFilterField,
    AdminListPagination,
    AdminListRow,
    AdminListSurfaceConfig,
    AdminPrivacyContext,
    DashboardFilter,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    StatusTab,
    SurfaceAction,
    admin_list_surface_feature_enabled,
    render_admin_list_surface,
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


def _config() -> AdminListSurfaceConfig:
    return AdminListSurfaceConfig(
        enabled=True,
        key="example-list",
        title="<Shared List>",
        subtitle="Generic runtime rows",
        columns=[
            AdminListColumn("name", "Name", href="/items?sort=name&dir=asc", sortable=True, active=True, direction="asc"),
            AdminListColumn("status", "Status", align="center"),
            AdminListColumn("summary", "Summary"),
            AdminListColumn("updated", "Updated", align="right", hidden_mobile=True),
        ],
        status_tabs=[
            StatusTab("All", "/items", 2, active=True),
            StatusTab("Held", "/items?status=held", 1, tone="warn"),
        ],
        filters=[
            DashboardFilter("Ready", "/items?status=ready", key="ready", active=True),
        ],
        filter_fields=[
            AdminListFilterField("q", "Search", "<needle>", "search", placeholder="Find rows"),
            AdminListFilterField("status", "Status", "ready", "select", options=["ready", "held"]),
            AdminListFilterField("needs_review", "Needs review", True, "checkbox"),
        ],
        filter_action="/items",
        reset_href="/items/reset",
        metrics=[
            DashboardMetric("Visible", 2, "/items", "active filter", tone="good"),
        ],
        actions=[SurfaceAction("New row", "/items/new", "good")],
        rows=[
            AdminListRow(
                "public",
                cells=[
                    AdminListCell("name", "<Example row>", href="/items/public?x=<1>"),
                    AdminListCell("status", "ready", tone="good", badges=["configured"]),
                    AdminListCell("summary", "Public summary"),
                    AdminListCell("updated", "1m ago", mono=True, nowrap=True),
                ],
                actions=[SurfaceAction("Open", "/items/public")],
                badges=["sample"],
            ),
            AdminListRow(
                "private",
                cells=[
                    AdminListCell("name", "Private row"),
                    AdminListCell("status", "held", tone="warn"),
                    AdminListCell(
                        "summary",
                        "raw owner private admin-list summary",
                        href="/items/private-raw",
                        privacy_scope="owner_private",
                        safe_alternate="safe admin-list summary",
                    ),
                    AdminListCell("updated", "2m ago", mono=True, nowrap=True),
                ],
                summary="raw owner private card summary",
                summary_privacy_scope="owner_private",
                summary_safe_alternate="safe card summary",
            ),
        ],
        pagination=AdminListPagination(count=2, page=1, page_count=1, previous_href="", next_href="/items?page=2"),
        mobile_card_primary_key="name",
        mobile_card_secondary_key="status",
    )


def test_admin_list_surface_renders_generic_table_controls_and_cards():
    html = render_admin_list_surface(_config(), privacy_policy=_policy(), privacy_context=_operator())

    assert 'id="example-list"' in html
    assert "pc-admin-list-surface" in html
    assert "&lt;Shared List&gt;" in html
    assert "pc-status-tabs" in html
    assert "pc-admin-list-filter-form" in html
    assert 'value="&lt;needle&gt;"' in html
    assert "<option value=\"ready\" selected>ready</option>" in html
    assert "pc-admin-list-table" in html
    assert "pc-admin-list-cards" in html
    assert "/items?sort=name&amp;dir=asc" in html
    assert "/items/public?x=&lt;1&gt;" in html
    assert "&lt;Example row&gt;" in html
    assert "configured" in html
    assert "safe admin-list summary" in html
    assert "safe card summary" in html
    assert "raw owner private admin-list summary" not in html
    assert "raw owner private card summary" not in html
    assert "/items/private-raw" not in html
    assert "Page 1 of 1" in html


def test_admin_list_owner_can_see_raw_private_cell_and_href():
    html = render_admin_list_surface(_config(), privacy_policy=_policy(), privacy_context=_owner())

    assert "raw owner private admin-list summary" in html
    assert "safe admin-list summary" not in html
    assert "/items/private-raw" in html


def test_admin_list_fails_closed_without_policy():
    html = render_admin_list_surface(
        AdminListSurfaceConfig(
            enabled=True,
            columns=[AdminListColumn("summary", "Summary")],
            rows=[
                AdminListRow(
                    "private",
                    cells=[
                        AdminListCell(
                            "summary",
                            "raw private value",
                            privacy_scope="owner_private",
                        )
                    ],
                )
            ],
        )
    )

    assert "[owner-private content withheld]" in html
    assert "raw private value" not in html


def test_admin_list_feature_gate_and_empty_state():
    config = AdminListSurfaceConfig(enabled=True, columns=[AdminListColumn("name", "Name")])

    assert admin_list_surface_feature_enabled(config, {ADMIN_LIST_FEATURE: True}) is True
    assert admin_list_surface_feature_enabled(config, {ADMIN_LIST_FEATURE: False}) is False
    assert render_admin_list_surface(config, features={ADMIN_LIST_FEATURE: False}) == ""

    html = render_admin_list_surface(config)
    assert "No rows found." in html
