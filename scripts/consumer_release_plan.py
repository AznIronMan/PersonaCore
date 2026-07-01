#!/usr/bin/env python3
"""Render a private consumer release propagation checklist.

The roster this reads is intentionally local-only. Keep real consumer names,
hosts, paths, smoke URLs, and restart commands in `.private/`, not in tracked
PersonaConsole docs.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_ROSTER = ROOT / ".private" / "consumer-release-roster.json"

TEMPLATE: dict[str, Any] = {
    "consumers": [
        {
            "key": "example-runtime",
            "label": "Example Runtime",
            "repo_path": "/path/to/example-runtime",
            "task_system": "Open or continue the runtime-owned task before code or deploy work.",
            "persona_console_source": "Install the published package version or sync the approved source checkout.",
            "update_steps": [
                "Read the runtime AGENTS.md.",
                "Update the PersonaConsole package pin or source checkout.",
                "Refresh static assets if the runtime vendors them.",
            ],
            "tests": [
                "PYTHONPATH=src python -m pytest tests",
                "Run the runtime's focused admin/render tests.",
            ],
            "smokes": [
                "Open the admin login route.",
                "Open one representative authenticated admin route.",
            ],
            "restart_steps": [
                "Restart or rebuild only services that import PersonaConsole.",
            ],
            "rollback": [
                "Restore the previous package pin or source checkout.",
                "Restart/rebuild the affected services again.",
            ],
            "notes": [
                "Keep private hosts, ports, tokens, screenshots, and DB paths out of tracked files.",
            ],
        }
    ]
}


def _as_list(value: object) -> list[str]:
    if value in (None, ""):
        return []
    if isinstance(value, str):
        return [value]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item) for item in value if item not in (None, "")]
    return [str(value)]


def load_roster(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise SystemExit(f"missing roster: {path}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"invalid roster JSON in {path}: {exc}") from exc
    if not isinstance(data, Mapping):
        raise SystemExit("roster must be a JSON object")
    consumers = data.get("consumers")
    if not isinstance(consumers, list):
        raise SystemExit("roster must include a consumers list")
    return dict(data)


def _consumer_label(consumer: Mapping[str, object]) -> str:
    return str(consumer.get("label") or consumer.get("key") or "consumer")


def _section(title: str, items: Iterable[str]) -> list[str]:
    body = [item.strip() for item in items if str(item).strip()]
    if not body:
        return []
    lines = [f"### {title}"]
    lines.extend(f"- [ ] {item}" for item in body)
    lines.append("")
    return lines


def render_plan(
    roster: Mapping[str, Any],
    *,
    version: str,
    source: str,
    release_label: str,
) -> str:
    consumers = roster.get("consumers") or []
    if not isinstance(consumers, Sequence):
        raise SystemExit("roster consumers must be a list")
    title = release_label or f"PersonaConsole {version}"
    lines = [
        f"# {title} Consumer Propagation Plan",
        "",
        f"- PersonaConsole version/source: `{version or source or 'operator-approved update'}`",
        f"- Source note: {source or 'Confirm package tag, source checkout, or local approved update before starting.'}",
        "- Private roster: not for commit; record results in each consumer task system.",
        "",
    ]
    for raw_consumer in consumers:
        if not isinstance(raw_consumer, Mapping):
            continue
        consumer = dict(raw_consumer)
        label = _consumer_label(consumer)
        lines.extend([f"## {label}", ""])
        repo_path = str(consumer.get("repo_path") or "").strip()
        if repo_path:
            lines.append(f"- Repo/root: `{repo_path}`")
        task_system = str(consumer.get("task_system") or "").strip()
        if task_system:
            lines.append(f"- Task tracking: {task_system}")
        pc_source = str(consumer.get("persona_console_source") or "").strip()
        if pc_source:
            lines.append(f"- Update source: {pc_source}")
        if repo_path or task_system or pc_source:
            lines.append("")
        lines.extend(_section("Update", _as_list(consumer.get("update_steps"))))
        lines.extend(_section("Verification", _as_list(consumer.get("tests"))))
        lines.extend(_section("Smokes", _as_list(consumer.get("smokes"))))
        lines.extend(_section("Restart Or Rebuild", _as_list(consumer.get("restart_steps"))))
        lines.extend(_section("Rollback", _as_list(consumer.get("rollback"))))
        notes = _as_list(consumer.get("notes"))
        if notes:
            lines.append("### Notes")
            lines.extend(f"- {note}" for note in notes)
            lines.append("")
        lines.append("---")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def _is_private_output(path: Path) -> bool:
    resolved = path.resolve()
    private_root = (ROOT / ".private").resolve()
    try:
        resolved.relative_to(private_root)
    except ValueError:
        return False
    return True


def write_output(path: Path, text: str) -> None:
    if not _is_private_output(path):
        raise SystemExit("refusing to write a private release plan outside .private/")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--roster", type=Path, default=DEFAULT_ROSTER, help="Ignored local roster JSON.")
    parser.add_argument("--version", default="", help="Expected PersonaConsole version.")
    parser.add_argument("--source", default="", help="Package tag, source checkout, or local update note.")
    parser.add_argument("--release-label", default="", help="Optional heading label.")
    parser.add_argument("--output", type=Path, help="Optional output path. Must be under .private/.")
    parser.add_argument("--print-template", action="store_true", help="Print a generic roster template and exit.")
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.print_template:
        print(json.dumps(TEMPLATE, indent=2))
        return 0
    roster = load_roster(args.roster)
    text = render_plan(
        roster,
        version=args.version,
        source=args.source,
        release_label=args.release_label,
    )
    if args.output:
        write_output(args.output, text)
    else:
        print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
