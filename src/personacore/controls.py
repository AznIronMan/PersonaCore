"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.controls import flash_query_params, flash_url, render_flash_banners, render_status_tabs
from personaconsole.models import FlashBanner, StatusTab

__all__ = [
    "FlashBanner",
    "StatusTab",
    "flash_query_params",
    "flash_url",
    "render_flash_banners",
    "render_status_tabs",
]
