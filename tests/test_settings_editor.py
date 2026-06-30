from personaconsole import (
    SETTINGS_EDITOR_FEATURE,
    BrandAssets,
    FlashBanner,
    PersonaConsoleConfig,
    SettingsChange,
    SettingsEditorConfig,
    SettingsField,
    SettingsGroup,
    SettingsValidationMessage,
    SurfaceAction,
    build_admin_brand_settings_editor,
    build_admin_brand_settings_group,
    render_settings_editor,
    settings_editor_feature_enabled,
)


def test_settings_editor_renders_grouped_fields_changes_and_redacted_secret():
    html = render_settings_editor(
        SettingsEditorConfig(
            enabled=True,
            title="<Runtime Settings>",
            subtitle="Grouped runtime-owned config",
            form_action="/settings/save",
            banners=[FlashBanner("Saved safely", tone="good", action_label="Audit", action_href="/settings/audit")],
            messages=[SettingsValidationMessage("Interval is above normal", field_key="interval", tone="warn")],
            groups=[
                SettingsGroup(
                    "runtime",
                    "Runtime",
                    "Safe display values only",
                    fields=[
                        SettingsField(
                            "provider",
                            "<Provider>",
                            "provider",
                            "select",
                            "openai",
                            options=["openai", "xai"],
                        ),
                        SettingsField(
                            "api-key",
                            "API key",
                            "api_key",
                            "secret",
                            "raw-secret-token",
                            display_value="configured",
                            changed=True,
                            pending_value="new-raw-secret-token",
                            pending_display_value="new secret staged",
                            restart_required=True,
                            actions=[SurfaceAction("Reveal", "/settings/reveal/api-key")],
                        ),
                        SettingsField(
                            "interval",
                            "Interval",
                            "interval",
                            "number",
                            15,
                            pending_value=30,
                            changed=True,
                            min_value=1,
                            max_value=60,
                            step=1,
                        ),
                        SettingsField("notes", "Notes", "notes", "textarea", "hello <operator>"),
                        SettingsField("debug", "Debug", "debug", "boolean", True),
                        SettingsField("payload", "Payload", "payload", "json", {"enabled": True}, readonly=True),
                    ],
                )
            ],
        )
    )

    assert "pc-settings-editor" in html
    assert "&lt;Runtime Settings&gt;" in html
    assert "&lt;Provider&gt;" in html
    assert '<form class="pc-settings-editor' in html
    assert 'action="/settings/save"' in html
    assert '<option value="openai" selected>openai</option>' in html
    assert 'value="30"' in html
    assert "hello &lt;operator&gt;" in html
    assert 'type="checkbox"' in html
    assert "&quot;enabled&quot;: true" in html
    assert "Pending Changes" in html
    assert "restart required" in html
    assert "configured" in html
    assert "/settings/reveal/api-key" in html
    assert "raw-secret-token" not in html
    assert "new-raw-secret-token" not in html
    assert "new secret staged" not in html


def test_settings_editor_explicit_change_redacts_secret_values():
    html = render_settings_editor(
        {
            "enabled": True,
            "changes": [
                SettingsChange(
                    "Webhook secret",
                    before="old raw",
                    after="new raw",
                    secret=True,
                    restart_required=True,
                )
            ],
            "groups": [{"key": "empty", "title": "Empty"}],
        }
    )

    assert "Webhook secret" in html
    assert "********" in html
    assert "old raw" not in html
    assert "new raw" not in html


def test_settings_editor_feature_gate_and_empty_state():
    config = SettingsEditorConfig(enabled=True)

    assert settings_editor_feature_enabled(config, {SETTINGS_EDITOR_FEATURE: True}) is True
    assert settings_editor_feature_enabled(config, {SETTINGS_EDITOR_FEATURE: False}) is False
    assert render_settings_editor(config, features={SETTINGS_EDITOR_FEATURE: False}) == ""

    html = render_settings_editor(config)

    assert "No editable settings configured." in html


def test_admin_brand_settings_group_renders_optional_icon_url_field():
    group = build_admin_brand_settings_group(
        BrandAssets(
            name="Example Runtime",
            admin_subtitle="Operations",
            small_logo_url="/assets/admin-icon.svg",
            wordmark_url="/assets/admin-wordmark.svg",
            lockup_url="/assets/admin-lockup.svg",
            home_url="/admin",
        )
    )

    html = render_settings_editor(
        SettingsEditorConfig(enabled=True, form_action="/settings/branding/save", groups=[group])
    )

    assert "Admin Branding" in html
    assert "Brand title" in html
    assert "Brand subtitle" in html
    assert "Admin icon URL" in html
    assert 'name="small_logo_url"' in html
    assert 'name="admin_subtitle"' in html
    assert 'type="url"' in html
    assert 'value="/assets/admin-icon.svg"' in html
    assert 'value="Operations"' in html
    assert "Leave blank for name-only branding." in html
    assert 'value="/assets/admin-wordmark.svg"' in html
    assert 'value="/assets/admin-lockup.svg"' in html
    assert 'action="/settings/branding/save"' in html


def test_admin_brand_settings_editor_uses_console_config_and_allows_blank_icon():
    config = PersonaConsoleConfig(
        brand_name="Example Runtime",
        page_title="Dashboard",
        brand_assets=BrandAssets(name="Example Runtime", home_url="/admin"),
    )

    html = render_settings_editor(build_admin_brand_settings_editor(config, form_action="/settings/branding"))

    assert "Admin Branding" in html
    assert 'name="brand_name"' in html
    assert 'value="Example Runtime"' in html
    assert 'name="admin_subtitle"' in html
    assert 'name="small_logo_url"' in html
    assert 'value="/admin"' in html
    assert "/assets/admin-icon.svg" not in html


def test_admin_brand_settings_group_accepts_config_shaped_mapping():
    html = render_settings_editor(
        build_admin_brand_settings_editor(
            {
                "brand_name": "Example Runtime",
                "icon_url": "/assets/legacy-icon.svg",
                "admin_subtitle": "Ops",
                "wordmark_url": "/assets/title.svg",
                "lockup_url": "/assets/full.svg",
            },
            form_action="/settings/branding",
        )
    )

    assert 'value="Example Runtime"' in html
    assert 'value="/assets/legacy-icon.svg"' in html
    assert 'value="Ops"' in html
    assert 'value="/assets/title.svg"' in html
    assert 'value="/assets/full.svg"' in html
