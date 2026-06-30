import json
import subprocess
import sys

from personaconsole.cutover_audit import (
    cutover_audit_report_to_text,
    run_consumer_shared_ui_cutover_audit,
)


def test_cutover_audit_passes_clean_consumer(tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    (tmp_path / "requirements.txt").write_text(
        "personaconsole @ https://github.com/AznIronMan/PersonaConsole/archive/refs/tags/v1.0.37.zip\n",
        encoding="utf-8",
    )
    (app / "admin.py").write_text(
        """
from personaconsole import SurfaceRegistryConfig, render_surface_registry_report

SURFACES = SurfaceRegistryConfig(enabled=True, surfaces=())

def render_admin():
    return render_surface_registry_report(SURFACES)
""",
        encoding="utf-8",
    )

    report = run_consumer_shared_ui_cutover_audit(tmp_path)

    assert report.ok is True
    assert report.finding_count == 0
    assert report.scanned_file_count == 2


def test_cutover_audit_detects_legacy_markers(tmp_path):
    app = tmp_path / "app"
    static = tmp_path / "static"
    app.mkdir()
    static.mkdir()
    (app / "admin.py").write_text(
        """
from personacore import render_shell_html

def _table(rows):
    return "PersonaConsole renderer unavailable; shared surface fallback"
""",
        encoding="utf-8",
    )
    (static / "persona-console.css").write_text("body { color: red; }\n", encoding="utf-8")

    report = run_consumer_shared_ui_cutover_audit(tmp_path)
    keys = {finding.key for finding in report.findings}
    text = cutover_audit_report_to_text(report)

    assert report.ok is False
    assert "legacy-personacore-import" in keys
    assert "duplicated-generic-helper" in keys
    assert "local-shared-fallback" in keys
    assert "copied-static-asset" in keys
    assert "missing-surface-registry" in keys
    assert str(tmp_path) not in text


def test_cutover_audit_ignore_file_suppresses_known_runtime_owned_findings(tmp_path):
    app = tmp_path / "app"
    app.mkdir()
    (app / "admin.py").write_text(
        """
from personaconsole import SurfaceRegistryConfig

def _table(rows):
    return "runtime-owned local table"
""",
        encoding="utf-8",
    )
    ignore = tmp_path / "cutover-ignore.txt"
    ignore.write_text("duplicated-generic-helper:app/admin.py\n", encoding="utf-8")

    report = run_consumer_shared_ui_cutover_audit(tmp_path, ignore_file=ignore)

    assert report.ok is True
    assert report.finding_count == 0


def test_cutover_audit_script_json(tmp_path):
    (tmp_path / "admin.py").write_text(
        "from personaconsole import SurfaceRegistryConfig\nSURFACES = SurfaceRegistryConfig(enabled=True)\n",
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            "scripts/consumer_shared_ui_cutover_audit.py",
            str(tmp_path),
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )
    payload = json.loads(result.stdout)

    assert payload["ok"] is True
    assert payload["finding_count"] == 0
