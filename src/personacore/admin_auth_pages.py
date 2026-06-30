"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.admin_auth_pages import (
    render_admin_login_page,
    render_admin_password_change_page,
)

__all__ = [
    "render_admin_login_page",
    "render_admin_password_change_page",
]
