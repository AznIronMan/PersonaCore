from __future__ import annotations

from dataclasses import asdict, dataclass
from fnmatch import fnmatch
import argparse
import json
from pathlib import Path
import re
import sys
import tomllib
from typing import Any, Iterable, Mapping, Sequence


DEFAULT_SCAN_SUFFIXES = (
    ".cfg",
    ".css",
    ".html",
    ".ini",
    ".jinja",
    ".jinja2",
    ".js",
    ".json",
    ".md",
    ".py",
    ".toml",
    ".txt",
    ".yaml",
    ".yml",
)

DEFAULT_EXCLUDED_DIRS = {
    ".git",
    ".mypy_cache",
    ".private",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "env",
    "ENV",
    "htmlcov",
    "node_modules",
    "venv",
}

DEFAULT_EXCLUDED_PATH_PARTS = {
    ("data", "files"),
    ("data", "generated"),
    ("data", "uploads"),
    ("data", "kay_files"),
}

PRIVATE_FILE_NAMES = {
    ".env",
    ".env.local",
    ".env.production",
    ".envrc",
}

STATIC_ASSET_NAMES = {
    "persona-console.css",
    "persona-console.js",
    "persona-public.css",
    "persona-public.js",
}

LEGACY_PATTERNS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("legacy-personacore-import", re.compile(r"\b(?:from|import)\s+personacore\b")),
    ("legacy-persona-console-import", re.compile(r"\b(?:from|import)\s+persona_console\b")),
    ("legacy-personacore-requirement", re.compile(r"\bpersonacore\s*@")),
    ("legacy-persona-console-requirement", re.compile(r"\bpersona_console\s*@")),
)

FALLBACK_MARKERS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("local-shared-fallback", re.compile(r"\bshared surface fallback\b", re.IGNORECASE)),
    ("local-shared-fallback", re.compile(r"\blocal shared UI fallback\b", re.IGNORECASE)),
    ("local-shared-fallback", re.compile(r"\blocal fallback markup\b", re.IGNORECASE)),
    ("local-shared-fallback", re.compile(r"\bPersonaConsole\b.{0,80}\bunavailable\b", re.IGNORECASE)),
)

DUPLICATE_HELPER_PATTERN = re.compile(
    r"^\s*def\s+_(?:"
    r"table|sortable_table|filter_form|filter_tabs|pagination|pager|"
    r"nav_groups|nav_groups_html|badge_html|status_tabs|status_pill"
    r")\b"
)

SURFACE_REGISTRY_MARKERS = (
    "SurfaceRegistryConfig",
    "surface_registry_config",
    "surface_registry_status",
    "surface_composition",
    "render_surface_registry_report",
)


@dataclass(frozen=True)
class CutoverAuditFinding:
    key: str
    level: str
    message: str
    path: str = ""
    line: int = 0
    category: str = "shared-ui"
    snippet: str = ""

    def as_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CutoverAuditReport:
    root: str
    ok: bool
    finding_count: int
    error_count: int
    warning_count: int
    info_count: int
    scanned_file_count: int
    findings: tuple[CutoverAuditFinding, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "root": self.root,
            "ok": self.ok,
            "finding_count": self.finding_count,
            "error_count": self.error_count,
            "warning_count": self.warning_count,
            "info_count": self.info_count,
            "scanned_file_count": self.scanned_file_count,
            "findings": [finding.as_dict() for finding in self.findings],
        }


