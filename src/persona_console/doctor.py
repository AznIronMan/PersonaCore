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
        checks.extend(_export_checks(module, "owner_private_exports", _OWNER_PRIVATE_EXPORTS))
        checks.extend(_export_checks(module, "render_exports", _RENDER_EXPORTS))
        checks.append(_adapter_health_render_check(module))
        checks.append(_token_health_render_check(module))
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
