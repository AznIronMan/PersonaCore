from pathlib import Path

from personaconsole import (
    CONTROL_CENTER_FEATURE,
    ControlCenterConfig,
    ControlGroup,
    ControlItem,
    ControlOption,
    ControlSection,
    PersonaConsoleConfig,
    SettingsValidationMessage,
    SurfaceAction,
    SurfaceRegistration,
    SurfaceRegistryConfig,
    build_control_center_from_sources,
    control_center_feature_enabled,
    render_control_center,
)


def test_control_center_css_prevents_form_grid_column_inheritance():
    css = Path("src/personaconsole/static/persona-console.css").read_text()

    assert ".pc-control-center {\n  display: grid;\n  gap: 14px;\n  grid-template-columns: minmax(0, 1fr);" in css
    assert "repeat(auto-fit, minmax(min(300px, 100%), 1fr))" in css


def test_control_center_renders_switches_changes_actions_and_redacted_secret():
    raw_secret = "raw-control-secret"
    html = render_control_center(
        ControlCenterConfig(
            enabled=True,
            title="Control Center",
            form_action="/control/save",
            messages=[SettingsValidationMessage("Runtime restart is queued.", "provider-secret", "warn")],
            actions=[SurfaceAction("Audit trail", "/control/audit", "info")],
            sections=[
                ControlSection(
                    "features",
                    "Features",
                    groups=[
                        ControlGroup(
                            "runtime",
                            "Runtime",
                            "Operator controls",
                            items=[
                                ControlItem(
                                    "messages",
                                    "Messages",
                                    "pc.feature.messages",
                                    "switch",
                                    True,
                                    owner="Console",
                                    source_path="pc.feature.messages",
                                    status="enabled",
                                ),
                                ControlItem(
                                    "canary-mode",
                                    "Canary mode",
                                    "engine.projection.canary_mode",
                                    "segmented",
                                    "log_only",
                                    options=[
                                        ControlOption("off", "Off"),
                                        ControlOption("log_only", "Log only"),
                                        ControlOption("block", "Block"),
                                    ],
                                    owner="Engine",
                                    source_path="engine.projection.canary_mode",
                                    restart_required=True,
                                ),
                                ControlItem(
                                    "provider-secret",
                                    "Provider API key",
                                    "runtime.provider_secret",
                                    "secret",
                                    raw_secret,
                                    display_value="configured",
                                    pending_display_value="new secret staged",
                                    changed=True,
                                    restart_required=True,
                                    owner="Runtime",
                                    source_path="runtime.provider_secret",
                                ),
                            ],
                        )
                    ],
                )
            ],
        )
    )

    assert "pc-control-center" in html
    assert "Control Center" in html
    assert 'action="/control/save"' in html
    assert 'name="pc.feature.messages" value="false"' in html
    assert 'type="checkbox"' in html
    assert "Log only" in html
    assert "Pending Changes" in html
    assert "restart required" in html
    assert "configured" in html
    assert "/control/audit" in html
    assert raw_secret not in html
    assert "new secret staged" not in html


def test_control_center_feature_gate_and_empty_state():
    config = ControlCenterConfig(enabled=True)

    assert control_center_feature_enabled(config, {CONTROL_CENTER_FEATURE: True}) is True
    assert control_center_feature_enabled(config, {CONTROL_CENTER_FEATURE: False}) is False
    assert render_control_center(config, features={CONTROL_CENTER_FEATURE: False}) == ""
    assert "No controls configured." in render_control_center(config)


def test_build_control_center_from_console_and_engine_sources():
    console_config = PersonaConsoleConfig(
        brand_name="Example Runtime",
        page_title="Dashboard",
        features={"messages": True, "review": False},
        nav_groups=[
            {"label": "Overview", "items": [{"label": "Overview", "href": "/", "active": "dashboard"}]},
        ],
    )
    registry = SurfaceRegistryConfig(
        enabled=True,
        features={"system_health": True},
        surfaces=[
            SurfaceRegistration(
                "health",
                "Health",
                feature="system_health",
                href="/health",
                summary="System health surface.",
            )
        ],
    )
    engine_catalog = {
        "catalog_id": "engine-control-catalog",
        "groups": [
            {
                "key": "engine-features",
                "label": "PersonaEngine Features",
                "section": "features",
                "controls": [
                    {
                        "key": "engine-feature-workflows",
                        "label": "Workflows",
                        "source_path": "engine.feature.workflows",
                        "kind": "boolean",
                        "value": True,
                        "owner": "Engine",
                        "restart_required": True,
                    }
                ],
            },
            {
                "key": "engine-cadence",
                "label": "Cadence",
                "section": "runtime",
                "controls": [
                    {
                        "key": "engine-cadence-max-chunk",
                        "label": "Max chunk size",
                        "source_path": "engine.projection.cadence_settings.max_chunk_chars",
                        "kind": "number",
                        "value": 220,
                        "owner": "Engine",
                    }
                ],
            },
            {
                "key": "engine-persona-extension-slots",
                "label": "Persona Extension Slots",
                "section": "persona",
                "owner": "Runtime",
                "controls": [
                    {
                        "key": "engine-extension-consumer-controls",
                        "label": "Consumer control sections",
                        "source_path": "runtime.control.extra_sections",
                        "kind": "readonly",
                        "value": "runtime-supplied",
                        "display_value": "runtime-supplied",
                        "owner": "Runtime",
                        "readonly": True,
                    }
                ],
            },
        ],
    }

    html = render_control_center(
        build_control_center_from_sources(
            console_config,
            surface_registry=registry,
            engine_catalog=engine_catalog,
            form_action="/control/save",
        )
    )

    assert "Features" in html
    assert "Appearance &amp; Navigation" in html
    assert "Runtime Behavior" in html
    assert "Persona Extensions" in html
    assert "Advanced &amp; Audit" in html
    assert "pc.feature.messages" in html
    assert "pc.feature.system_health" in html
    assert "engine.feature.workflows" in html
    assert "engine.projection.cadence_settings.max_chunk_chars" in html
    assert "runtime.control.extra_sections" in html
    assert "Surface registry preview" in html