def _safe_rel(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.name


def _clip(value: object, limit: int = 160) -> str:
    text = " ".join(str(value or "").split())
    if len(text) <= limit:
        return text
    return text[: max(0, limit - 1)].rstrip() + "..."


def _is_excluded(path: Path, root: Path, excluded_dirs: set[str]) -> bool:
    rel = path.relative_to(root)
    parts = rel.parts
    if any(part in excluded_dirs for part in parts):
        return True
    if path.name in PRIVATE_FILE_NAMES or path.name.startswith(".env."):
        return True
    for excluded in DEFAULT_EXCLUDED_PATH_PARTS:
        if len(parts) >= len(excluded) and tuple(parts[: len(excluded)]) == excluded:
            return True
    return False


def _iter_scan_files(
    root: Path,
    *,
    suffixes: Sequence[str] = DEFAULT_SCAN_SUFFIXES,
    excluded_dirs: Iterable[str] = DEFAULT_EXCLUDED_DIRS,
) -> list[Path]:
    clean_suffixes = {str(suffix).lower() for suffix in suffixes}
    clean_excluded_dirs = {str(item) for item in excluded_dirs}
    files: list[Path] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        if _is_excluded(path, root, clean_excluded_dirs):
            continue
        if path.suffix.lower() not in clean_suffixes:
            continue
        files.append(path)
    return files


def _legacy_level(path: str) -> str:
    if path.startswith(("docs/", ".tasks/", "CHANGELOG", "README")):
        return "warn"
    return "error"


def _copied_static_asset(path: str) -> bool:
    if not path.endswith(tuple(STATIC_ASSET_NAMES)):
        return False
    return "/personaconsole/static/" not in path and not path.startswith("src/personaconsole/static/")


def _has_surface_registry_marker(texts: Iterable[str]) -> bool:
    return any(marker in text for text in texts for marker in SURFACE_REGISTRY_MARKERS)


def _finding_ignored(finding: CutoverAuditFinding, patterns: Sequence[str]) -> bool:
    if not patterns:
        return False
    targets = (
        finding.path,
        f"{finding.key}:{finding.path}",
        f"{finding.category}:{finding.path}",
        f"{finding.level}:{finding.path}",
        finding.key,
        finding.category,
    )
    return any(fnmatch(target, pattern) for pattern in patterns for target in targets)


def load_cutover_audit_ignore_patterns(path: str | Path | None) -> tuple[str, ...]:
    if not path:
        return ()
    ignore_path = Path(path)
    text = ignore_path.read_text(encoding="utf-8")
    if ignore_path.suffix.lower() == ".json":
        payload = json.loads(text)
        if isinstance(payload, Mapping):
            values = payload.get("ignore_patterns") or payload.get("ignores") or ()
        else:
            values = payload
        return tuple(str(item).strip() for item in values if str(item).strip())
    if ignore_path.suffix.lower() == ".toml":
        payload = tomllib.loads(text)
        values = payload.get("ignore_patterns") or payload.get("ignores")
        if values is None and isinstance(payload.get("cutover_audit"), Mapping):
            values = payload["cutover_audit"].get("ignore_patterns") or payload["cutover_audit"].get("ignores")
        return tuple(str(item).strip() for item in (values or ()) if str(item).strip())
    patterns = []
    for line in text.splitlines():
        clean = line.strip()
        if not clean or clean.startswith("#"):
            continue
        patterns.append(clean)
    return tuple(patterns)


def run_consumer_shared_ui_cutover_audit(
    root: str | Path = ".",
    *,
    ignore_patterns: Sequence[str] = (),
    ignore_file: str | Path | None = None,
    suffixes: Sequence[str] = DEFAULT_SCAN_SUFFIXES,
) -> CutoverAuditReport:
    base = Path(root).resolve()
    patterns = tuple(ignore_patterns) + load_cutover_audit_ignore_patterns(ignore_file)
    findings: list[CutoverAuditFinding] = []
    texts: list[str] = []
    files = _iter_scan_files(base, suffixes=suffixes)

    for path in files:
        rel = _safe_rel(path, base)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        texts.append(text)

        if _copied_static_asset(rel):
            findings.append(
                CutoverAuditFinding(
                    key="copied-static-asset",
                    level="warn",
                    category="static-assets",
                    path=rel,
                    message="PersonaConsole static asset appears copied into the consumer; prefer serving package assets.",
                )
            )

        for line_number, line in enumerate(text.splitlines(), start=1):
            for key, pattern in LEGACY_PATTERNS:
                if pattern.search(line):
                    findings.append(
                        CutoverAuditFinding(
                            key=key,
                            level=_legacy_level(rel),
                            category="legacy-import",
                            path=rel,
                            line=line_number,
                            message="Deprecated PersonaConsole compatibility name remains.",
                            snippet=_clip(line),
                        )
                    )
            for key, pattern in FALLBACK_MARKERS:
                if pattern.search(line):
                    findings.append(
                        CutoverAuditFinding(
                            key=key,
                            level="warn",
                            category="fallback",
                            path=rel,
                            line=line_number,
                            message="Local shared UI fallback marker remains; confirm it is archived or runtime-owned.",
                            snippet=_clip(line),
                        )
                    )
            if DUPLICATE_HELPER_PATTERN.search(line):
                findings.append(
                    CutoverAuditFinding(
                        key="duplicated-generic-helper",
                        level="warn",
                        category="generic-helper",
                        path=rel,
                        line=line_number,
                        message="Generic UI helper definition remains in consumer code; confirm it is runtime-specific or move it to PersonaConsole.",
                        snippet=_clip(line),
                    )
                )

    if not _has_surface_registry_marker(texts):
        findings.append(
            CutoverAuditFinding(
                key="missing-surface-registry",
                level="error",
                category="surface-registry",
                message="No PersonaConsole surface registry marker found in scanned files.",
            )
        )

    visible_findings = tuple(finding for finding in findings if not _finding_ignored(finding, patterns))
    error_count = sum(1 for finding in visible_findings if finding.level == "error")
    warning_count = sum(1 for finding in visible_findings if finding.level == "warn")
    info_count = sum(1 for finding in visible_findings if finding.level == "info")
    return CutoverAuditReport(
        root=str(base),
        ok=error_count == 0,
        finding_count=len(visible_findings),
        error_count=error_count,
        warning_count=warning_count,
        info_count=info_count,
        scanned_file_count=len(files),
        findings=visible_findings,
    )


def cutover_audit_report_to_text(report: CutoverAuditReport) -> str:
    lines = [
        f"PersonaConsole shared UI cutover audit: {'ok' if report.ok else 'failed'}",
        f"- scanned files: {report.scanned_file_count}",
        f"- findings: {report.finding_count} ({report.error_count} errors, {report.warning_count} warnings, {report.info_count} info)",
    ]
    for finding in report.findings:
        location = f"{finding.path}:{finding.line}" if finding.path and finding.line else finding.path
        prefix = f"- [{finding.level}] {finding.key}"
        detail = f"{prefix} {location} - {finding.message}".rstrip()
        if finding.snippet:
            detail += f" :: {finding.snippet}"
        lines.append(detail)
    return "\n".join(lines)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a public-safe PersonaConsole shared UI cutover audit for a consumer repo.")
    parser.add_argument("root", nargs="?", default=".", help="Consumer repository root to scan.")
    parser.add_argument("--ignore", action="append", default=(), help="Glob-style ignore pattern. Matches key:path, category:path, level:path, key, category, or path.")
    parser.add_argument("--ignore-file", default="", help="JSON, TOML, or line-based ignore file.")
    parser.add_argument("--json", action="store_true", help="Emit JSON.")
    parser.add_argument("--fail-on", choices=("error", "warning", "never"), default="error", help="Exit nonzero on errors, warnings, or never.")
    args = parser.parse_args(argv)

    report = run_consumer_shared_ui_cutover_audit(args.root, ignore_patterns=tuple(args.ignore or ()), ignore_file=args.ignore_file or None)
    if args.json:
        print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    else:
        print(cutover_audit_report_to_text(report))

    if args.fail_on == "never":
        return 0
    if args.fail_on == "warning" and (report.error_count or report.warning_count):
        return 1
    if args.fail_on == "error" and report.error_count:
        return 1
    return 0


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main(sys.argv[1:]))
