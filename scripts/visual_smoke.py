from __future__ import annotations

import argparse
import contextlib
import http.server
import socket
import sys
import threading
from pathlib import Path
from typing import Iterator


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from examples.fixture_app import render_dashboard_fragment, render_fixture_page


class FixtureHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, output_dir: Path, **kwargs):
        self.output_dir = output_dir
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def log_message(self, format: str, *args: object) -> None:
        return

    def do_GET(self) -> None:
        path = self.path.split("?", 1)[0]
        if path in {"/", "/index.html"}:
            self._send_html((self.output_dir / "index.html").read_text(encoding="utf-8"))
            return
        if path == "/fragments/dashboard":
            self._send_html(render_dashboard_fragment())
            return
        super().do_GET()

    def _send_html(self, html: str) -> None:
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind(("127.0.0.1", 0))
        return int(sock.getsockname()[1])


@contextlib.contextmanager
def serve_fixture(output_dir: Path) -> Iterator[str]:
    port = _free_port()

    def handler(*args, **kwargs):
        return FixtureHandler(*args, output_dir=output_dir, **kwargs)

    server = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield f"http://127.0.0.1:{port}/"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def write_fixture(output_dir: Path) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    html_path = output_dir / "index.html"
    html_path.write_text(
        render_fixture_page(static_base_url="/src/persona_console/static"),
        encoding="utf-8",
    )
    return html_path


def run_visual_smoke(output_dir: Path, *, headed: bool = False) -> None:
    try:
        from playwright.sync_api import expect, sync_playwright
    except ImportError as exc:
        raise SystemExit(
            "Playwright is not installed. Run: python3 -m pip install -e '.[visual]' "
            "&& python3 -m playwright install chromium"
        ) from exc

    write_fixture(output_dir)
    screenshot_dir = output_dir / "screenshots"
    screenshot_dir.mkdir(parents=True, exist_ok=True)

    with serve_fixture(output_dir) as url:
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=not headed)
            try:
                for name, viewport in {
                    "desktop": {"width": 1440, "height": 1000},
                    "mobile": {"width": 390, "height": 844},
                }.items():
                    page = browser.new_page(viewport=viewport)
                    page.goto(url, wait_until="networkidle")
                    expect(page.locator(".persona-console-shell")).to_be_visible()
                    expect(page.locator(".pc-dashboard-overview")).to_be_visible()
                    expect(page.locator(".pc-dashboard-stat-grid")).to_be_visible()
                    expect(page.locator(".pc-dashboard-health")).to_be_visible()
                    expect(page.locator(".pc-token-health")).to_be_visible()
                    expect(page.locator(".pc-dashboard-adapter-grid")).to_be_visible()
                    expect(page.locator(".pc-reference-workspace")).to_be_visible()
                    expect(page.locator("#live-pill")).to_be_visible()
                    if name == "mobile":
                        toggle = page.locator(".admin-mobile-toggle")
                        expect(toggle).to_be_visible()
                        toggle.click()
                        expect(page.locator(".admin-mobile-panel")).to_be_visible()
                    else:
                        expect(page.locator(".admin-nav-groups")).to_be_visible()
                    page.screenshot(path=screenshot_dir / f"{name}.png", full_page=True)
                    page.close()
            finally:
                browser.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="Run PersonaCore fixture visual smoke checks.")
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=ROOT / "build" / "visual-smoke",
        help="Directory for generated fixture HTML and screenshots.",
    )
    parser.add_argument("--headed", action="store_true", help="Run Chromium with a visible window.")
    args = parser.parse_args()

    run_visual_smoke(args.output_dir, headed=args.headed)
    print(f"Visual smoke passed. Screenshots: {args.output_dir / 'screenshots'}")


if __name__ == "__main__":
    main()
