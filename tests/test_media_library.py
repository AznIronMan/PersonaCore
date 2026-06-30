import personaconsole


def _policy() -> personaconsole.OwnerPrivateScopePolicy:
    return personaconsole.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})


def _operator() -> personaconsole.AdminPrivacyContext:
    return personaconsole.AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )


def _owner() -> personaconsole.AdminPrivacyContext:
    return personaconsole.AdminPrivacyContext(
        access_tier="owner_private",
        viewer_person_key="owner",
        allowed_scopes=("public", "operator", "owner_private"),
    )


def _library_config(view: str = "grid") -> personaconsole.MediaLibrarySurfaceConfig:
    return personaconsole.MediaLibrarySurfaceConfig(
        enabled=True,
        title="Artifact Library",
        subtitle="Uploads, received media, and generated jobs",
        view=view,
        status_tabs=[
            personaconsole.StatusTab("All", "/media", count=4, active=True),
            personaconsole.StatusTab("Review", "/media?status=review", count=1, tone="warn"),
        ],
        filters=[
            personaconsole.DashboardFilter("Images", "/media?type=image", key="images", active=True),
            personaconsole.DashboardFilter("Jobs", "/media?type=jobs", key="jobs"),
        ],
        view_options=[
            personaconsole.DashboardFilter("Grid", "/media?view=grid", key="grid"),
            personaconsole.DashboardFilter("List", "/media?view=list", key="list"),
        ],
        metrics=[
            personaconsole.DashboardMetric("Assets", 4, "/media", "visible", tone="info"),
            personaconsole.DashboardMetric("Sendable", 2, "/media?sendable=1", "ready", tone="good"),
        ],
        actions=[personaconsole.SurfaceAction("Upload", "/media/upload", tone="good")],
        action_slots=[
            personaconsole.MediaLibraryActionSlot(
                "import",
                "Import Media",
                "Consumer runtime owns upload and import routes.",
                actions=[
                    personaconsole.SurfaceAction("Import file", "/media/import", tone="info"),
                    personaconsole.SurfaceAction("Regenerate", "/media/jobs/regenerate", method="post", tone="warn"),
                ],
            )
        ],
        items=[
            personaconsole.MediaLibraryItem(
                "portrait",
                "Portrait reference",
                href="/media/artifacts/portrait",
                preview_url="/media/artifacts/portrait.jpg",
                preview_alt="Portrait preview",
                media_type="image",
                status="approved",
                review_status="approved",
                safety="safe",
                sendability="sendable",
                heat="low",
                shareability="ready",
                owner="example-persona",
                source="upload",
                timestamp="now",
                detail="Primary visual anchor.",
                badges=["reference", personaconsole.SurfaceBadge("visual", "info")],
                metadata=[
                    personaconsole.MediaLibraryMetadata("ratio", "Ratio", "4:5"),
                    personaconsole.MediaLibraryMetadata("quality", "Quality", "curated", tone="good"),
                ],
                actions=[personaconsole.SurfaceAction("Open", "/media/artifacts/portrait")],
                selected=True,
            ),
            personaconsole.MediaLibraryItem(
                "voice",
                "Voice note",
                href="/media/audio/voice",
                preview_url="/media/audio/voice.mp3",
                media_type="audio",
                status="pending",
                review_status="review",
                safety="review",
                sendability="manual",
                source="received",
                detail="Audio fallback preview.",
            ),
            personaconsole.MediaLibraryItem(
                "doc",
                "Reference PDF",
                href="/media/files/reference",
                media_type="pdf",
                status="stored",
                source="import",
                detail="Non-image placeholder.",
            ),
        ],
    )


def test_media_library_renders_grid_controls_actions_and_preview_dialog():
    html = personaconsole.render_media_library_surface(_library_config())

    assert 'id="media-library"' in html
    assert "pc-media-library-surface" in html
    assert "pc-media-library-view-grid" in html
    assert "Artifact Library" in html
    assert "pc-status-tabs" in html
    assert "pc-media-library-controls" in html
    assert "pc-media-library-action-slot" in html
    assert "Upload" in html
    assert "Import file" in html
    assert "data-method=\"post\"" in html
    assert "pc-media-library-grid" in html
    assert "Portrait reference" in html
    assert "/media/artifacts/portrait.jpg" in html
    assert "pc-media-library-dialog" in html
    assert "pc-media-library-flag" in html
    assert "<b>safety</b>safe" in html
    assert "<b>send</b>sendable" in html
    assert "Reference PDF" in html
    assert "FILE" in html


def test_media_library_renders_list_mode():
    html = personaconsole.render_media_library_surface(_library_config("list"))

    assert "pc-media-library-view-list" in html
    assert "pc-media-library-table" in html
    assert "pc-media-library-row-media" in html
    assert "Portrait reference" in html
    assert "Voice note" in html
    assert "Source" in html


def test_media_library_redacts_private_items_and_strips_unsafe_urls():
    raw_value = "raw private portrait title"
    raw_url = "/media/raw-private/portrait.jpg"
    html = personaconsole.render_media_library_surface(
        {
            "enabled": True,
            "items": [
                {
                    "key": "private",
                    "label": raw_value,
                    "href": "/media/raw-private/detail",
                    "preview_url": raw_url,
                    "detail": "raw private media detail",
                    "safe_alternate": "operator-safe media summary",
                    "privacy_scope": "owner_private",
                    "metadata": [
                        {
                            "key": "note",
                            "label": "Note",
                            "value": "raw private metadata",
                            "safe_alternate": "safe metadata",
                            "privacy_scope": "owner_private",
                        }
                    ],
                    "actions": [{"label": "Unsafe", "href": "https://private.example/media"}],
                },
                {
                    "key": "public-unsafe",
                    "label": "Public unsafe URL",
                    "href": "javascript:alert(1)",
                    "preview_url": "//private.example/asset.png",
                    "actions": [{"label": "Callback", "href": "/oauth/callback"}],
                },
            ],
        },
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "operator-safe media summary" in html
    assert "safe metadata" in html
    assert "raw private" not in html
    assert raw_url not in html
    assert "https://private.example" not in html
    assert "javascript:" not in html
    assert "private.example" not in html
    assert "/oauth/callback" not in html
    assert "is-disabled" in html
    assert "is-private" in html


def test_media_library_owner_can_see_private_root_relative_urls():
    html = personaconsole.render_media_library_surface(
        {
            "enabled": True,
            "items": [
                {
                    "key": "private",
                    "label": "raw owner artifact",
                    "href": "/media/owner/detail",
                    "preview_url": "/media/owner/preview.jpg",
                    "media_type": "image",
                    "detail": "raw owner detail",
                    "privacy_scope": "owner_private",
                    "safe_alternate": "safe summary",
                }
            ],
        },
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw owner artifact" in html
    assert "raw owner detail" in html
    assert "/media/owner/detail" in html
    assert "/media/owner/preview.jpg" in html
    assert "safe summary" not in html


def test_media_library_feature_flag_and_empty_state():
    config = personaconsole.MediaLibrarySurfaceConfig(enabled=True)

    assert personaconsole.media_library_surface_feature_enabled(config, {"media_library": True}) is True
    assert personaconsole.render_media_library_surface(config, features={"media_library": False}) == ""
    assert "No media items found." in personaconsole.render_media_library_surface(config)
