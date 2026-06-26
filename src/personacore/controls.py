"""Shared control primitive re-exports for the public PersonaCore import path."""

from persona_console.controls import render_status_tabs
from persona_console.models import StatusTab

__all__ = [
    "StatusTab",
    "render_status_tabs",
]
