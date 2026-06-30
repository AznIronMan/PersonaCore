from __future__ import annotations

from importlib.resources import files
from typing import Any

from jinja2 import ChoiceLoader, FileSystemLoader

from .render import active_nav_label, render_nav_groups, render_status_pill, render_user_pill


def configure_jinja_loader(templates: Any) -> None:
    """Add PersonaConsole templates and helper globals to Jinja2Templates."""

    template_dir = files("personaconsole").joinpath("templates")
    env = templates.env
    existing = env.loader
    persona_loader = FileSystemLoader(str(template_dir))
    if existing is None:
        env.loader = persona_loader
    elif isinstance(existing, ChoiceLoader):
        env.loader = ChoiceLoader([*existing.loaders, persona_loader])
    else:
        env.loader = ChoiceLoader([existing, persona_loader])
    env.globals.update(
        personaconsole_active_nav_label=active_nav_label,
        personaconsole_nav=render_nav_groups,
        personaconsole_status_pill=render_status_pill,
        personaconsole_user_pill=render_user_pill,
        persona_console_active_nav_label=active_nav_label,
        persona_console_nav=render_nav_groups,
        persona_console_status_pill=render_status_pill,
        persona_console_user_pill=render_user_pill,
    )
