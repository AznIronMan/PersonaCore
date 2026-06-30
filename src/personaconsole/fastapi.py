from __future__ import annotations

from importlib.resources import files


def register_static_assets(app: object, *, mount_path: str = "/persona-console/static") -> None:
    """Mount PersonaConsole static assets on a FastAPI app."""

    try:
        from fastapi.staticfiles import StaticFiles
    except ImportError as exc:  # pragma: no cover - only hit without FastAPI.
        raise RuntimeError("FastAPI is required to mount PersonaConsole assets") from exc

    static_dir = files("personaconsole").joinpath("static")
    app.mount(mount_path, StaticFiles(directory=str(static_dir)), name="personaconsole_static")
