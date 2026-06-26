import importlib
import sys
import tomllib
from pathlib import Path

import persona_console
import personacore


def test_personacore_reexports_core_api():
    assert personacore.PersonaCoreConfig is persona_console.PersonaCoreConfig
    assert personacore.PersonaConsoleConfig is persona_console.PersonaConsoleConfig
    assert personacore.PersonaCoreConfig is personacore.PersonaConsoleConfig
    assert personacore.DashboardData is persona_console.DashboardData
    assert personacore.DashboardMetricSpec is persona_console.DashboardMetricSpec
    assert personacore.render_dashboard_sections is persona_console.render_dashboard_sections
    assert personacore.dashboard_metrics_from_counts is persona_console.dashboard_metrics_from_counts
    assert personacore.run_consumer_integration_doctor is persona_console.run_consumer_integration_doctor
    assert personacore.MESSAGES_FEATURE == persona_console.MESSAGES_FEATURE == "messages"
    assert personacore.ACTIVITY_FEATURE == persona_console.ACTIVITY_FEATURE == "activity"
    assert personacore.MEDIA_FEATURE == persona_console.MEDIA_FEATURE == "media"
    assert personacore.MessageSurfaceConfig is persona_console.MessageSurfaceConfig
    assert personacore.ActivitySurfaceConfig is persona_console.ActivitySurfaceConfig
    assert personacore.MediaSurfaceConfig is persona_console.MediaSurfaceConfig
    assert personacore.render_message_surface is persona_console.render_message_surface
    assert personacore.render_surface_sections is persona_console.render_surface_sections
    assert personacore.ADAPTER_HEALTH_FEATURE == persona_console.ADAPTER_HEALTH_FEATURE == "adapter_health"
    assert personacore.AdapterHealthConfig is persona_console.AdapterHealthConfig
    assert personacore.AdapterHealthCard is persona_console.AdapterHealthCard
    assert personacore.render_adapter_health_panel is persona_console.render_adapter_health_panel
    assert personacore.TOKEN_HEALTH_FEATURE == persona_console.TOKEN_HEALTH_FEATURE == "token_health"
    assert personacore.TokenHealthConfig is persona_console.TokenHealthConfig
    assert personacore.build_token_health_report is persona_console.build_token_health_report
    assert personacore.token_health_config_for_providers is persona_console.token_health_config_for_providers
    assert personacore.OwnerPrivateScopePolicy is persona_console.OwnerPrivateScopePolicy
    assert personacore.AdminPrivacyContext is persona_console.AdminPrivacyContext
    assert personacore.PrivacyRenderMode is persona_console.PrivacyRenderMode
    assert personacore.render_private_text is persona_console.render_private_text
    assert personacore.NavItem is persona_console.NavItem
    assert personacore.render_shell_html is persona_console.render_shell_html
    assert "PersonaCoreConfig" in personacore.__all__
    assert "DashboardData" in personacore.__all__
    assert "ADAPTER_HEALTH_FEATURE" in personacore.__all__
    assert "AdapterHealthConfig" in personacore.__all__
    assert "run_consumer_integration_doctor" in personacore.__all__
    assert "MESSAGES_FEATURE" in personacore.__all__
    assert "MessageSurfaceConfig" in personacore.__all__
    assert "render_surface_sections" in personacore.__all__
    assert "TOKEN_HEALTH_FEATURE" in personacore.__all__
    assert "TokenHealthConfig" in personacore.__all__
    assert "OwnerPrivateScopePolicy" in personacore.__all__


def test_personacore_submodules_reexport_existing_implementation():
    from personacore.adapter_health import render_adapter_health_panel
    from personacore.dashboard import dashboard_metrics_from_counts, render_dashboard_sections
    from personacore.models import AdapterHealthConfig, DashboardMetricSpec, MessageSurfaceConfig, PersonaCoreConfig
    from personacore.privacy import OwnerPrivateScopePolicy, render_private_text
    from personacore.render import render_nav_groups
    from personacore.surfaces import render_message_surface, render_surface_sections
    from personacore.token_health import build_token_health_report, token_health_config_for_providers
    from personacore.doctor import run_consumer_integration_doctor

    assert PersonaCoreConfig is persona_console.PersonaConsoleConfig
    assert AdapterHealthConfig is persona_console.AdapterHealthConfig
    assert MessageSurfaceConfig is persona_console.MessageSurfaceConfig
    assert DashboardMetricSpec is persona_console.DashboardMetricSpec
    assert render_adapter_health_panel is persona_console.render_adapter_health_panel
    assert OwnerPrivateScopePolicy is persona_console.OwnerPrivateScopePolicy
    assert render_private_text is persona_console.render_private_text
    assert render_nav_groups is persona_console.render_nav_groups
    assert render_dashboard_sections is persona_console.render_dashboard_sections
    assert dashboard_metrics_from_counts is persona_console.dashboard_metrics_from_counts
    assert render_message_surface is persona_console.render_message_surface
    assert render_surface_sections is persona_console.render_surface_sections
    assert build_token_health_report is persona_console.build_token_health_report
    assert token_health_config_for_providers is persona_console.token_health_config_for_providers
    assert run_consumer_integration_doctor is persona_console.run_consumer_integration_doctor


def test_personacore_import_does_not_require_fastapi_dependency():
    already_imported = "fastapi" in sys.modules
    sys.modules.pop("personacore", None)

    module = importlib.import_module("personacore")

    assert module.PersonaCoreConfig is persona_console.PersonaConsoleConfig
    if not already_imported:
        assert "fastapi" not in sys.modules


def test_public_package_metadata_matches_runtime_version():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert pyproject["project"]["name"] == "personacore"
    assert pyproject["project"]["version"] == personacore.__version__ == "1.0.9"
