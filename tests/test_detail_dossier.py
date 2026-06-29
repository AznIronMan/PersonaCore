from personaconsole import (
    DETAIL_DOSSIER_FEATURE,
    AdminPrivacyContext,
    DetailDossierActionSlot,
    DetailDossierAuditRow,
    DetailDossierField,
    DetailDossierHeader,
    DetailDossierMetric,
    DetailDossierRelatedLink,
    DetailDossierSection,
    DetailDossierSourceTable,
    DetailDossierSurfaceConfig,
    DetailDossierTableCell,
    DetailDossierTableColumn,
    DetailDossierTableRow,
    DetailDossierTimelineEvent,
    OwnerPrivateScopePolicy,
    SurfaceAction,
    detail_dossier_surface_feature_enabled,
    render_detail_dossier_surface,
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


def _config() -> DetailDossierSurfaceConfig:
    return DetailDossierSurfaceConfig(
        enabled=True,
        key="example-detail",
        header=DetailDossierHeader(
            title="<Example Person>",
            subtitle="raw owner private header",
            entity_type="Person",
            status="active",
            tone="good",
            href="/people/example?x=<1>",
            initials="EP",
            badges=["profile"],
            actions=[SurfaceAction("Open source", "/source/example")],
            privacy_scope="owner_private",
            safe_alternate="safe header",
        ),
        fields=[
            DetailDossierField("handle", "Handle", "@example", href="/handles/example", mono=True),
            DetailDossierField("trust", "Trust", "operator", tone="good"),
            DetailDossierField(
                "private_note",
                "Private Note",
                "raw owner private dossier field",
                privacy_scope="owner_private",
                safe_alternate="safe dossier field",
                wide=True,
            ),
        ],
        metrics=[
            DetailDossierMetric("messages", "Messages", 12, "last 7 days", href="/messages?person=example"),
            DetailDossierMetric("risk", "Risk", "low", tone="good"),
        ],
        sections=[
            DetailDossierSection(
                "overview",
                "Overview",
                "Operator summary",
                body="<unsafe body>",
                fields=[DetailDossierField("source", "Source", "runtime")],
                badges=["section"],
            ),
            DetailDossierSection(
                "private-context",
                "Private Context",
                body="raw owner private section body",
                body_privacy_scope="owner_private",
                body_safe_alternate="safe section body",
            ),
        ],
        source_tables=[
            DetailDossierSourceTable(
                "source-rows",
                "Source Rows",
                columns=[
                    DetailDossierTableColumn("kind", "Kind"),
                    DetailDossierTableColumn("summary", "Summary"),
                    DetailDossierTableColumn("count", "Count", align="right"),
                ],
                rows=[
                    DetailDossierTableRow(
                        "row-1",
                        cells=[
                            DetailDossierTableCell("kind", "message", mono=True),
                            DetailDossierTableCell("summary", "<public source>", href="/source/1?x=<1>"),
                            DetailDossierTableCell("count", 3, numeric=True),
                        ],
                        actions=[SurfaceAction("Open", "/source/1")],
                    ),
                    DetailDossierTableRow(
                        "row-2",
                        cells=[
                            DetailDossierTableCell("kind", "private"),
                            DetailDossierTableCell(
                                "summary",
                                "raw owner private table summary",
                                href="/source/private-raw",
                                privacy_scope="owner_private",
                                safe_alternate="safe table summary",
                            ),
                            DetailDossierTableCell("count", 1, numeric=True),
                        ],
                    ),
                ],
            )
        ],
        timeline=[
            DetailDossierTimelineEvent("created", "Created", "09:00", "Profile created", actor="operator"),
            DetailDossierTimelineEvent(
                "private",
                "Private Event",
                "10:00",
                "raw owner private timeline summary",
                detail="raw owner private timeline detail",
                href="/timeline/private-raw",
                privacy_scope="owner_private",
                safe_alternate="safe timeline",
            ),
        ],
        related_links=[
            DetailDossierRelatedLink("messages", "Messages", "/messages?person=example", "12 rows", tone="info"),
        ],
        audit_rows=[
            DetailDossierAuditRow("updated", "Updated", "1m ago", actor="runtime"),
            DetailDossierAuditRow(
                "private-audit",
                "Private Audit",
                "raw owner private audit value",
                privacy_scope="owner_private",
                safe_alternate="safe audit value",
            ),
        ],
        action_slots=[
            DetailDossierActionSlot(
                "review",
                "Review Actions",
                body="<escaped action copy>",
                body_html='<form action="/review" method="post"><button>Queue</button></form>',
                actions=[SurfaceAction("History", "/review/history")],
            )
        ],
    )


def test_detail_dossier_surface_renders_generic_detail_contract():
    html = render_detail_dossier_surface(_config(), privacy_policy=_policy(), privacy_context=_operator())

    assert 'id="example-detail"' in html
    assert "pc-detail-dossier-surface" in html
    assert "safe header" in html
    assert "raw owner private header" not in html
    assert "/people/example?x=&lt;1&gt;" not in html
    assert "pc-detail-dossier-fields" in html
    assert "safe dossier field" in html
    assert "raw owner private dossier field" not in html
    assert "Messages" in html
    assert "pc-detail-dossier-section" in html
    assert "&lt;unsafe body&gt;" in html
    assert "safe section body" in html
    assert "pc-detail-dossier-table" in html
    assert "&lt;public source&gt;" in html
    assert "/source/1?x=&lt;1&gt;" in html
    assert "safe table summary" in html
    assert "/source/private-raw" not in html
    assert "safe timeline" in html
    assert "/timeline/private-raw" not in html
    assert "safe audit value" in html
    assert "&lt;escaped action copy&gt;" in html
    assert '<form action="/review" method="post"><button>Queue</button></form>' in html
    assert "raw owner private" not in html


def test_detail_dossier_owner_can_render_private_detail_and_links():
    html = render_detail_dossier_surface(_config(), privacy_policy=_policy(), privacy_context=_owner())

    assert "raw owner private header" in html
    assert "/people/example?x=&lt;1&gt;" in html
    assert "raw owner private table summary" in html
    assert "/source/private-raw" in html
    assert "raw owner private timeline summary" in html
    assert "/timeline/private-raw" in html
    assert "raw owner private audit value" in html


def test_detail_dossier_feature_flag_and_empty_states():
    config = DetailDossierSurfaceConfig(enabled=True, key="empty-detail")

    assert detail_dossier_surface_feature_enabled(config, features={DETAIL_DOSSIER_FEATURE: False}) is False
    assert render_detail_dossier_surface(config, features={DETAIL_DOSSIER_FEATURE: False}) == ""

    html = render_detail_dossier_surface(config)
    assert 'id="empty-detail"' in html
    assert "No detail data." in html
