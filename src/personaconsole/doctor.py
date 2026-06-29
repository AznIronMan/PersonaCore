from __future__ import annotations

import argparse
import importlib
import importlib.metadata
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Sequence


_TOKEN_HEALTH_EXPORTS = (
    "TOKEN_HEALTH_FEATURE",
    "TokenHealthCheck",
    "TokenHealthConfig",
    "build_token_health_report",
    "render_token_health_panel",
    "token_health_config_for_providers",
    "token_health_feature_enabled",
    "token_health_lookup",
)
_ADAPTER_HEALTH_EXPORTS = (
    "ADAPTER_HEALTH_FEATURE",
    "AdapterHealthCard",
    "AdapterHealthConfig",
    "AdapterHealthSparkBucket",
    "adapter_health_feature_enabled",
    "render_adapter_health_panel",
)
_AVAILABILITY_MONITOR_EXPORTS = (
    "AVAILABILITY_MONITOR_FEATURE",
    "AvailabilityEventRow",
    "AvailabilityMonitorRow",
    "AvailabilityMonitorSurfaceConfig",
    "AvailabilityPolicyRow",
    "AvailabilityScenarioRow",
    "AvailabilityWindowRow",
    "availability_monitor_feature_enabled",
    "render_availability_monitor_surface",
)
_ADMIN_LIST_EXPORTS = (
    "ADMIN_LIST_FEATURE",
    "AdminListCell",
    "AdminListColumn",
    "AdminListFilterField",
    "AdminListPagination",
    "AdminListRow",
    "AdminListSurfaceConfig",
    "admin_list_surface_feature_enabled",
    "render_admin_list_surface",
)
_ADMIN_AUTH_PAGE_EXPORTS = (
    "AdminAuthLink",
    "AdminAuthSummaryItem",
    "AdminLoginPageConfig",
    "AdminPasswordChangePageConfig",
    "render_admin_login_page",
    "render_admin_password_change_page",
)
_DETAIL_DOSSIER_EXPORTS = (
    "DETAIL_DOSSIER_FEATURE",
    "DetailDossierActionSlot",
    "DetailDossierAuditRow",
    "DetailDossierField",
    "DetailDossierHeader",
    "DetailDossierMetric",
    "DetailDossierRelatedLink",
    "DetailDossierSection",
    "DetailDossierSourceTable",
    "DetailDossierSurfaceConfig",
    "DetailDossierTableCell",
    "DetailDossierTableColumn",
    "DetailDossierTableRow",
    "DetailDossierTimelineEvent",
    "detail_dossier_surface_feature_enabled",
    "render_detail_dossier_surface",
)
_MEDIA_LIBRARY_EXPORTS = (
    "MEDIA_LIBRARY_FEATURE",
    "MediaLibraryActionSlot",
    "MediaLibraryItem",
    "MediaLibraryMetadata",
    "MediaLibrarySurfaceConfig",
    "media_library_surface_feature_enabled",
    "render_media_library_surface",
)
_SURFACE_EXPORTS = (
    "ACTIVITY_FEATURE",
    "MEDIA_FEATURE",
    "MESSAGES_FEATURE",
    "ActivitySurfaceConfig",
    "MediaSurfaceConfig",
    "MessageSurfaceConfig",
    "message_surface_feature_enabled",
    "render_activity_surface",
    "render_media_surface",
    "render_message_surface",
    "render_surface_sections",
)
_PEOPLE_EXPORTS = (
    "PEOPLE_FEATURE",
    "PeopleSurfaceConfig",
    "PersonListRow",
    "PersonRelationshipSummary",
    "PersonTag",
    "people_surface_feature_enabled",
    "render_people_surface",
)
_REVIEW_EXPORTS = (
    "REVIEW_FEATURE",
    "ReviewAgendaItem",
    "ReviewBoardRow",
    "ReviewQueueCard",
    "ReviewQueueSection",
    "ReviewSurfaceConfig",
    "render_review_surface",
    "review_surface_feature_enabled",
)
_JOURNAL_EXPORTS = (
    "JOURNAL_FEATURE",
    "JOURNAL_THEME_KEYS",
    "JournalCalendarDay",
    "JournalDetail",
    "JournalEntry",
    "JournalMarker",
    "JournalSurfaceConfig",
    "JournalThemeOption",
    "build_journal_calendar",
    "journal_surface_feature_enabled",
    "journal_theme_key",
    "journal_theme_options",
    "render_journal_surface",
)
_PUBLIC_PRESENCE_EXPORTS = (
    "PUBLIC_PRESENCE_FEATURE",
    "PUBLIC_THEME_KEYS",
    "BrandAssets",
    "ChatPageConfig",
    "ConnectorGroup",
    "ConnectorOption",
    "LegalNotice",
    "LoginPageConfig",
    "PublicLink",
    "PublicMediaConfig",
    "PublicMediaSource",
    "PublicSettingsSurfaceConfig",
    "PublicSplashPageConfig",
    "PublicThemeOption",
    "public_presence_feature_enabled",
    "public_theme_options",
    "render_brand_logo",
    "render_chat_page",
    "render_connector_groups",
    "render_login_page",
    "render_public_media",
    "render_public_settings_surface",
    "render_public_splash_page",
)
_OPERATIONS_EXPORTS = (
    "AGENT_OPS_FEATURE",
    "OPERATIONS_FEATURE",
    "PERSONA_EDITOR_FEATURE",
    "PERSONA_RUNTIME_FEATURE",
    "TERMINAL_STREAM_FEATURE",
    "AgentOpsSurfaceConfig",
    "AgentSessionRow",
    "BridgeStatusCard",
    "ContinuityItem",
    "OperationsSurfaceConfig",
    "OpsLogEvent",
    "OpsSettingItem",
    "OpsStatusCard",
    "OpsTableRow",
    "PersonaChangeRow",
    "PersonaEditorConfig",
    "PersonaPanel",
    "PersonaProfileField",
    "PersonaProfileSection",
    "PersonaProposalCard",
    "PersonaRuleRow",
    "PersonaRuntimeSurfaceConfig",
    "PersonaStateField",
    "PersonaTraitRow",
    "SurfaceAction",
    "TerminalStreamConfig",
    "TerminalStreamEvent",
    "agent_ops_surface_feature_enabled",
    "operations_surface_feature_enabled",
    "persona_editor_feature_enabled",
    "persona_runtime_surface_feature_enabled",
    "render_agent_ops_surface",
    "render_operations_surface",
    "render_persona_editor",
    "render_persona_runtime_surface",
    "render_terminal_stream",
    "render_workflow_sections",
    "terminal_stream_feature_enabled",
)
_WORKER_OPERATIONS_EXPORTS = (
    "WORKER_OPERATIONS_FEATURE",
    "WorkerControlActionSlot",
    "WorkerDeadLetterRow",
    "WorkerDryRunCandidate",
    "WorkerOperationsSurfaceConfig",
    "WorkerProcessEvent",
    "WorkerReadinessRow",
    "WorkerRollbackCandidate",
    "WorkerRunTelemetryRow",
    "WorkerScheduleRow",
    "render_worker_operations_surface",
    "worker_operations_surface_feature_enabled",
)
_BRIDGE_OPS_EXPORTS = (
    "BRIDGE_OPS_FEATURE",
    "BridgeDeliveryRow",
    "BridgeHeartbeatRow",
    "BridgeOpsSurfaceConfig",
    "BridgeProviderCapabilityRow",
    "BridgeQueueRow",
    "BridgeStatusCard",
    "BridgeWebhookRow",
    "bridge_ops_feature_enabled",
    "render_bridge_ops_surface",
)
_COMMAND_INTAKE_EXPORTS = (
    "COMMAND_INTAKE_FEATURE",
    "CommandCandidateRow",
    "CommandConfirmationStep",
    "CommandHistoryRow",
    "CommandIntakeSurfaceConfig",
    "CommandParsedField",
    "CommandQueueRow",
    "CommandRiskRow",
    "command_intake_feature_enabled",
    "render_command_intake_surface",
)
_SETTINGS_EDITOR_EXPORTS = (
    "SETTINGS_EDITOR_FEATURE",
    "SettingsChange",
    "SettingsEditorConfig",
    "SettingsField",
    "SettingsGroup",
    "SettingsOption",
    "SettingsValidationMessage",
    "render_settings_editor",
    "settings_editor_feature_enabled",
)
_SYSTEM_HEALTH_EXPORTS = (
    "SYSTEM_HEALTH_FEATURE",
    "SystemAuditFilterState",
    "SystemAuditRow",
    "SystemDatabaseCard",
    "SystemHealthCheck",
    "SystemHealthGroup",
    "SystemHealthSurfaceConfig",
    "SystemPaginationState",
    "SystemReadinessProbe",
    "SystemSecretCoverageRow",
    "SystemSecretFilterState",
    "SystemSecretInventoryRow",
    "SystemTableSummary",
    "render_system_health_surface",
    "system_health_surface_feature_enabled",
)
_OWNER_PRIVATE_EXPORTS = (
    "OWNER_PRIVATE_ADMIN_FEATURE",
    "AdminPrivacyContext",
    "OwnerPrivateScopePolicy",
    "PrivacyRenderMode",
    "can_view_raw_private",
    "owner_private_scope_for_content",
    "privacy_render_mode",
    "render_private_text",
)
_RENDER_EXPORTS = (
    "LiveRefreshConfig",
    "NavGroup",
    "NavItem",
    "PersonaConsoleConfig",
    "live_refresh_attributes",
    "render_dashboard_sections",
    "render_live_region",
    "render_live_status",
    "render_shell_html",
)
_CONTROL_EXPORTS = (
    "FlashBanner",
    "StatusTab",
    "flash_query_params",
    "flash_url",
    "render_flash_banners",
    "render_status_tabs",
)


