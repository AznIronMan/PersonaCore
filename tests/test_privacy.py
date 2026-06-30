from personaconsole import (
    OWNER_PRIVATE_ADMIN_FEATURE,
    AdminPrivacyContext,
    NavGroup,
    NavItem,
    OwnerPrivateScopePolicy,
    PersonaConsoleConfig,
    PrivacyRenderMode,
    can_view_raw_private,
    owner_private_scope_for_content,
    privacy_render_mode,
    render_nav_groups,
    render_private_text,
    render_shell_html,
)


def _policy() -> OwnerPrivateScopePolicy:
    return OwnerPrivateScopePolicy(
        owner_private_scopes={"owner_private": ("owner",)},
        aliases={"master_private": "owner_private"},
    )


def test_owner_private_scope_requires_matching_owner_and_scope():
    policy = _policy()

    owner = AdminPrivacyContext(
        access_tier="owner_private",
        viewer_person_key="owner",
        allowed_scopes=("public", "operator", "owner_private"),
    )
    operator = AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )
    admin = AdminPrivacyContext(
        access_tier="admin",
        viewer_person_key="admin",
        allowed_scopes=("public", "operator", "owner_private"),
    )

    assert can_view_raw_private(policy, owner, "owner_private") is True
    assert can_view_raw_private(policy, owner, "master_private") is True
    assert can_view_raw_private(policy, operator, "owner_private") is False
    assert can_view_raw_private(policy, admin, "owner_private") is False


def test_owner_private_render_modes_prefer_safe_alternate_then_withheld():
    policy = _policy()
    operator = AdminPrivacyContext(access_tier="operator", viewer_person_key="operator")

    assert (
        privacy_render_mode(policy, operator, "owner_private", has_safe_alternate=True)
        == PrivacyRenderMode.SAFE_ALTERNATE
    )
    assert privacy_render_mode(policy, operator, "owner_private") == PrivacyRenderMode.WITHHELD
    assert render_private_text(
        "raw private text",
        safe_alternate="operator-safe summary",
        policy=policy,
        context=operator,
        scope="owner_private",
    ) == "operator-safe summary"
    assert render_private_text(
        "raw private text",
        policy=policy,
        context=operator,
        scope="owner_private",
    ) == "[owner-private content withheld]"


def test_direct_content_tied_to_owner_resolves_owner_private_scope():
    policy = _policy()

    assert owner_private_scope_for_content(
        policy,
        sender_person_key="owner",
        receiver_person_key="operator",
        surface="dm",
    ) == "owner_private"
    assert owner_private_scope_for_content(
        policy,
        sender_person_key="operator",
        receiver_person_key="owner",
        is_direct=True,
    ) == "owner_private"
    assert owner_private_scope_for_content(
        policy,
        sender_person_key="owner",
        receiver_person_key="operator",
        surface="public_comment",
    ) is None


def test_owner_private_nav_feature_hides_module_without_changing_policy():
    policy = _policy()
    operator = AdminPrivacyContext(access_tier="operator", viewer_person_key="operator")
    nav = (
        NavGroup(
            "Admin",
            (
                NavItem("Dashboard", "/"),
                NavItem("Owner Private", "/owner-private", feature=OWNER_PRIVATE_ADMIN_FEATURE),
            ),
        ),
    )

    hidden = render_nav_groups(nav, active="dashboard", features={OWNER_PRIVATE_ADMIN_FEATURE: False})
    visible = render_nav_groups(nav, active="dashboard", features={OWNER_PRIVATE_ADMIN_FEATURE: True})

    assert "Owner Private" not in hidden
    assert "Owner Private" in visible
    assert privacy_render_mode(policy, operator, "owner_private") == PrivacyRenderMode.WITHHELD


def test_shell_applies_feature_gated_nav_items():
    config = PersonaConsoleConfig(
        brand_name="Example",
        page_title="Dashboard",
        features={OWNER_PRIVATE_ADMIN_FEATURE: False},
        nav_groups=[
            {
                "label": "Admin",
                "items": [
                    {"label": "Dashboard", "href": "/"},
                    {
                        "label": "Owner Private",
                        "href": "/owner-private",
                        "feature": OWNER_PRIVATE_ADMIN_FEATURE,
                    },
                ],
            }
        ],
    )

    html = render_shell_html(config, "<main>Body</main>")

    assert "Owner Private" not in html
