from personaconsole import (
    PEOPLE_FEATURE,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    PeopleSurfaceConfig,
    PersonListRow,
    PersonRelationshipSummary,
    PersonTag,
    people_surface_feature_enabled,
    render_people_surface,
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


def _people_config() -> PeopleSurfaceConfig:
    return PeopleSurfaceConfig(
        enabled=True,
        title="<People>",
        subtitle="Canonical people",
        search_action="/people",
        search_value="<needle>",
        sort="updated",
        direction="desc",
        reset_href="/people/reset",
        new_person_html='<p class="hint">Consumer-owned form slot</p>',
        rows=[
            PersonListRow(
                key="person-1",
                label="<Example Consumer>",
                href="/people/person-1?x=<1>",
                subtitle='id 301 - "consumer"',
                external_id="CN0001",
                trust_label="internal",
                trust_tone="info",
                linked_users=4,
                tags=[PersonTag("<supportive>", tone="good"), {"label": "review", "tone": "warn"}],
                relationship=PersonRelationshipSummary(
                    label="Persona",
                    score="+54",
                    tone="good",
                    score_percent=78,
                    lanes=[PersonTag("trusted", tone="info")],
                    labels=[PersonTag("friend", tone="good")],
                ),
                notes="Public note summary",
                updated="1h ago",
            ),
            {
                "key": "owner-private",
                "label": "Owner Private",
                "external_id": "INT-OWNER",
                "trust_label": "owner-private",
                "trust_tone": "warn",
                "linked_users": 1,
                "notes": "raw owner-private people note",
                "notes_safe_alternate": "operator-safe people summary",
                "notes_privacy_scope": "owner_private",
                "updated": "2h ago",
                "unlinked": True,
            },
        ],
    )


def test_people_surface_renders_reference_style_table_with_escaped_data():
    html = render_people_surface(_people_config(), privacy_policy=_policy(), privacy_context=_operator())

    assert 'id="people"' in html
    assert "pc-people-surface" in html
    assert "&lt;People&gt;" in html
    assert 'value="&lt;needle&gt;"' in html
    assert "/people/person-1?x=&lt;1&gt;" in html
    assert "&lt;Example Consumer&gt;" in html
    assert "&lt;supportive&gt;" in html
    assert "+54" in html
    assert "operator-safe people summary" in html
    assert "raw owner-private people note" not in html
    assert "Consumer-owned form slot" in html


def test_people_surface_owner_can_see_raw_private_notes():
    html = render_people_surface(_people_config(), privacy_policy=_policy(), privacy_context=_owner())

    assert "raw owner-private people note" in html
    assert "operator-safe people summary" not in html


def test_people_surface_fails_closed_without_policy():
    html = render_people_surface(
        PeopleSurfaceConfig(
            enabled=True,
            rows=[
                PersonListRow(
                    "owner-private",
                    "Owner Private",
                    notes="raw private note",
                    notes_privacy_scope="owner_private",
                )
            ],
        )
    )

    assert "[owner-private content withheld]" in html
    assert "raw private note" not in html


def test_people_surface_feature_flag_and_empty_state():
    config = PeopleSurfaceConfig(enabled=True)

    assert people_surface_feature_enabled(config, {PEOPLE_FEATURE: True}) is True
    assert render_people_surface(config, features={PEOPLE_FEATURE: False}) == ""

    html = render_people_surface(config)
    assert "No people found." in html
