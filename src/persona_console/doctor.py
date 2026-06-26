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
    "NavGroup",
    "NavItem",
    "PersonaConsoleConfig",
    "render_dashboard_sections",
    "render_shell_html",
)
_CONTROL_EXPORTS = (
    "StatusTab",
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
    persona_console: ModuleSnapshot = field(default_factory=lambda: ModuleSnapshot("persona_console", False))
    personacore: ModuleSnapshot = field(default_factory=lambda: ModuleSnapshot("personacore", False))
    checks: tuple[DoctorCheck, ...] = ()

    def as_dict(self, *, include_paths: bool = False) -> dict[str, Any]:
        data = asdict(self)
        if not include_paths:
            for key in ("persona_console", "personacore"):
                if isinstance(data.get(key), dict):
                    data[key]["path"] = ""
        return data


def run_consumer_integration_doctor(
    *,
    expected_version: str = "",
    include_paths: bool = False,
) -> ConsumerIntegrationDoctorReport:
    """Run public-safe PersonaCore integration checks for consumer runtimes."""

    checks: list[DoctorCheck] = []
    persona_console = _module_snapshot("persona_console", include_paths=include_paths)
    personacore = _module_snapshot("personacore", include_paths=include_paths)
    package_version = _distribution_version("personacore")

    checks.append(_check(persona_console.imported, "persona_console_import", "persona_console importable", persona_console.error))
    checks.append(_check(personacore.imported, "personacore_import", "personacore importable", personacore.error))
    if persona_console.imported and personacore.imported:
        checks.append(
            _check(
                persona_console.version == personacore.version,
                "runtime_versions_match",
                f"runtime versions match at {persona_console.version or 'unknown'}",
                f"persona_console={persona_console.version or 'unknown'} personacore={personacore.version or 'unknown'}",
            )
        )
    if expected_version and persona_console.imported and personacore.imported:
        checks.append(
            _check(
                persona_console.version == expected_version and personacore.version == expected_version,
                "expected_version_match",
                f"runtime version matches expected {expected_version}",
                f"persona_console={persona_console.version or 'unknown'} personacore={personacore.version or 'unknown'}",
            )
        )
    if package_version and personacore.imported:
        checks.append(
            _check(
                package_version == personacore.version,
                "package_metadata_match",
                f"installed package metadata matches runtime {package_version}",
                f"package={package_version} runtime={personacore.version or 'unknown'}",
            )
        )
    if personacore.imported:
        module = importlib.import_module("personacore")
        checks.extend(_export_checks(module, "adapter_health_exports", _ADAPTER_HEALTH_EXPORTS))
        checks.extend(_export_checks(module, "token_health_exports", _TOKEN_HEALTH_EXPORTS))
        checks.extend(_export_checks(module, "surface_exports", _SURFACE_EXPORTS))
        checks.extend(_export_checks(module, "people_exports", _PEOPLE_EXPORTS))
        checks.extend(_export_checks(module, "review_exports", _REVIEW_EXPORTS))
        checks.extend(_export_checks(module, "owner_private_exports", _OWNER_PRIVATE_EXPORTS))
        checks.extend(_export_checks(module, "render_exports", _RENDER_EXPORTS))
        checks.extend(_export_checks(module, "control_exports", _CONTROL_EXPORTS))
        checks.append(_adapter_health_render_check(module))
        checks.append(_token_health_render_check(module))
        checks.append(_controls_render_check(module))
        checks.append(_surface_render_check(module))
        checks.append(_people_render_check(module))
        checks.append(_review_render_check(module))
        checks.append(_owner_private_render_check(module))
        checks.append(_shell_render_check(module))

    report_checks = tuple(checks)
    return ConsumerIntegrationDoctorReport(
        ok=all(check.ok for check in report_checks),
        expected_version=expected_version,
        package_version=package_version,
        persona_console=persona_console,
        personacore=personacore,
        checks=report_checks,
    )


def doctor_report_to_text(report: ConsumerIntegrationDoctorReport, *, include_paths: bool = False) -> str:
    data = report.as_dict(include_paths=include_paths)
    lines = [f"PersonaCore consumer integration doctor: {'ok' if report.ok else 'failed'}"]
    for module_key in ("persona_console", "personacore"):
        module = data[module_key]
        version = module.get("version") or "unknown"
        source = f" ({module.get('path')})" if module.get("path") else ""
        status = "ok" if module.get("imported") else "failed"
        lines.append(f"- {module_key}: {status} version={version}{source}")
    if data.get("package_version"):
        lines.append(f"- package metadata: personacore {data['package_version']}")
    for check in data["checks"]:
        status = "ok" if check["ok"] else "failed"
        detail = f" [{check['detail']}]" if check.get("detail") else ""
        lines.append(f"- {check['key']}: {status} - {check['summary']}{detail}")
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run PersonaCore consumer integration checks.")
    parser.add_argument("--expected-version", default="", help="Expected PersonaCore runtime version.")
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


def _controls_render_check(module: Any) -> DoctorCheck:
    try:
        html = module.render_status_tabs(
            [
                module.StatusTab("All", "/review", 8, active=True),
                module.StatusTab("Pending", "/review?status=pending", 3, tone="warn"),
            ],
        )
    except Exception as exc:
        return _check(False, "controls_render", "shared controls render failed", f"{exc.__class__.__name__}: {exc}")
    ok = (
        "pc-status-tabs" in html
        and "status-tabs" in html
        and "pc-status-tab" in html
        and "status-tab-count" in html
        and "/review?status=pending" in html
        and "Pending" in html
    )
    return _check(ok, "controls_render", "shared controls render status tabs")


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
            ),
            "<main>doctor body</main>",
        )
    except Exception as exc:
        return _check(False, "shell_render", "shell render failed", f"{exc.__class__.__name__}: {exc}")
    ok = "Example Runtime" in html and "doctor body" in html and "persona-console" in html
    return _check(ok, "shell_render", "shared shell renders generic body")


if __name__ == "__main__":
    raise SystemExit(main())