@dataclass(frozen=True)
class DoctorCheck:
    key: str
    ok: bool
    summary: str
    detail: str = ""


@dataclass(frozen=True)
class ModuleSnapshot:
    name: str
    imported: bool
    version: str = ""
    path: str = ""
    error: str = ""


@dataclass(frozen=True)
class ConsumerIntegrationDoctorReport:
    ok: bool
    expected_version: str = ""
    package_version: str = ""
    personaconsole: ModuleSnapshot = field(default_factory=lambda: ModuleSnapshot("personaconsole", False))
    persona_console_compat: ModuleSnapshot = field(default_factory=lambda: ModuleSnapshot("persona_console", False))
    personacore_compat: ModuleSnapshot = field(default_factory=lambda: ModuleSnapshot("personacore", False))
    checks: tuple[DoctorCheck, ...] = ()

    def as_dict(self, *, include_paths: bool = False) -> dict[str, Any]:
        data = asdict(self)
        if not include_paths:
            for key in ("personaconsole", "persona_console_compat", "personacore_compat"):
                if isinstance(data.get(key), dict):
                    data[key]["path"] = ""
        return data


def run_consumer_integration_doctor(
    *,
    expected_version: str = "",
    include_paths: bool = False,
) -> ConsumerIntegrationDoctorReport:
    """Run public-safe PersonaConsole integration checks for consumer runtimes."""

    checks: list[DoctorCheck] = []
    personaconsole = _module_snapshot("personaconsole", include_paths=include_paths)
    persona_console_compat = _module_snapshot("persona_console", include_paths=include_paths)
    personacore_compat = _module_snapshot("personacore", include_paths=include_paths)
    package_version = _distribution_version("personaconsole")

    checks.append(_check(personaconsole.imported, "personaconsole_import", "personaconsole importable", personaconsole.error))
    checks.append(
        _check(
            persona_console_compat.imported,
            "persona_console_compat_import",
            "legacy persona_console shim importable",
            persona_console_compat.error,
        )
    )
    checks.append(
        _check(
            personacore_compat.imported,
            "personacore_compat_import",
            "legacy personacore shim importable",
            personacore_compat.error,
        )
    )
    if personaconsole.imported and persona_console_compat.imported and personacore_compat.imported:
        checks.append(
            _check(
                personaconsole.version == persona_console_compat.version == personacore_compat.version,
                "legacy_shim_versions_match",
                f"legacy shims match canonical runtime {personaconsole.version or 'unknown'}",
                (
                    f"personaconsole={personaconsole.version or 'unknown'} "
                    f"persona_console={persona_console_compat.version or 'unknown'} "
                    f"personacore={personacore_compat.version or 'unknown'}"
                ),
            )
        )
    if expected_version and personaconsole.imported:
        checks.append(
            _check(
                personaconsole.version == expected_version,
                "expected_version_match",
                f"runtime version matches expected {expected_version}",
                f"personaconsole={personaconsole.version or 'unknown'}",
            )
        )
    if package_version and personaconsole.imported:
        checks.append(
            _check(
                package_version == personaconsole.version,
                "package_metadata_match",
                f"installed package metadata matches runtime {package_version}",
                f"package={package_version} runtime={personaconsole.version or 'unknown'}",
            )
        )
    if personaconsole.imported:
        module = importlib.import_module("personaconsole")
        checks.extend(_export_checks(module, "adapter_health_exports", _ADAPTER_HEALTH_EXPORTS))
        checks.extend(_export_checks(module, "availability_monitor_exports", _AVAILABILITY_MONITOR_EXPORTS))
        checks.extend(_export_checks(module, "admin_list_exports", _ADMIN_LIST_EXPORTS))
        checks.extend(_export_checks(module, "admin_auth_page_exports", _ADMIN_AUTH_PAGE_EXPORTS))
        checks.extend(_export_checks(module, "detail_dossier_exports", _DETAIL_DOSSIER_EXPORTS))
        checks.extend(_export_checks(module, "media_library_exports", _MEDIA_LIBRARY_EXPORTS))
        checks.extend(_export_checks(module, "token_health_exports", _TOKEN_HEALTH_EXPORTS))
        checks.extend(_export_checks(module, "surface_exports", _SURFACE_EXPORTS))
        checks.extend(_export_checks(module, "people_exports", _PEOPLE_EXPORTS))
        checks.extend(_export_checks(module, "review_exports", _REVIEW_EXPORTS))
        checks.extend(_export_checks(module, "journal_exports", _JOURNAL_EXPORTS))
        checks.extend(_export_checks(module, "public_presence_exports", _PUBLIC_PRESENCE_EXPORTS))
        checks.extend(_export_checks(module, "operations_exports", _OPERATIONS_EXPORTS))
        checks.extend(_export_checks(module, "worker_operations_exports", _WORKER_OPERATIONS_EXPORTS))
        checks.extend(_export_checks(module, "bridge_ops_exports", _BRIDGE_OPS_EXPORTS))
        checks.extend(_export_checks(module, "command_intake_exports", _COMMAND_INTAKE_EXPORTS))
        checks.extend(_export_checks(module, "settings_editor_exports", _SETTINGS_EDITOR_EXPORTS))
        checks.extend(_export_checks(module, "system_health_exports", _SYSTEM_HEALTH_EXPORTS))
        checks.extend(_export_checks(module, "owner_private_exports", _OWNER_PRIVATE_EXPORTS))
        checks.extend(_export_checks(module, "render_exports", _RENDER_EXPORTS))
        checks.extend(_export_checks(module, "control_exports", _CONTROL_EXPORTS))
        checks.append(_adapter_health_render_check(module))
        checks.append(_availability_monitor_render_check(module))
        checks.append(_admin_list_render_check(module))
        checks.append(_admin_auth_page_render_check(module))
        checks.append(_detail_dossier_render_check(module))
        checks.append(_media_library_render_check(module))
        checks.append(_token_health_render_check(module))
        checks.append(_controls_render_check(module))
        checks.append(_surface_render_check(module))
        checks.append(_people_render_check(module))
        checks.append(_review_render_check(module))
        checks.append(_journal_render_check(module))
        checks.append(_public_presence_render_check(module))
        checks.append(_operations_render_check(module))
        checks.append(_worker_operations_render_check(module))
        checks.append(_persona_editor_render_check(module))
        checks.append(_bridge_ops_render_check(module))
        checks.append(_command_intake_render_check(module))
        checks.append(_settings_editor_render_check(module))
        checks.append(_system_health_render_check(module))
        checks.append(_owner_private_render_check(module))
        checks.append(_shell_render_check(module))

    report_checks = tuple(checks)
    return ConsumerIntegrationDoctorReport(
        ok=all(check.ok for check in report_checks),
        expected_version=expected_version,
        package_version=package_version,
        personaconsole=personaconsole,
        persona_console_compat=persona_console_compat,
        personacore_compat=personacore_compat,
        checks=report_checks,
    )


