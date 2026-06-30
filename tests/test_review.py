from personaconsole import (
    REVIEW_FEATURE,
    AdminPrivacyContext,
    DashboardAction,
    DashboardFilter,
    DashboardMetric,
    OwnerPrivateScopePolicy,
    ReviewAgendaItem,
    ReviewBoardRow,
    ReviewQueueCard,
    ReviewQueueSection,
    ReviewSurfaceConfig,
    render_review_surface,
    review_surface_feature_enabled,
)


def _policy() -> OwnerPrivateScopePolicy:
    return OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})


def _owner() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="owner_private",
        viewer_person_key="owner",
        allowed_scopes=("public", "operator", "owner_private"),
    )


def _operator() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )


def _review_config() -> ReviewSurfaceConfig:
    return ReviewSurfaceConfig(
        enabled=True,
        title="<Review>",
        subtitle="Operator gates",
        filters=[
            DashboardFilter("<All>", "/review?kind=<all>", key="8", active=True),
            {"label": "Media", "href": "/review?kind=media", "key": "1"},
        ],
        metrics=[
            DashboardMetric("Pending", 8, "/review?status=pending", "needs review", tone="warn"),
            DashboardMetric("Failed", 1, "/review?status=failed", "attention", tone="bad"),
        ],
        actions=[DashboardAction("Proposals", "/persona/proposals?status=<pending>", tone="info")],
        rows=[
            ReviewBoardRow(
                kind="<proposal>",
                status="pending",
                risk="warn",
                entity="persona:<state>",
                actor="<operator>",
                age="1h ago",
                summary="safe public summary",
                href="/persona/proposals?target=<state>",
                badges=["review"],
            ),
            ReviewBoardRow(
                kind="message",
                status="held",
                risk="bad",
                entity="messages:private",
                actor="runtime",
                age="now",
                summary="raw owner-private review summary",
                summary_safe_alternate="operator-safe review summary",
                summary_privacy_scope="owner_private",
                href="/messages/raw-private-review",
            ),
        ],
        agenda=[
            ReviewAgendaItem("Persona proposals", 3, "/persona/proposals", "review queue", "Inspect diffs", "warn"),
            {"label": "Media", "value": "1", "href": "/review/media", "category": "drafts", "summary": "Review assets"},
        ],
        queue_sections=[
            ReviewQueueSection(
                "Publishing Queues",
                "safe summaries",
                cards=[
                    ReviewQueueCard(
                        "<Draft Post>",
                        status="draft",
                        href="/review/social?q=<post>",
                        category="social",
                        summary="post summary",
                        meta=[("Key", "post-1"), {"label": "Source", "value": "operator"}],
                    ),
                    ReviewQueueCard(
                        "Private queue",
                        status="pending",
                        href="/review/private-queue",
                        category="dm",
                        summary="raw owner-private queue summary",
                        summary_safe_alternate="operator-safe queue summary",
                        summary_privacy_scope="owner_private",
                    ),
                ],
            )
        ],
    )


def test_review_surface_renders_reference_board_and_escapes_data():
    html = render_review_surface(_review_config(), privacy_policy=_policy(), privacy_context=_operator())

    assert 'id="review"' in html
    assert "pc-review-surface" in html
    assert "&lt;Review&gt;" in html
    assert "/review?kind=&lt;all&gt;" in html
    assert "/persona/proposals?status=&lt;pending&gt;" in html
    assert "Decision Board" in html
    assert "Review Agenda" in html
    assert "Publishing Queues" in html
    assert "persona:&lt;state&gt;" in html
    assert "operator-safe review summary" in html
    assert "operator-safe queue summary" in html
    assert "raw owner-private" not in html
    assert "/messages/raw-private-review" not in html
    assert "/review/private-queue" not in html


def test_review_surface_owner_can_see_raw_private_rows_and_links():
    html = render_review_surface(_review_config(), privacy_policy=_policy(), privacy_context=_owner())

    assert "raw owner-private review summary" in html
    assert "raw owner-private queue summary" in html
    assert "/messages/raw-private-review" in html
    assert "/review/private-queue" in html
    assert "operator-safe review summary" not in html


def test_review_surface_feature_flag_and_empty_state():
    config = ReviewSurfaceConfig(enabled=True)

    assert review_surface_feature_enabled(config, {REVIEW_FEATURE: True}) is True
    assert render_review_surface(config, features={REVIEW_FEATURE: False}) == ""

    html = render_review_surface(config)
    assert "No decision rows found." in html
