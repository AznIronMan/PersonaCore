from personaconsole import (
    LiveRefreshConfig,
    NavGroup,
    SurfaceAdapterBinding,
    SurfaceAssetRequirement,
    SurfaceRegistration,
    SurfaceRegistryConfig,
    build_surface_registry_report,
    render_surface_registry_report,
    surface_registry_feature_enabled,
    surface_registry_feature_flags,
    surface_registry_report_to_dict,
    surface_registry_to_nav_groups,
)


def _registry() -> SurfaceRegistryConfig:
    return SurfaceRegistryConfig(
        enabled=True,
        features={"messages": True, "system_health": True, "review": False},
        nav_groups=[NavGroup("Core", (), key="core"), NavGroup("System", (), key="system")],
        surfaces=[
            SurfaceRegistration(
                "messages",
                "Messages",
                feature="messages",
                renderer="render_message_surface",
                route_key="messages",
                href="/messages",
                nav_group="core",
                active="messages",
                theme_key="dark",
                live_refresh=LiveRefreshConfig(enabled=True, url="/partials/messages"),
                required_assets=[SurfaceAssetRequirement("css", "Shared CSS", "/persona-console/static/persona-console.css")],
                adapters=[SurfaceAdapterBinding("message_rows", "Message rows", "runtime snapshot")],
            ),
            SurfaceRegistration(
                "system-health",
                "System Health",
                feature="system_health",
                renderer="render_system_health_surface",
                route_key="system-health",
                href="/system/health",
                nav_group="system",
                active="health",
                required_assets=["css"],
            ),
            SurfaceRegistration(
                "review",
                "Review",
                feature="review",
                renderer="render_review_surface",
                route_key="review",
                href="/review",
                enabled=True,
                required=False,
            ),
        ],
    )


def test_surface_registry_reports_configured_nav_features_and_renderers():
    registry = _registry()
    report = build_surface_registry_report(
        registry,
        available_renderers={
            "render_message_surface": True,
            "render_system_health_surface": True,
            "render_review_surface": True,
        },
        available_assets={"css": True},
    )
    html = render_surface_registry_report(
        registry,
        available_renderers={
            "render_message_surface": True,
            "render_system_health_surface": True,
            "render_review_surface": True,
        },
        available_assets={"css": True},
    )
    nav_groups = surface_registry_to_nav_groups(registry)
    flags = surface_registry_feature_flags(registry)

    assert report.ok is True
    assert report.surface_count == 3
    assert report.enabled_count == 2
    assert report.disabled_count == 1
    assert any(group.key == "core" for group in nav_groups)
    assert flags["messages"] is True
    assert flags["review"] is False
    assert "pc-surface-registry" in html
    assert "Messages" in html
    assert "Message rows" in html
    assert "No registry issues found." not in html
    assert "Surface is disabled: Review" in html


def test_surface_registry_validation_catches_public_safe_gaps():
    registry = SurfaceRegistryConfig(
        enabled=True,
        features={"mystery_feature": True},
        surfaces=[
            SurfaceRegistration(
                "one",
                "One",
                feature="mystery_feature",
                renderer="render_missing",
                route_key="duplicate",
                href="/one",
                required_assets=[SurfaceAssetRequirement("logo", "Logo", "/persona-console/static/logo.png", present=False)],
            ),
            SurfaceRegistration("two", "Two", renderer="render_two", route_key="duplicate", href="https://private.example/two"),
        ],
    )

    report = build_surface_registry_report(registry, available_renderers={"render_two": True})
    data = surface_registry_report_to_dict(report)
    keys = {issue["key"] for issue in data["issues"]}

    assert report.ok is False
    assert "unknown-feature" in keys
    assert "missing-renderer" in keys
    assert "missing-asset" in keys
    assert "duplicate-route-key" in keys
    assert "unsafe-href" in keys


def test_surface_registry_feature_gate_and_empty_state():
    config = SurfaceRegistryConfig(enabled=True)

    assert surface_registry_feature_enabled(config, {"surface_composition": True}) is True
    assert render_surface_registry_report(config, features={"surface_composition": False}) == ""

    html = render_surface_registry_report(config)
    assert "No PersonaConsole surfaces registered." in html
