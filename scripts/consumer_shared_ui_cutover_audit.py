#!/usr/bin/env python3
"""Run the PersonaConsole shared UI cutover audit for a consumer repository."""

from __future__ import annotations

from pathlib import Path
import sys


ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from personaconsole.cutover_audit import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