def doctor_report_to_text(report: ConsumerIntegrationDoctorReport, *, include_paths: bool = False) -> str:
    data = report.as_dict(include_paths=include_paths)
    lines = [f"PersonaConsole consumer integration doctor: {'ok' if report.ok else 'failed'}"]
    for module_key in ("personaconsole", "persona_console_compat", "personacore_compat"):
        module = data[module_key]
        version = module.get("version") or "unknown"
        source = f" ({module.get('path')})" if module.get("path") else ""
        status = "ok" if module.get("imported") else "failed"
        lines.append(f"- {module_key}: {status} version={version}{source}")
    if data.get("package_version"):
        lines.append(f"- package metadata: personaconsole {data['package_version']}")
    for check in data["checks"]:
        status = "ok" if check["ok"] else "failed"
        detail = f" [{check['detail']}]" if check.get("detail") else ""
        lines.append(f"- {check['key']}: {status} - {check['summary']}{detail}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run PersonaConsole consumer integration checks.")
    parser.add_argument("--expected-version", default="", help="Expected PersonaConsole runtime version.")
    parser.add_argument("--json", action="store_true", help="Print JSON instead of text.")
    parser.add_argument("--show-paths", action="store_true", help="Include imported module filesystem paths.")
    args = parser.parse_args(argv)

    report = run_consumer_integration_doctor(
        expected_version=args.expected_version,
        include_paths=args.show_paths,
    )
    if args.json:
        print(json.dumps(report.as_dict(include_paths=args.show_paths), indent=2, sort_keys=True))
    else:
        print(doctor_report_to_text(report, include_paths=args.show_paths))
    return 0 if report.ok else 1


def _module_snapshot(name: str, *, include_paths: bool) -> ModuleSnapshot:
    try:
        module = importlib.import_module(name)
    except Exception as exc:
        return ModuleSnapshot(name=name, imported=False, error=f"{exc.__class__.__name__}: {exc}")
    path = str(Path(getattr(module, "__file__", "") or "")) if include_paths else ""
    return ModuleSnapshot(
        name=name,
        imported=True,
        version=str(getattr(module, "__version__", "") or ""),
        path=path,
    )


def _distribution_version(name: str) -> str:
    try:
        return importlib.metadata.version(name)
    except importlib.metadata.PackageNotFoundError:
        return ""


def _check(ok: bool, key: str, summary: str, detail: str = "") -> DoctorCheck:
    return DoctorCheck(key=key, ok=bool(ok), summary=summary, detail=detail)


def _export_checks(module: Any, group: str, names: Sequence[str]) -> list[DoctorCheck]:
    return [
        _check(
            hasattr(module, name),
            f"{group}.{name}",
            f"{name} exported",
        )
        for name in names
    ]


def _token_health_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-secret"
    try:
        config = module.token_health_config_for_providers("discord", show_secret_names=False)
        report = module.build_token_health_report(config, values={"DISCORD_TOKEN": raw_value})
        html = module.render_token_health_panel(report)
    except Exception as exc:
        return _check(False, "token_health_render", "token health render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        report.get("ok") is True
        and report.get("enabled") is True
        and "pc-token-health" in html
        and "Discord bot token" in html
        and raw_value not in str(report)
        and raw_value not in html
    )
    return _check(ok, "token_health_render", "token health report and panel render without raw values")


def _adapter_health_render_check(module: Any) -> DoctorCheck:
    try:
        html = module.render_adapter_health_panel(
            module.AdapterHealthConfig(
                enabled=True,
                cards=[
                    module.AdapterHealthCard(
                        "Messages",
                        "healthy",
                        route="inbound/outbound",
                        policy="runtime-owned policy",
                        last_in="1m ago",
                        last_out="2m ago",
                        counts=[{"label": "0 failed", "tone": "good"}],
                        sparkline=[module.AdapterHealthSparkBucket("now", 75, tone="good")],
                    )
                ],
            )
        )
    except Exception as exc:
        return _check(False, "adapter_health_render", "adapter health render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-adapter-health" in html
        and "Messages" in html
        and "0 failed" in html
        and "runtime-owned policy" in html
    )
    return _check(ok, "adapter_health_render", "adapter health panel renders generic runtime cards")


