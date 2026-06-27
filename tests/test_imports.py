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
    assert personacore.PEOPLE_FEATURE == persona_console.PEOPLE_FEATURE == "people"
    assert personacore.PeopleSurfaceConfig is persona_console.PeopleSurfaceConfig
    assert personacore.PersonListRow is persona_console.PersonListRow
    assert personacore.PersonRelationshipSummary is persona_console.PersonRelationshipSummary
    assert personacore.PersonTag is persona_console.PersonTag
    assert personacore.render_people_surface is persona_console.render_people_surface
    assert personacore.REVIEW_FEATURE == persona_console.REVIEW_FEATURE == "review"
    assert personacore.ReviewSurfaceConfig is persona_console.ReviewSurfaceConfig
    assert personacore.ReviewBoardRow is persona_console.ReviewBoardRow
    assert personacore.render_review_surface is persona_console.render_review_surface
    assert personacore.JOURNAL_FEATURE == persona_console.JOURNAL_FEATURE == "journal"
    assert len(personacore.JOURNAL_THEME_KEYS) == 12
    assert personacore.JournalSurfaceConfig is persona_console.JournalSurfaceConfig
    assert personacore.JournalEntry is persona_console.JournalEntry
    assert personacore.JournalCalendarDay is persona_console.JournalCalendarDay
    assert personacore.render_journal_surface is persona_console.render_journal_surface
    assert personacore.journal_theme_options is persona_console.journal_theme_options
    assert personacore.PUBLIC_PRESENCE_FEATURE == persona_console.PUBLIC_PRESENCE_FEATURE == "public_presence"
    assert len(personacore.PUBLIC_THEME_KEYS) == 12
    assert personacore.BrandAssets is persona_console.BrandAssets
    assert personacore.PublicMediaConfig is persona_console.PublicMediaConfig
    assert personacore.PublicMediaSource is persona_console.PublicMediaSource
    assert personacore.PublicSplashPageConfig is persona_console.PublicSplashPageConfig
    assert personacore.LoginPageConfig is persona_console.LoginPageConfig
    assert personacore.ChatPageConfig is persona_console.ChatPageConfig
    assert personacore.PublicSettingsSurfaceConfig is persona_console.PublicSettingsSurfaceConfig
    assert personacore.ConnectorOption is persona_console.ConnectorOption
    assert personacore.ConnectorGroup is persona_console.ConnectorGroup
    assert personacore.render_public_splash_page is persona_console.render_public_splash_page
    assert personacore.render_login_page is persona_console.render_login_page
    assert personacore.render_chat_page is persona_console.render_chat_page
    assert personacore.render_public_settings_surface is persona_console.render_public_settings_surface
    assert personacore.OPERATIONS_FEATURE == persona_console.OPERATIONS_FEATURE == "operations"
    assert personacore.PERSONA_RUNTIME_FEATURE == persona_console.PERSONA_RUNTIME_FEATURE == "persona"
    assert personacore.AGENT_OPS_FEATURE == persona_console.AGENT_OPS_FEATURE == "agent_ops"
    assert personacore.OperationsSurfaceConfig is persona_console.OperationsSurfaceConfig
    assert personacore.PersonaRuntimeSurfaceConfig is persona_console.PersonaRuntimeSurfaceConfig
    assert personacore.AgentOpsSurfaceConfig is persona_console.AgentOpsSurfaceConfig
    assert personacore.render_operations_surface is persona_console.render_operations_surface
    assert personacore.render_persona_runtime_surface is persona_console.render_persona_runtime_surface
    assert personacore.render_agent_ops_surface is persona_console.render_agent_ops_surface
    assert personacore.FlashBanner is persona_console.FlashBanner
    assert personacore.render_flash_banners is persona_console.render_flash_banners
    assert personacore.flash_url is persona_console.flash_url
    assert personacore.StatusTab is persona_console.StatusTab
    assert personacore.render_status_tabs is persona_console.render_status_tabs
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
    assert "PEOPLE_FEATURE" in personacore.__all__
    assert "PeopleSurfaceConfig" in personacore.__all__
    assert "render_people_surface" in personacore.__all__
    assert "REVIEW_FEATURE" in personacore.__all__
    assert "ReviewSurfaceConfig" in personacore.__all__
    assert "render_review_surface" in personacore.__all__
    assert "JOURNAL_FEATURE" in personacore.__all__
    assert "JOURNAL_THEME_KEYS" in personacore.__all__
    assert "JournalSurfaceConfig" in personacore.__all__
    assert "render_journal_surface" in personacore.__all__
    assert "PUBLIC_PRESENCE_FEATURE" in personacore.__all__
    assert "PublicSplashPageConfig" in personacore.__all__
    assert "render_public_splash_page" in personacore.__all__
    assert "render_login_page" in personacore.__all__
    assert "render_chat_page" in personacore.__all__
    assert "render_public_settings_surface" in personacore.__all__
    assert "OPERATIONS_FEATURE" in personacore.__all__
    assert "OperationsSurfaceConfig" in personacore.__all__
    assert "render_operations_surface" in personacore.__all__
    assert "PERSONA_RUNTIME_FEATURE" in personacore.__all__
    assert "render_persona_runtime_surface" in personacore.__all__
    assert "AGENT_OPS_FEATURE" in personacore.__all__
    assert "render_agent_ops_surface" in personacore.__all__
    assert "FlashBanner" in personacore.__all__
    assert "render_flash_banners" in personacore.__all__
    assert "flash_url" in personacore.__all__
    assert "StatusTab" in personacore.__all__
    assert "render_status_tabs" in personacore.__all__
    assert "OwnerPrivateScopePolicy" in personacore.__all__


