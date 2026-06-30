from personaconsole import (
    JOURNAL_FEATURE,
    JOURNAL_THEME_KEYS,
    AdminPrivacyContext,
    JournalCalendarDay,
    JournalDetail,
    JournalEntry,
    JournalMarker,
    JournalSurfaceConfig,
    OwnerPrivateScopePolicy,
    SurfaceAction,
    build_journal_calendar,
    journal_surface_feature_enabled,
    journal_theme_key,
    journal_theme_options,
    render_journal_surface,
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


def _entry() -> JournalEntry:
    return JournalEntry(
        "private",
        "2026-06-24",
        "raw private title",
        "raw private first paragraph\n\nraw private second paragraph",
        href="/journal/private",
        subtitle="raw private subtitle",
        author_label="example-persona",
        privacy_label="owner-private",
        timestamp="21:40",
        previous_href="/journal/private-prev",
        next_href="/journal/private-next",
        details=[
            JournalDetail("Source", "raw private source"),
            JournalDetail("Confidence", "0.92", "good"),
        ],
        markers=[JournalMarker("<focused>", "good")],
        actions=[SurfaceAction("Open raw", "/journal/raw", method="post")],
        privacy_scope="owner_private",
        safe_alternate="operator-safe journal page",
    )


def test_journal_surface_renders_calendar_theme_and_redacts_private_entry_for_operator():
    calendar = [
        JournalCalendarDay("2026-06-23", 23, href="/journal?date=2026-06-23", has_entry=True),
        JournalCalendarDay(
            "2026-06-24",
            24,
            href="/journal/private",
            has_entry=True,
            selected=True,
            markers=["private"],
            privacy_scope="owner_private",
        ),
    ]

    html = render_journal_surface(
        JournalSurfaceConfig(
            enabled=True,
            title="<Journal>",
            month_label="2026-06",
            previous_month_href="/journal?month=2026-05",
            next_month_href="/journal?month=2026-07",
            calendar=calendar,
            entry=_entry(),
            theme="matrix",
            theme_options=["paper", "matrix", {"key": "night-ink", "href": "/settings?theme=night-ink"}],
        ),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert 'id="journal"' in html
    assert "pc-journal-theme-matrix" in html
    assert "&lt;Journal&gt;" in html
    assert "2026-06" in html
    assert "/journal?month=2026-05" in html
    assert "pc-journal-calendar-day has-entry is-selected" in html
    assert "operator-safe journal page" in html
    assert "raw private" not in html
    assert "/journal/private" not in html
    assert "/journal/private-prev" not in html
    assert "Source And Provenance" not in html
    assert "/journal/raw" not in html
    assert "&lt;focused&gt;" in html


def test_journal_surface_owner_can_see_raw_private_entry_links_and_details():
    html = render_journal_surface(
        JournalSurfaceConfig(enabled=True, month_label="2026-06", entry=_entry()),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private title" in html
    assert "raw private first paragraph" in html
    assert "/journal/private-prev" in html
    assert "/journal/private-next" in html
    assert "Source And Provenance" in html
    assert "raw private source" in html
    assert 'data-method="POST"' in html
    assert "/journal/raw" in html
    assert "operator-safe journal page" not in html


def test_journal_calendar_helper_builds_six_week_month_grid():
    days = build_journal_calendar(
        "2026-06",
        ["2026-06-01", {"date": "2026-06-24"}, JournalEntry("e", "2026-06-30", "End")],
        selected_date="2026-06-24",
        href_template="/journal?date={date}",
    )

    assert len(days) == 42
    assert days[0].date == "2026-06-01"
    assert days[-1].date == "2026-07-12"
    selected = next(day for day in days if day.date == "2026-06-24")
    assert selected.has_entry is True
    assert selected.selected is True
    assert selected.href == "/journal?date=2026-06-24"
    assert next(day for day in days if day.date == "2026-07-01").in_month is False


def test_journal_theme_catalog_and_feature_flags():
    config = JournalSurfaceConfig(enabled=True, month_label="2026-06")

    assert len(JOURNAL_THEME_KEYS) == 12
    assert journal_theme_key("not-real") == "paper"
    assert len(journal_theme_options("night-ink")) == 12
    assert any(option.key == "night-ink" and option.selected for option in journal_theme_options("night-ink"))
    assert journal_surface_feature_enabled(config, {JOURNAL_FEATURE: True}) is True
    assert render_journal_surface(config, features={JOURNAL_FEATURE: False}) == ""
    assert "No journal entry selected." in render_journal_surface(config)
    assert "pc-journal-theme-paper" in render_journal_surface(JournalSurfaceConfig(enabled=True, theme="bad-theme"))
