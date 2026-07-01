from personaconsole import (
    PUBLIC_PROFILE_FEATURE,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    PublicProfileField,
    PublicProfileHistoryRow,
    PublicProfileMediaItem,
    PublicProfilePreview,
    PublicProfileReadinessCheck,
    PublicProfileSection,
    PublicProfileSurfaceConfig,
    SurfaceAction,
    public_profile_feature_enabled,
    render_public_profile_surface,
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


def _config() -> PublicProfileSurfaceConfig:
    return PublicProfileSurfaceConfig(
        enabled=True,
        title="Public Profile",
        subtitle="Profile draft, readiness, preview, media, and history.",
        status="draft",
        status_tone="info",
        form_action="/public-profile/save",
        submit_label="Save draft",
        actions=[
            SurfaceAction("Open public preview", "/public-profile/preview", "info"),
            SurfaceAction("Publish", "", "warn", disabled=True, title="Consumer runtime owns publishing."),
        ],
        preview=PublicProfilePreview(
            "Example Persona",
            "Public preview",
            "A generic public biography.",
            "/public-profile/preview",
            "/media/example.jpg",
            "draft",
            "info",
            actions=[SurfaceAction("Preview route", "/public-profile/preview")],
        ),
        readiness=[
            PublicProfileReadinessCheck("copy", "Profile copy", "ready", "good", "Required copy is present."),
            PublicProfileReadinessCheck("hero", "Hero media", "missing", "bad", "Upload a public-safe hero image."),
        ],
        sections=[
            PublicProfileSection(
                "copy",
                "Copy",
                "Public-facing text owned by the consumer runtime.",
                fields=[
                    PublicProfileField("display_name", "Display name", "Example Persona", required=True),
                    PublicProfileField("bio", "Bio", "Warm public biography.", multiline=True, rows=4),
                    PublicProfileField(
                        "private_note",
                        "Private note",
                        "raw private profile note",
                        detail="raw private detail",
                        privacy_scope="owner_private",
                        safe_alternate="safe profile note",
                    ),
                    PublicProfileField("published_slug", "Published slug", "example-persona", disabled=True),
                ],
            )
        ],
        media=[
            PublicProfileMediaItem("hero", "Hero image", "image", "/media/hero.jpg", "ready", "good", "Public-safe image."),
            PublicProfileMediaItem(
                "private-media",
                "Private media",
                "image",
                "/media/private.jpg",
                "held",
                "warn",
                "raw private media detail",
                privacy_scope="owner_private",
                safe_alternate="safe media summary",
            ),
        ],
        history=[
            PublicProfileHistoryRow("draft", "Draft saved", "draft", "info", "operator", "09:00", "Saved public-safe copy."),
            PublicProfileHistoryRow(
                "private-history",
                "Private history",
                "held",
                "warn",
                "operator",
                "09:05",
                "raw private history",
                privacy_scope="owner_private",
                safe_alternate="safe history summary",
            ),
        ],
    )


def test_public_profile_surface_renders_editor_preview_and_redacts_private_values():
    html = render_public_profile_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-public-profile-surface" in html
    assert 'action="/public-profile/save"' in html
    assert 'name="display_name"' in html
    assert "required" in html
    assert "textarea" in html
    assert "safe profile note" in html
    assert "safe media summary" in html
    assert "safe history summary" in html
    assert "Hero media" in html
    assert "missing" in html
    assert "Open preview" in html
    assert "Publish" in html
    assert 'aria-disabled="true"' in html
    assert "raw private profile note" not in html
    assert "raw private detail" not in html
    assert "raw private media detail" not in html
    assert "raw private history" not in html
    assert "/media/private.jpg" not in html


def test_public_profile_owner_can_see_raw_private_values():
    html = render_public_profile_surface(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private profile note" in html
    assert "raw private media detail" in html
    assert "raw private history" in html
    assert "/media/private.jpg" in html
    assert "safe profile note" not in html


def test_public_profile_feature_gate_and_empty_state():
    config = PublicProfileSurfaceConfig(enabled=True)

    assert public_profile_feature_enabled(config, {PUBLIC_PROFILE_FEATURE: True}) is True
    assert public_profile_feature_enabled(config, {PUBLIC_PROFILE_FEATURE: False}) is False
    assert render_public_profile_surface(config, features={PUBLIC_PROFILE_FEATURE: False}) == ""

    html = render_public_profile_surface(config)

    assert "No public profile data configured." in html