def _availability_monitor_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-availability"
    raw_url = "/doctor/private-availability"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_availability_monitor_surface(
            module.AvailabilityMonitorSurfaceConfig(
                enabled=True,
                tabs=[module.StatusTab("Live", "/availability", 2, active=True, tone="good")],
                metrics=[module.DashboardMetric("Open windows", 1, "/availability/windows", "active", tone="good")],
                windows=[
                    module.AvailabilityWindowRow(
                        "private-window",
                        "Private window",
                        "open",
                        "good",
                        "09:00",
                        "17:00",
                        "UTC",
                        "weekday",
                        "chat",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe availability window",
                    )
                ],
                monitors=[
                    module.AvailabilityMonitorRow("queue", "Queue latency", "healthy", "good", "12s", "30s", "1m ago", "2m"),
                ],
                policies=[
                    module.AvailabilityPolicyRow("review", "Review gate", "active", "good", "operator confirmation", "Required for risky sends."),
                ],
                scenarios=[
                    module.AvailabilityScenarioRow(
                        "private-scenario",
                        "Private scenario",
                        "review",
                        "warn",
                        "preflight",
                        "hold",
                        "08:30",
                        "10:00",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe availability scenario",
                    )
                ],
                events=[
                    module.AvailabilityEventRow(
                        "private-event",
                        "Private event",
                        "held",
                        "warn",
                        "09:10",
                        "monitor",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe availability event",
                    )
                ],
                actions=[module.SurfaceAction("Refresh", "/availability/refresh", "info", method="post")],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "availability_monitor_render", "availability monitor render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-availability-monitor-surface" in html
        and "Schedule Windows" in html
        and "Live Monitors" in html
        and "Policy Posture" in html
        and "Scenario QA" in html
        and "Monitor Events" in html
        and "safe availability window" in html
        and "safe availability scenario" in html
        and "safe availability event" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "availability_monitor_render", "availability monitor renders schedule, policy, scenario, and redaction")


def _admin_list_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-admin-list"
    raw_url = "/doctor/private-admin-list"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_admin_list_surface(
            module.AdminListSurfaceConfig(
                enabled=True,
                key="admin-list-doctor",
                title="Generic List",
                subtitle="Doctor smoke",
                columns=[
                    module.AdminListColumn("name", "Name", href="/list?sort=name", sortable=True, active=True, direction="asc"),
                    module.AdminListColumn("status", "Status"),
                    module.AdminListColumn("summary", "Summary"),
                ],
                status_tabs=[module.StatusTab("All", "/list", 2, active=True)],
                filters=[module.DashboardFilter("Ready", "/list?status=ready", key="ready", active=True)],
                filter_fields=[
                    module.AdminListFilterField("q", "Search", "example", "search"),
                    module.AdminListFilterField("status", "Status", "ready", "select", options=["ready", "held"]),
                ],
                filter_action="/list",
                metrics=[module.DashboardMetric("Rows", 2, "/list", "visible", tone="good")],
                actions=[module.SurfaceAction("Create", "/list/new", "good")],
                rows=[
                    module.AdminListRow(
                        "public",
                        cells=[
                            module.AdminListCell("name", "Example row", href="/list/public"),
                            module.AdminListCell("status", "ready", tone="good", badges=["configured"]),
                            module.AdminListCell("summary", "Public row summary"),
                        ],
                        actions=[module.SurfaceAction("Open", "/list/public")],
                    ),
                    module.AdminListRow(
                        "private",
                        cells=[
                            module.AdminListCell("name", "Private row"),
                            module.AdminListCell("status", "held", tone="warn"),
                            module.AdminListCell(
                                "summary",
                                raw_value,
                                href=raw_url,
                                privacy_scope="owner_private",
                                safe_alternate="safe admin list summary",
                            ),
                        ],
                    ),
                ],
                pagination=module.AdminListPagination(count=2, page=1, page_count=1),
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "admin_list_render", "admin list surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-admin-list-surface" in html
        and "Generic List" in html
        and "pc-admin-list-filter-form" in html
        and "pc-admin-list-table" in html
        and "pc-admin-list-cards" in html
        and "safe admin list summary" in html
        and "Page 1 of 1" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "admin_list_render", "generic admin list renders controls, rows, cards, and redaction")


def _admin_auth_page_render_check(module: Any) -> DoctorCheck:
    raw_value = "<script>raw-doctor-admin-auth</script>"
    private_host = "private-auth.example"
    try:
        brand = module.BrandAssets(
            name="Example Runtime",
            small_logo_url=f"https://{private_host}/logo.svg",
            home_url=f"https://{private_host}/",
        )
        login = module.render_admin_login_page(
            module.AdminLoginPageConfig(
                brand=brand,
                title="Admin Login",
                subtitle="Operator session required.",
                form_action=f"https://{private_host}/login",
                next_path=f"https://{private_host}/runtime",
                username_value=raw_value,
                status_message=raw_value,
                summary_items=[
                    module.AdminAuthSummaryItem("Session", "required", "info", raw_value),
                ],
                help_links=[module.AdminAuthLink("Help", "/help")],
            )
        )
        password = module.render_admin_password_change_page(
            module.AdminPasswordChangePageConfig(
                brand=brand,
                subject_label=raw_value,
                next_path="/runtime",
                min_length=8,
                disabled=True,
                status_message="Password challenge expired.",
            )
        )
    except Exception as exc:
        return _check(
            False,
            "admin_auth_page_render",
            "admin auth page render failed",
            f"{exc.__class__.__name__}: {exc}",
        )
    html = login + password
    ok = (
        "pc-admin-auth-page" in html
        and "pc-admin-login-page" in login
        and "pc-admin-password-change-page" in password
        and 'action="/login"' in login
        and 'value="/"' in login
        and 'action="/login/password-change"' in password
        and 'value="/runtime"' in password
        and 'minlength="8"' in password
        and " disabled" in password
        and "JavaScript is not required" in html
        and "&lt;script&gt;raw-doctor-admin-auth&lt;/script&gt;" in html
        and raw_value not in html
        and private_host not in html
    )
    return _check(ok, "admin_auth_page_render", "admin auth login and password-change pages render safely")


def _detail_dossier_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-detail-dossier"
    raw_url = "/doctor/private-detail-dossier"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_detail_dossier_surface(
            module.DetailDossierSurfaceConfig(
                enabled=True,
                key="detail-dossier-doctor",
                header=module.DetailDossierHeader(
                    title="Example Detail",
                    subtitle="Doctor smoke",
                    entity_type="Runtime Entity",
                    status="ready",
                    tone="good",
                ),
                fields=[
                    module.DetailDossierField("key", "Key", "example", mono=True),
                    module.DetailDossierField(
                        "private",
                        "Private",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe detail value",
                    ),
                ],
                metrics=[module.DetailDossierMetric("events", "Events", 3, "recent", tone="info")],
                sections=[
                    module.DetailDossierSection(
                        "overview",
                        "Overview",
                        body="Public overview",
                    )
                ],
                source_tables=[
                    module.DetailDossierSourceTable(
                        "sources",
                        "Sources",
                        columns=["kind", "summary"],
                        rows=[
                            module.DetailDossierTableRow(
                                "private",
                                cells=[
                                    module.DetailDossierTableCell("kind", "note"),
                                    module.DetailDossierTableCell(
                                        "summary",
                                        raw_value,
                                        href=raw_url,
                                        privacy_scope="owner_private",
                                        safe_alternate="safe table value",
                                    ),
                                ],
                            )
                        ],
                    )
                ],
                timeline=[
                    module.DetailDossierTimelineEvent(
                        "private",
                        "Private",
                        "now",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe timeline value",
                    )
                ],
                related_links=[module.DetailDossierRelatedLink("open", "Open", "/detail/open", "related")],
                audit_rows=[
                    module.DetailDossierAuditRow(
                        "private",
                        "Private Audit",
                        raw_value,
                        privacy_scope="owner_private",
                        safe_alternate="safe audit value",
                    )
                ],
                action_slots=[module.DetailDossierActionSlot("actions", "Actions", body="Operator actions")],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "detail_dossier_render", "detail dossier surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-detail-dossier-surface" in html
        and "Example Detail" in html
        and "pc-detail-dossier-table" in html
        and "safe detail value" in html
        and "safe table value" in html
        and "safe timeline value" in html
        and "safe audit value" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "detail_dossier_render", "detail dossier renders fields, tables, timeline, audit, slots, and redaction")


def _media_library_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-media-library"
    raw_url = "/doctor/private-media-library"
    unsafe_url = "https://private.example/media-library"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_media_library_surface(
            module.MediaLibrarySurfaceConfig(
                enabled=True,
                title="Media Library",
                view="grid",
                status_tabs=[module.StatusTab("All", "/media", 2, active=True)],
                filters=[module.DashboardFilter("Images", "/media?type=image", key="images", active=True)],
                view_options=[
                    module.DashboardFilter("Grid", "/media?view=grid", key="grid"),
                    module.DashboardFilter("List", "/media?view=list", key="list"),
                ],
                metrics=[module.DashboardMetric("Assets", 2, "/media", "visible")],
                actions=[module.SurfaceAction("Upload", "/media/upload")],
                action_slots=[
                    module.MediaLibraryActionSlot(
                        "import",
                        "Import",
                        "Consumer-owned import route",
                        actions=[module.SurfaceAction("Import file", "/media/import")],
                    )
                ],
                items=[
                    module.MediaLibraryItem(
                        "public",
                        "Public artifact",
                        href="/media/public",
                        preview_url="/media/public.jpg",
                        media_type="image",
                        status="ready",
                        review_status="approved",
                        safety="safe",
                        sendability="sendable",
                        source="upload",
                    ),
                    module.MediaLibraryItem(
                        "private",
                        raw_value,
                        href=raw_url,
                        preview_url=raw_url,
                        media_type="image",
                        detail=raw_value,
                        privacy_scope="owner_private",
                        safe_alternate="safe media library summary",
                        metadata=[
                            module.MediaLibraryMetadata(
                                "note",
                                "Note",
                                raw_value,
                                privacy_scope="owner_private",
                                safe_alternate="safe media metadata",
                            )
                        ],
                        actions=[module.SurfaceAction("Unsafe", unsafe_url)],
                    ),
                ],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "media_library_render", "media library surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-media-library-surface" in html
        and "pc-media-library-grid" in html
        and "pc-media-library-dialog" in html
        and "pc-media-library-action-slot" in html
        and "safe media library summary" in html
        and "safe media metadata" in html
        and raw_value not in html
        and raw_url not in html
        and unsafe_url not in html
    )
    return _check(ok, "media_library_render", "media library renders gallery controls, action slots, previews, and redaction")


def _controls_render_check(module: Any) -> DoctorCheck:
    try:
        tabs_html = module.render_status_tabs(
            [
                module.StatusTab("All", "/review", 8, active=True),
                module.StatusTab("Pending", "/review?status=pending", 3, tone="warn"),
            ],
        )
        flash_html = module.render_flash_banners(
            [
                module.FlashBanner(
                    "Saved",
                    tone="good",
                    action_label="View",
                    action_href="/review?saved=1",
                )
            ],
        )
        flash_href = module.flash_url("/review?tab=all#queue", "Saved", level="warn", timestamp=123)
    except Exception as exc:
        return _check(False, "controls_render", "shared controls render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-status-tabs" in tabs_html
        and "status-tabs" in tabs_html
        and "pc-status-tab" in tabs_html
        and "status-tab-count" in tabs_html
        and "/review?status=pending" in tabs_html
        and "Pending" in tabs_html
        and "pc-flash-stack" in flash_html
        and "pc-flash-banner" in flash_html
        and "pc-flash-action" in flash_html
        and "flash_level=warn" in flash_href
        and "flash_ts=123" in flash_href
        and flash_href.endswith("#queue")
    )
    return _check(ok, "controls_render", "shared controls render status tabs and flash banners")


def _surface_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-message"
    raw_url = "/doctor/raw-private-media"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_surface_sections(
            messages=module.MessageSurfaceConfig(
                enabled=True,
                filters=[
                    module.DashboardFilter("All", "/messages", key="1", active=True),
                ],
                metrics=[
                    module.DashboardMetric("Threads", 1, "/messages", "doctor"),
                ],
                actions=[
                    module.DashboardAction("Raw rows", "/messages?view=raw"),
                ],
                conversations=[
                    module.MessageConversation(
                        "one",
                        "Example thread",
                        summary=raw_value,
                        safe_alternate="safe thread summary",
                        privacy_scope="owner_private",
                    )
                ],
                transcript=[
                    module.MessageTranscriptItem(
                        "Example",
                        raw_value,
                        safe_alternate="safe message summary",
                        privacy_scope="owner_private",
                    )
                ],
                conversation_title="Threads",
                transcript_title="Selected thread",
                transcript_meta="doctor smoke",
            ),
            media=module.MediaSurfaceConfig(
                enabled=True,
                cards=[
                    module.MediaArtifactCard(
                        raw_value,
                        href=raw_url,
                        preview_url=raw_url + ".png",
                        safe_alternate="safe media summary",
                        privacy_scope="owner_private",
                    )
                ],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "surface_render", "message/activity/media surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-message-surface" in html
        and "pc-message-controls" in html
        and "pc-message-metrics" in html
        and "Selected thread" in html
        and "pc-media-surface" in html
        and "safe thread summary" in html
        and "safe message summary" in html
        and "safe media summary" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "surface_render", "message and media surfaces render with owner-private redaction")


def _people_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-people-note"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_people_surface(
            module.PeopleSurfaceConfig(
                enabled=True,
                search_action="/people",
                rows=[
                    module.PersonListRow(
                        "person",
                        "Example person",
                        external_id="CN0001",
                        trust_label="internal",
                        trust_tone="info",
                        linked_users=1,
                        tags=[module.PersonTag("supportive", tone="good")],
                        relationship=module.PersonRelationshipSummary(
                            label="Persona",
                            score="+42",
                            tone="good",
                            score_percent=71,
                            lanes=[module.PersonTag("trusted", tone="info")],
                        ),
                        notes="Public note summary",
                    ),
                    module.PersonListRow(
                        "owner-private",
                        "Owner private",
                        notes=raw_value,
                        notes_safe_alternate="safe people summary",
                        notes_privacy_scope="owner_private",
                    ),
                ],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "people_render", "people surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-people-surface" in html
        and "Example person" in html
        and "safe people summary" in html
        and "+42" in html
        and raw_value not in html
    )
    return _check(ok, "people_render", "people surface renders with owner-private redaction")


def _review_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-review-summary"
    raw_url = "/doctor/raw-private-review"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_review_surface(
            module.ReviewSurfaceConfig(
                enabled=True,
                filters=[module.DashboardFilter("All", "/review", key="1", active=True)],
                metrics=[module.DashboardMetric("Pending", 1, "/review", "doctor", tone="warn")],
                rows=[
                    module.ReviewBoardRow(
                        "message",
                        "held",
                        "messages:owner-private",
                        summary=raw_value,
                        summary_safe_alternate="safe review summary",
                        summary_privacy_scope="owner_private",
                        href=raw_url,
                        risk="bad",
                    )
                ],
                agenda=[
                    module.ReviewAgendaItem("Messages", 1, "/review/messages", "queue", "Inspect safe summary", "warn"),
                ],
                queue_sections=[
                    module.ReviewQueueSection(
                        "Queues",
                        cards=[
                            module.ReviewQueueCard(
                                "Owner private queue",
                                status="pending",
                                summary=raw_value,
                                summary_safe_alternate="safe queue summary",
                                summary_privacy_scope="owner_private",
                                href=raw_url,
                            )
                        ],
                    )
                ],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "review_render", "review surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-review-surface" in html
        and "Decision Board" in html
        and "safe review summary" in html
        and "safe queue summary" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "review_render", "review surface renders with owner-private redaction")


def _journal_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-journal"
    raw_url = "/doctor/raw-private-journal"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_journal_surface(
            module.JournalSurfaceConfig(
                enabled=True,
                title="Journal",
                subtitle="Doctor smoke",
                month_label="2026-06",
                previous_month_href="/journal?month=2026-05",
                next_month_href="/journal?month=2026-07",
                calendar=[
                    module.JournalCalendarDay(
                        "2026-06-24",
                        24,
                        href=raw_url,
                        has_entry=True,
                        selected=True,
                        privacy_scope="owner_private",
                    )
                ],
                entry=module.JournalEntry(
                    "doctor",
                    "2026-06-24",
                    raw_value,
                    raw_value,
                    href=raw_url,
                    subtitle=raw_value,
                    previous_href=raw_url + "-prev",
                    next_href=raw_url + "-next",
                    details=[module.JournalDetail("Source", raw_value)],
                    actions=[module.SurfaceAction("Open raw", raw_url, method="post")],
                    privacy_scope="owner_private",
                    safe_alternate="safe journal page",
                ),
                theme="night-ink",
                theme_options=module.journal_theme_options("night-ink"),
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "journal_render", "journal surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-journal-surface" in html
        and "pc-journal-theme-night-ink" in html
        and "safe journal page" in html
        and "pc-journal-calendar-day" in html
        and len(module.JOURNAL_THEME_KEYS) >= 12
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "journal_render", "journal surface renders themed pages with owner-private redaction")


def _public_presence_render_check(module: Any) -> DoctorCheck:
    raw_value = "<script>raw-doctor-public-presence</script>"
    private_host = "private-login.example"
    try:
        brand = module.BrandAssets(
            name="Example Persona",
            small_logo_url="/assets/example-small.svg",
            large_logo_url="/assets/example-large.svg",
            wordmark_url="/assets/example-wordmark.svg",
            signature_text="public fixture",
        )
        connectors = [
            module.ConnectorGroup(
                "Connect",
                description="Provider-neutral connector choices",
                connectors=[
                    module.ConnectorOption(
                        "web_chat",
                        "Web chat",
                        href="/login/web-chat",
                        icon="chat",
                        status="Ready",
                        tone="good",
                        description=raw_value,
                        configured=True,
                    ),
                    module.ConnectorOption(
                        "social",
                        "Social",
                        action="connect",
                        icon="share",
                        status="Needs setup",
                        tone="warn",
                        configured=False,
                    ),
                ],
            )
        ]
        video = module.PublicMediaConfig(
            kind="video",
            sources=[module.PublicMediaSource("/media/example-hero.mp4", "video/mp4")],
            audio_src="/media/example-hero.mp3",
            poster_url="/media/example-poster.jpg",
        )
        splash = module.render_public_splash_page(
            module.PublicSplashPageConfig(
                brand=brand,
                title=raw_value,
                subtitle="Public fixture",
                description="Generic public homepage",
                media=video,
                chat_href="/chat",
                social_links=[module.PublicLink("Example social", "/social", external=False)],
                legal_notices=[module.LegalNotice("terms", "Terms", body="Generic legal copy.")],
            )
        )
        login = module.render_login_page(
            module.LoginPageConfig(
                brand=brand,
                title="Sign in",
                subtitle="Generic login pattern",
                connector_groups=connectors,
                email_action="/login/email",
                status_message=raw_value,
            )
        )
        chat = module.render_chat_page(
            module.ChatPageConfig(
                brand=brand,
                title="Chat",
                subtitle="Generic chat surface",
                connector_groups=connectors,
                settings_themes=module.public_theme_options("studio"),
            )
        )
        settings = module.render_public_settings_surface(
            module.PublicSettingsSurfaceConfig(
                enabled=True,
                brand=brand,
                splash_media=video,
                connector_groups=connectors,
                social_links=[module.PublicLink("Example social", "/social", external=False)],
                theme_options=module.public_theme_options("studio"),
            ),
            features={module.PUBLIC_PRESENCE_FEATURE: True},
        )
    except Exception as exc:
        return _check(
            False,
            "public_presence_render",
            "public presence surfaces render failed",
            f"{exc.__class__.__name__}: {exc}",
        )
    html = splash + login + chat + settings
    ok = (
        "pc-public-splash" in splash
        and "pc-public-login-page" in login
        and "pc-public-chat-shell" in chat
        and "pc-public-settings-surface" in settings
        and "persona-public.css" in splash
        and "persona-public.js" in chat
        and "pc-connector-option" in login
        and 'data-connector-configured="false"' in login
        and "pc-public-sound-toggle" in splash
        and "muted" in splash
        and "&lt;script&gt;raw-doctor-public-presence&lt;/script&gt;" in html
        and raw_value not in html
        and private_host not in html
        and len(module.PUBLIC_THEME_KEYS) >= 12
    )
    return _check(ok, "public_presence_render", "public splash, login, chat, and settings surfaces render safely")


def _operations_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-operations"
    raw_url = "/doctor/raw-private-operations"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_workflow_sections(
            operations=module.OperationsSurfaceConfig(
                enabled=True,
                status_cards=[
                    module.OpsStatusCard(
                        "Workers",
                        "lagging",
                        "/workers",
                        "Queue above target",
                        tone="warn",
                        actions=[module.SurfaceAction("Inspect", "/workers/inspect")],
                    )
                ],
                logs=[
                    module.OpsLogEvent(
                        "Privacy",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe operations log",
                    )
                ],
                settings=[module.OpsSettingItem("Webhook secret", "raw-doctor-secret", "configured", secret=True)],
            ),
            persona=module.PersonaRuntimeSurfaceConfig(
                enabled=True,
                panels=[
                    module.PersonaPanel(
                        raw_value,
                        summary=raw_value,
                        privacy_scope="owner_private",
                        safe_alternate="safe persona panel",
                    )
                ],
                continuity=[
                    module.ContinuityItem(
                        "Memory",
                        raw_value,
                        raw_value,
                        raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe continuity item",
                    )
                ],
            ),
            agent_ops=module.AgentOpsSurfaceConfig(
                enabled=True,
                bridges=[module.BridgeStatusCard("Webhook", "healthy", counts=[{"label": "0 failed", "tone": "good"}])],
                sessions=[
                    module.AgentSessionRow(
                        "session",
                        raw_value,
                        "held",
                        raw_url,
                        objective=raw_value,
                        privacy_scope="owner_private",
                        safe_alternate="safe agent session",
                    )
                ],
                terminal_stream=module.TerminalStreamConfig(
                    enabled=True,
                    events=[
                        module.TerminalStreamEvent(
                            "doctor-terminal",
                            raw_value,
                            "09:00",
                            "output",
                            privacy_scope="owner_private",
                            safe_alternate="safe terminal event",
                        )
                    ],
                    history_url="/agent-ops/sessions/doctor/history",
                    stream_url="/agent-ops/sessions/doctor/live",
                    has_more_before=True,
                ),
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(
            False,
            "operations_render",
            "operations/persona/agent surfaces render failed",
            f"{exc.__class__.__name__}: {exc}",
        )
    ok = (
        "pc-operations-surface" in html
        and "pc-persona-surface" in html
        and "pc-agent-ops-surface" in html
        and "pc-terminal-stream" in html
        and "safe operations log" in html
        and "safe persona panel" in html
        and "safe continuity item" in html
        and "safe agent session" in html
        and "safe terminal event" in html
        and "raw-doctor-secret" not in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "operations_render", "operations/persona/agent surfaces render with safe alternates")


def _worker_operations_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-worker-ops"
    raw_url = "/doctor/raw-private-worker-ops"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_worker_operations_surface(
            module.WorkerOperationsSurfaceConfig(
                enabled=True,
                metrics=[module.DashboardMetric("Workers", 2, detail="doctor fixture", tone="warn")],
                readiness=[
                    module.WorkerReadinessRow(
                        "reflection",
                        "Reflection worker",
                        "ready",
                        "good",
                        schedule_status="due soon",
                        next_run="2m",
                    )
                ],
                schedules=[module.WorkerScheduleRow("reflection-schedule", "reflection", "Reflection schedule", status="enabled", cadence="15m")],
                runs=[
                    module.WorkerRunTelemetryRow(
                        "run-private",
                        "reflection",
                        "failed",
                        "due",
                        "09:00",
                        error=raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe worker run failure",
                    )
                ],
                dead_letters=[
                    module.WorkerDeadLetterRow(
                        "dead-private",
                        "media",
                        "open",
                        "provider",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe dead letter reason",
                    )
                ],
                rollback_candidates=[
                    module.WorkerRollbackCandidate("rollback", "media", "dry_run", "resume", audit_id=42, reason="review rollback")
                ],
                dry_run_candidates=[
                    module.WorkerDryRunCandidate(
                        "dry-private",
                        "self_learn",
                        "capture",
                        "reflection",
                        "recorded",
                        summary=raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe dry-run candidate",
                    )
                ],
                process_events=[
                    module.WorkerProcessEvent(
                        "event-private",
                        "media",
                        "dead_letter",
                        "open",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe process event",
                    )
                ],
                action_slots=[
                    module.WorkerControlActionSlot(
                        "proposal",
                        "Queue Control Proposal",
                        "Runtime owns the post target.",
                        '<form action="/workers/proposals" method="post"><button>Queue</button></form>',
                    )
                ],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "worker_operations_render", "worker operations render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-worker-ops-surface" in html
        and "Reflection worker" in html
        and "Reflection schedule" in html
        and "safe worker run failure" in html
        and "safe dead letter reason" in html
        and "safe dry-run candidate" in html
        and "safe process event" in html
        and "Queue Control Proposal" in html
        and "/workers/proposals" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "worker_operations_render", "worker operations surface renders with safe alternates")


def _settings_editor_render_check(module: Any) -> DoctorCheck:
    raw_secret = "raw-doctor-settings-secret"
    try:
        html = module.render_settings_editor(
            module.SettingsEditorConfig(
                enabled=True,
                title="Runtime Settings",
                form_action="/settings/save",
                restart_required=True,
                banners=[module.FlashBanner("Settings saved.", tone="good", action_label="Audit", action_href="/settings/audit")],
                messages=[module.SettingsValidationMessage("One value needs review.", field_key="interval", tone="warn")],
                groups=[
                    module.SettingsGroup(
                        "runtime",
                        "Runtime",
                        "Runtime-owned settings",
                        fields=[
                            module.SettingsField("provider", "Provider", "provider", "select", "safe-provider", options=["safe-provider", "other-provider"]),
                            module.SettingsField(
                                "api_key",
                                "API key",
                                "api_key",
                                "secret",
                                raw_secret,
                                display_value="configured",
                                changed=True,
                                pending_display_value="new secret staged",
                                restart_required=True,
                                actions=[module.SurfaceAction("Reveal", "/settings/reveal/api-key")],
                            ),
                            module.SettingsField("interval", "Interval", "interval", "number", 15, pending_value=30, changed=True),
                        ],
                    )
                ],
            )
        )
    except Exception as exc:
        return _check(False, "settings_editor_render", "settings editor render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-settings-editor" in html
        and "Runtime Settings" in html
        and "Pending Changes" in html
        and "restart required" in html
        and "configured" in html
        and "new secret staged" not in html
        and raw_secret not in html
        and 'value="30"' in html
        and "/settings/reveal/api-key" in html
    )
    return _check(ok, "settings_editor_render", "settings editor renders redacted changed settings")


def _persona_editor_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-persona-editor"
    raw_secret = "raw-doctor-persona-state-secret"
    raw_url = "/doctor/private-persona-editor"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_persona_editor(
            module.PersonaEditorConfig(
                enabled=True,
                tabs=[
                    module.StatusTab("All", "/persona/editor", 7, active=True),
                    module.StatusTab("Pending", "/persona/editor?status=pending", 2, tone="warn"),
                ],
                profile_sections=[
                    module.PersonaProfileSection(
                        "profile",
                        "Profile",
                        fields=[
                            module.PersonaProfileField("display", "Display", "Example Persona", status="approved", tone="good"),
                            module.PersonaProfileField(
                                "private-profile",
                                "Private profile",
                                raw_value,
                                href=raw_url,
                                privacy_scope="owner_private",
                                safe_alternate="safe persona profile",
                            ),
                        ],
                    )
                ],
                traits=[
                    module.PersonaTraitRow("tone", "Tone", "+4", "high", "approved", "good", "Public trait"),
                ],
                rules=[
                    module.PersonaRuleRow(
                        "private-rule",
                        "Private rule",
                        raw_value,
                        "owner",
                        1,
                        "pending-review",
                        "warn",
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe persona rule",
                    )
                ],
                state_fields=[
                    module.PersonaStateField(
                        "secret",
                        "State secret",
                        raw_secret,
                        pending_value="new-raw-doctor-persona-state-secret",
                        pending_display_value="new secret staged",
                        field_type="secret",
                        secret=True,
                        changed=True,
                    )
                ],
                proposals=[
                    module.PersonaProposalCard(
                        "proposal",
                        "Review proposal",
                        "pending-review",
                        "warn",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe persona proposal",
                        changes=[
                            module.PersonaChangeRow(
                                "private-change",
                                "Private change",
                                raw_value,
                                raw_value,
                                "held",
                                "bad",
                                privacy_scope="owner_private",
                                safe_alternate="safe persona change",
                            )
                        ],
                        actions=[module.SurfaceAction("Approve", "/persona/proposals/approve", "good", method="post")],
                    )
                ],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "persona_editor_render", "persona editor render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-persona-editor-surface" in html
        and "Profile" in html
        and "Traits" in html
        and "Rules" in html
        and "Mutable State" in html
        and "Proposals" in html
        and "safe persona profile" in html
        and "safe persona rule" in html
        and "safe persona proposal" in html
        and "safe persona change" in html
        and "new secret staged" in html
        and raw_value not in html
        and raw_secret not in html
        and "new-raw-doctor-persona-state-secret" not in html
        and raw_url not in html
    )
    return _check(ok, "persona_editor_render", "persona editor renders profile, rules, state, proposals, and redaction")


def _bridge_ops_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-bridge-delivery"
    raw_url = "/doctor/private-bridge-delivery"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_bridge_ops_surface(
            module.BridgeOpsSurfaceConfig(
                enabled=True,
                tabs=[module.StatusTab("All", "/bridge", 6, active=True)],
                metrics=[module.DashboardMetric("Failed", 1, "/bridge/failed", "needs review", tone="bad")],
                bridges=[
                    module.BridgeStatusCard(
                        "Webhook",
                        "healthy",
                        route="verify/reply",
                        counts=[{"label": "0 failed", "tone": "good"}],
                    )
                ],
                webhooks=[
                    module.BridgeWebhookRow("verify", "Verify endpoint", "healthy", "good", "POST", "/webhooks/example", "ok", "2m ago"),
                ],
                queues=[
                    module.BridgeQueueRow("inbound", "Inbound queue", "degraded", "warn", queued=4, failed=1, claimed=2, last_in="1m ago"),
                ],
                heartbeats=[
                    module.BridgeHeartbeatRow("worker", "Worker heartbeat", "stale", "warn", "worker-loop", "420ms", "14m ago"),
                ],
                providers=[
                    module.BridgeProviderCapabilityRow("chat", "Chat provider", "example-chat", "messages", "ready", "good", True, True, "/docs/chat"),
                ],
                deliveries=[
                    module.BridgeDeliveryRow(
                        "private",
                        "Private delivery",
                        "failed",
                        "bad",
                        "outbound",
                        "example-chat",
                        "private-target",
                        3,
                        "09:05",
                        raw_value,
                        raw_url,
                        "owner_private",
                        "safe bridge delivery",
                    )
                ],
                actions=[module.SurfaceAction("Refresh", "/bridge/refresh", "info", method="post")],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "bridge_ops_render", "bridge ops render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-bridge-ops-surface" in html
        and "Verify endpoint" in html
        and "Inbound queue" in html
        and "Worker heartbeat" in html
        and "Chat provider" in html
        and "safe bridge delivery" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "bridge_ops_render", "bridge ops renders provider-neutral posture with owner-private redaction")


def _command_intake_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-command"
    raw_url = "/doctor/private-command"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_command_intake_surface(
            module.CommandIntakeSurfaceConfig(
                enabled=True,
                tabs=[module.StatusTab("Preview", "/commands", 1, active=True, tone="info")],
                metrics=[module.DashboardMetric("Queued", 2, "/commands/queue", "runtime owned", tone="warn")],
                form_action="/commands/preview",
                input_value=raw_value,
                input_privacy_scope="owner_private",
                input_safe_alternate="safe command prompt",
                parsed_fields=[
                    module.CommandParsedField("intent", "Intent", "adjust schedule", status="parsed", tone="good"),
                    module.CommandParsedField(
                        "private",
                        "Private parameter",
                        raw_value,
                        privacy_scope="owner_private",
                        safe_alternate="safe parsed value",
                    ),
                ],
                candidates=[
                    module.CommandCandidateRow(
                        "target",
                        "Example target",
                        "person",
                        "0.82",
                        "matched",
                        "info",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe candidate",
                    )
                ],
                risks=[
                    module.CommandRiskRow(
                        "policy",
                        "Policy check",
                        "medium",
                        "review",
                        "warn",
                        raw_value,
                        privacy_scope="owner_private",
                        safe_alternate="safe risk",
                    )
                ],
                confirmations=[
                    module.CommandConfirmationStep(
                        "operator",
                        "Operator confirmation",
                        "pending",
                        "warn",
                        "Required before queueing.",
                        actions=[module.SurfaceAction("Confirm", "/commands/confirm", "good", method="post")],
                    )
                ],
                queue=[
                    module.CommandQueueRow(
                        "queued",
                        "Queued command",
                        "queued",
                        "info",
                        raw_value,
                        "operator",
                        "example target",
                        "09:10",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe queued command",
                    )
                ],
                history=[
                    module.CommandHistoryRow(
                        "history",
                        "Previous command",
                        "completed",
                        "good",
                        raw_value,
                        "operator",
                        "example target",
                        "08:40",
                        "2s",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe command history",
                    )
                ],
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "command_intake_render", "command intake render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-command-intake-surface" in html
        and "Parsed Preview" in html
        and "Candidates" in html
        and "Risks" in html
        and "Confirmations" in html
        and "Queue" in html
        and "History" in html
        and "safe command prompt" in html
        and "safe parsed value" in html
        and "safe candidate" in html
        and "safe risk" in html
        and "safe queued command" in html
        and "safe command history" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "command_intake_render", "command intake renders preview, queue, history, and redaction")


def _system_health_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw-doctor-private-system-audit"
    raw_url = "/doctor/private-system-audit"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        html = module.render_system_health_surface(
            module.SystemHealthSurfaceConfig(
                enabled=True,
                tabs=[
                    module.StatusTab("All", "/system", 8, active=True),
                    module.StatusTab("Needs care", "/system?status=warn", 2, tone="warn"),
                ],
                metrics=[
                    module.DashboardMetric("Runtime", "ok", "/system/runtime", "shared render smoke", tone="good"),
                    module.DashboardMetric("Database", "degraded", "/system/database", "one table stale", tone="warn"),
                ],
                health_groups=[
                    module.SystemHealthGroup(
                        "runtime",
                        "Runtime",
                        status="degraded",
                        checks=[
                            module.SystemHealthCheck("admin", "Admin server", "healthy", summary="admin responds", required=True),
                            module.SystemHealthCheck("worker", "Worker queue", "lagging", tone="warn", summary="queue above target", blocked=True),
                        ],
                    )
                ],
                databases=[
                    module.SystemDatabaseCard(
                        "runtime-db",
                        "Runtime database",
                        "degraded",
                        database="runtime_db",
                        user="runtime_user",
                        host="internal",
                        schema_version="2026.06",
                        tables=12,
                        records="4.2k",
                        latency="42ms",
                        summary="Connection works; one table needs review.",
                    )
                ],
                tables=[
                    module.SystemTableSummary("messages", "healthy", schema="current", rows=128, owner="runtime", updated="2m ago"),
                    module.SystemTableSummary("audit_events", "stale", tone="warn", schema="current", rows=41, owner="admin", updated="1h ago"),
                ],
                secret_coverage=[
                    module.SystemSecretCoverageRow(
                        "providers",
                        "Provider secrets",
                        "missing",
                        tone="warn",
                        present=3,
                        missing=1,
                        required=4,
                        section="providers",
                        source="runtime",
                        import_status="needs import",
                        last_checked="1m ago",
                    ),
                ],
                secret_filters=module.SystemSecretFilterState(query="provider", section="providers", result_count=1, total_count=2, clear_href="/system/secrets"),
                secret_rows=[
                    module.SystemSecretInventoryRow(
                        "provider-token",
                        "Provider token",
                        section="providers",
                        source="runtime",
                        status="configured",
                        tone="good",
                        value_kind="secret",
                        present=True,
                        active=True,
                        import_status="imported",
                        last_checked="1m ago",
                    )
                ],
                secret_pagination=module.SystemPaginationState(page=1, page_count=2, total=2, limit=1, next_href="/system/secrets?page=2"),
                readiness=[
                    module.SystemReadinessProbe("schema", "Schema migration", "ready", checked_at="09:00"),
                    module.SystemReadinessProbe("token-scan", "Token scan", "blocked", tone="bad", summary="manual pass required", checked_at="09:01"),
                ],
                audit_rows=[
                    module.SystemAuditRow(
                        "private-audit",
                        "Private audit event",
                        "update",
                        "operator",
                        "held",
                        "09:02",
                        raw_value,
                        href=raw_url,
                        privacy_scope="owner_private",
                        safe_alternate="safe system audit summary",
                        entity="settings",
                        source="admin_console",
                    )
                ],
                audit_filters=module.SystemAuditFilterState(
                    query="private",
                    actor="operator",
                    action="update",
                    entity="settings",
                    source="admin_console",
                    status="held",
                    result_count=1,
                    total_count=4,
                    clear_href="/system/audit",
                ),
                audit_pagination=module.SystemPaginationState(page=1, page_count=1, total=1, limit=20),
            ),
            privacy_policy=policy,
            privacy_context=operator,
        )
    except Exception as exc:
        return _check(False, "system_health_render", "system health surface render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-system-health-surface" in html
        and "Runtime database" in html
        and "Secret Coverage" in html
        and "Values are never rendered here." in html
        and "Secret Rows" in html
        and "Showing 1 of 2 secret rows" in html
        and "Schema And Tables" in html
        and "Readiness" in html
        and "Showing 1 of 4 audit events" in html
        and "safe system audit summary" in html
        and raw_value not in html
        and raw_url not in html
    )
    return _check(ok, "system_health_render", "system health surface renders posture data with owner-private redaction")


def _owner_private_render_check(module: Any) -> DoctorCheck:
    raw_value = "raw owner-private text"
    try:
        policy = module.OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
        operator = module.AdminPrivacyContext(
            access_tier="operator",
            viewer_person_key="operator",
            allowed_scopes=("public", "operator"),
        )
        owner = module.AdminPrivacyContext(
            access_tier="owner_private",
            viewer_person_key="owner",
            allowed_scopes=("public", "operator", "owner_private"),
        )
        safe_text = module.render_private_text(
            raw_value,
            policy=policy,
            context=operator,
            scope="owner_private",
            safe_alternate="safe alternate",
        )
        owner_text = module.render_private_text(
            raw_value,
            policy=policy,
            context=owner,
            scope="owner_private",
            safe_alternate="safe alternate",
        )
    except Exception as exc:
        return _check(False, "owner_private_render", "owner-private render failed", f"{exc.__class__.__name__}: {exc}")
    ok = safe_text == "safe alternate" and owner_text == raw_value
    return _check(ok, "owner_private_render", "owner-private policy renders safe alternate and owner raw text")


def _shell_render_check(module: Any) -> DoctorCheck:
    try:
        html = module.render_shell_html(
            module.PersonaConsoleConfig(
                brand_name="Example Runtime",
                page_title="Doctor",
                page_subtitle="Integration smoke",
                active="dashboard",
                nav_groups=[
                    module.NavGroup(
                        label="Core",
                        items=(module.NavItem("Dashboard", "/"),),
                        key="core",
                    )
                ],
                app_version=module.__version__,
                live_refresh=module.LiveRefreshConfig(
                    enabled=True,
                    key="doctor",
                    url="/doctor/partial",
                    interval_seconds=15,
                    stale_after_seconds=60,
                    fallback_href="/doctor",
                ),
            ),
            "<main>doctor body</main>",
        )
    except Exception as exc:
        return _check(False, "shell_render", "shell render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "Example Runtime" in html
        and "doctor body" in html
        and "persona-console" in html
        and "data-pc-live-target" in html
        and 'data-pc-live-url="/doctor/partial"' in html
        and "pc-live-noscript" in html
    )
    return _check(ok, "shell_render", "shared shell renders generic body and live partial contract")


if __name__ == "__main__":
    raise SystemExit(main())
