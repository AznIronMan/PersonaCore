from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "consumer_release_plan.py"


def _write_roster(path: Path) -> None:
    path.write_text(
        json.dumps(
            {
                "consumers": [
                    {
                        "key": "example",
                        "label": "Example Runtime",
                        "repo_path": "/private/example",
                        "task_system": "Use the runtime task tracker.",
                        "persona_console_source": "Use public tag.",
                        "update_steps": ["Read AGENTS.md", "Update package pin"],
                        "tests": ["Run focused tests"],
                        "smokes": ["Smoke admin login"],
                        "restart_steps": ["Restart admin service"],
                        "rollback": ["Restore previous pin"],
                        "notes": ["Record result in the consumer task."],
                    }
                ]
            }
        ),
        encoding="utf-8",
    )


def test_consumer_release_plan_renders_roster_checklist(tmp_path: Path) -> None:
    roster = tmp_path / "roster.json"
    _write_roster(roster)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--roster",
            str(roster),
            "--version",
            "1.2.3",
            "--source",
            "public tag v1.2.3",
        ],
        cwd=ROOT,
        check=True,
        text=True,
        capture_output=True,
    )

    assert "# PersonaConsole 1.2.3 Consumer Propagation Plan" in result.stdout
    assert "## Example Runtime" in result.stdout
    assert "- [ ] Read AGENTS.md" in result.stdout
    assert "- [ ] Run focused tests" in result.stdout
    assert "- [ ] Restart admin service" in result.stdout
    assert "public tag v1.2.3" in result.stdout


def test_consumer_release_plan_refuses_tracked_output(tmp_path: Path) -> None:
    roster = tmp_path / "roster.json"
    _write_roster(roster)

    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--roster",
            str(roster),
            "--version",
            "1.2.3",
            "--output",
            str(ROOT / "docs" / "private-plan.md"),
        ],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )

    assert result.returncode != 0
    assert "outside .private" in result.stderr
    assert not (ROOT / "docs" / "private-plan.md").exists()


def test_consumer_release_plan_allows_private_output(tmp_path: Path) -> None:
    roster = tmp_path / "roster.json"
    _write_roster(roster)
    output = ROOT / ".private" / "release-plans" / "test-consumer-plan.md"
    output.unlink(missing_ok=True)

    try:
        subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--roster",
                str(roster),
                "--version",
                "1.2.3",
                "--output",
                str(output),
            ],
            cwd=ROOT,
            check=True,
            text=True,
            capture_output=True,
        )

        assert output.exists()
        assert "Example Runtime" in output.read_text(encoding="utf-8")
    finally:
        output.unlink(missing_ok=True)
