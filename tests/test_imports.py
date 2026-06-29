import importlib
import sys
import tomllib
from pathlib import Path

import persona_console
import personacore
import personaconsole


def test_personaconsole_is_canonical_api():
    assert personaconsole.PersonaConsoleConfig is personaconsole.PersonaCoreConfig
    assert personaconsole.DashboardData
    assert personaconsole.DashboardMetricSpec
    assert personaconsole.render_dashboard_sections
    assert personaconsole.run_consumer_integration_doctor
    assert personaconsole.MESSAGES_FEATURE == "messages"
    assert personaconsole.ADAPTER_HEALTH_FEATURE == "adapter_health"
    assert personaconsole.AVAILABILITY_MONITOR_FEATURE == "availability_monitor"
    assert personaconsole.ADMIN_LIST_FEATURE == "admin_list"
    assert personaconsole.DETAIL_DOSSIER_FEATURE == "detail_dossier"
    assert personaconsole.TOKEN_HEALTH_FEATURE == "token_health"
    assert personaconsole.PEOPLE_FEATURE == "people"
    assert personaconsole.REVIEW_FEATURE == "review"
    assert personaconsole.JOURNAL_FEATURE == "journal"
    assert personaconsole.PUBLIC_PRESENCE_FEATURE == "public_presence"
    assert personaconsole.OPERATIONS_FEATURE == "operations"
    assert personaconsole.BRIDGE_OPS_FEATURE == "bridge_ops"
    assert personaconsole.COMMAND_INTAKE_FEATURE == "command_intake"
    assert personaconsole.PERSONA_EDITOR_FEATURE == "persona_editor"
    assert personaconsole.PERSONA_RUNTIME_FEATURE == "persona"
    assert personaconsole.AGENT_OPS_FEATURE == "agent_ops"
    assert personaconsole.TERMINAL_STREAM_FEATURE == "terminal_stream"
    assert personaconsole.SETTINGS_EDITOR_FEATURE == "settings_editor"
    assert personaconsole.SYSTEM_HEALTH_FEATURE == "system_health"
    assert "PersonaConsoleConfig" in personaconsole.__all__
    assert "PersonaCoreConfig" in personaconsole.__all__
    assert "render_public_splash_page" in personaconsole.__all__
    assert "render_availability_monitor_surface" in personaconsole.__all__
    assert "render_admin_list_surface" in personaconsole.__all__
    assert "render_detail_dossier_surface" in personaconsole.__all__
    assert "render_bridge_ops_surface" in personaconsole.__all__
    assert "render_command_intake_surface" in personaconsole.__all__
    assert "render_terminal_stream" in personaconsole.__all__
    assert "render_settings_editor" in personaconsole.__all__
    assert "render_system_health_surface" in personaconsole.__all__
    assert "render_persona_editor" in personaconsole.__all__
    assert "run_consumer_integration_doctor" in personaconsole.__all__


def test_legacy_import_shims_reexport_canonical_api():
    for legacy in (persona_console, personacore):
        assert legacy.__version__ == personaconsole.__version__
        assert legacy.PersonaConsoleConfig is personaconsole.PersonaConsoleConfig
        assert legacy.PersonaCoreConfig is personaconsole.PersonaCoreConfig
        assert legacy.DashboardData is personaconsole.DashboardData
        assert legacy.render_dashboard_sections is personaconsole.render_dashboard_sections
        assert legacy.render_adapter_health_panel is personaconsole.render_adapter_health_panel
        assert legacy.render_availability_monitor_surface is personaconsole.render_availability_monitor_surface
        assert legacy.render_admin_list_surface is personaconsole.render_admin_list_surface
        assert legacy.render_detail_dossier_surface is personaconsole.render_detail_dossier_surface
        assert legacy.render_token_health_panel is personaconsole.render_token_health_panel
        assert legacy.render_message_surface is personaconsole.render_message_surface
        assert legacy.render_people_surface is personaconsole.render_people_surface
        assert legacy.render_review_surface is personaconsole.render_review_surface
        assert legacy.render_journal_surface is personaconsole.render_journal_surface
        assert legacy.render_public_splash_page is personaconsole.render_public_splash_page
        assert legacy.render_bridge_ops_surface is personaconsole.render_bridge_ops_surface
        assert legacy.render_command_intake_surface is personaconsole.render_command_intake_surface
        assert legacy.render_operations_surface is personaconsole.render_operations_surface
        assert legacy.render_persona_editor is personaconsole.render_persona_editor
        assert legacy.render_terminal_stream is personaconsole.render_terminal_stream
        assert legacy.render_settings_editor is personaconsole.render_settings_editor
        assert legacy.render_system_health_surface is personaconsole.render_system_health_surface
        assert legacy.render_private_text is personaconsole.render_private_text


def test_legacy_submodules_reexport_canonical_implementation():
    legacy_modules = {
        "adapter_health": "render_adapter_health_panel",
        "admin_list": "render_admin_list_surface",
        "availability_monitor": "render_availability_monitor_surface",
        "detail_dossier": "render_detail_dossier_surface",
        "bridge_ops": "render_bridge_ops_surface",
        "command_intake": "render_command_intake_surface",
        "controls": "render_flash_banners",
        "dashboard": "render_dashboard_sections",
        "doctor": "run_consumer_integration_doctor",
        "fastapi": "register_static_assets",
        "journal": "render_journal_surface",
        "models": "PersonaConsoleConfig",
        "operations": "render_operations_surface",
        "people": "render_people_surface",
        "persona_editor": "render_persona_editor",
        "privacy": "render_private_text",
        "public_presence": "render_public_splash_page",
        "render": "render_nav_groups",
        "review": "render_review_surface",
        "settings_editor": "render_settings_editor",
        "system_health": "render_system_health_surface",
        "surfaces": "render_message_surface",
        "terminal": "render_terminal_stream",
        "token_health": "build_token_health_report",
    }
    for module_name, symbol in legacy_modules.items():
        canonical = importlib.import_module(f"personaconsole.{module_name}")
        old_console = importlib.import_module(f"persona_console.{module_name}")
        old_core = importlib.import_module(f"personacore.{module_name}")
        assert getattr(old_console, symbol) is getattr(canonical, symbol)
        assert getattr(old_core, symbol) is getattr(canonical, symbol)


def test_personaconsole_import_does_not_require_fastapi_dependency():
    already_imported = "fastapi" in sys.modules
    sys.modules.pop("personaconsole", None)

    module = importlib.import_module("personaconsole")

    assert module.PersonaConsoleConfig is personaconsole.PersonaConsoleConfig
    if not already_imported:
        assert "fastapi" not in sys.modules


def test_public_package_metadata_matches_runtime_version():
    pyproject = tomllib.loads(Path("pyproject.toml").read_text())

    assert pyproject["project"]["name"] == "personaconsole"
    assert pyproject["project"]["version"] == personaconsole.__version__ == "1.0.30"