def test_personacore_submodules_reexport_existing_implementation():
    from personacore.adapter_health import render_adapter_health_panel
    from personacore.dashboard import dashboard_metrics_from_counts, render_dashboard_sections
    from personacore.models import (
        AdapterHealthConfig,
        DashboardMetricSpec,
        MessageSurfaceConfig,
        OperationsSurfaceConfig,
        PeopleSurfaceConfig,
        PersonaCoreConfig,
        PersonaRuntimeSurfaceConfig,
        PublicSettingsSurfaceConfig,
        PublicSplashPageConfig,
        FlashBanner,
        StatusTab,
    )
    from personacore.controls import flash_url, render_flash_banners, render_status_tabs
    from personacore.people import PEOPLE_FEATURE, render_people_surface
    from personacore.privacy import OwnerPrivateScopePolicy, render_private_text
    from personacore.render import render_nav_groups
    from personacore.review import REVIEW_FEATURE, render_review_surface
    from personacore.journal import JOURNAL_FEATURE, render_journal_surface
    from personacore.public_presence import PUBLIC_PRESENCE_FEATURE, render_public_splash_page
    from personacore.surfaces import render_message_surface, render_surface_sections
    from personacore.operations import OPERATIONS_FEATURE, OperationsSurfaceConfig as OpsConfig, render_operations_surface
    from personacore.token_health import build_token_health_report, token_health_config_for_providers
    from personacore.doctor import run_consumer_integration_doctor

    assert PersonaCoreConfig is persona_console.PersonaConsoleConfig
    assert AdapterHealthConfig is persona_console.AdapterHealthConfig
    assert MessageSurfaceConfig is persona_console.MessageSurfaceConfig
    assert PeopleSurfaceConfig is persona_console.PeopleSurfaceConfig
    assert DashboardMetricSpec is persona_console.DashboardMetricSpec
    assert OperationsSurfaceConfig is persona_console.OperationsSurfaceConfig
    assert PersonaRuntimeSurfaceConfig is persona_console.PersonaRuntimeSurfaceConfig
    assert PublicSettingsSurfaceConfig is persona_console.PublicSettingsSurfaceConfig
    assert PublicSplashPageConfig is persona_console.PublicSplashPageConfig
    assert OpsConfig is persona_console.OperationsSurfaceConfig
    assert FlashBanner is persona_console.FlashBanner
    assert StatusTab is persona_console.StatusTab
    assert flash_url is persona_console.flash_url
    assert render_flash_banners is persona_console.render_flash_banners
    assert render_status_tabs is persona_console.render_status_tabs
    assert render_adapter_health_panel is persona_console.render_adapter_health_panel
    assert OwnerPrivateScopePolicy is persona_console.OwnerPrivateScopePolicy
    assert render_private_text is persona_console.render_private_text
    assert render_nav_groups is persona_console.render_nav_groups
    assert render_dashboard_sections is persona_console.render_dashboard_sections
    assert dashboard_metrics_from_counts is persona_console.dashboard_metrics_from_counts
    assert render_message_surface is persona_console.render_message_surface
    assert render_surface_sections is persona_console.render_surface_sections
    assert PEOPLE_FEATURE == persona_console.PEOPLE_FEATURE
    assert render_people_surface is persona_console.render_people_surface
    assert REVIEW_FEATURE == persona_console.REVIEW_FEATURE
    assert render_review_surface is persona_console.render_review_surface
    assert JOURNAL_FEATURE == persona_console.JOURNAL_FEATURE
    assert render_journal_surface is persona_console.render_journal_surface
    assert PUBLIC_PRESENCE_FEATURE == persona_console.PUBLIC_PRESENCE_FEATURE
    assert render_public_splash_page is persona_console.render_public_splash_page
    assert OPERATIONS_FEATURE == persona_console.OPERATIONS_FEATURE
    assert render_operations_surface is persona_console.render_operations_surface
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
    assert pyproject["project"]["version"] == personacore.__version__ == "1.0.20"
