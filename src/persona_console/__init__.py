"""Shared admin console shell and assets for persona runtimes."""

from .fastapi import register_static_assets
from .dashboard import (
    render_dashboard_activity,
    render_dashboard_adapter_cards,
    render_dashboard_attention,
    render_dashboard_filters,
    render_dashboard_flow,
    render_dashboard_health_strip,
    render_dashboard_metrics,
    render_dashboard_queue,
    render_dashboard_route_cards,
    render_dashboard_sections,
)
from .models import (
    DashboardAction,
    DashboardActivityItem,
    DashboardAdapterCard,
    DashboardAttention,
    DashboardAttentionItem,
    DashboardData,
    DashboardFilter,
    DashboardFlow,
    DashboardFlowBucket,
    DashboardFlowSegment,
    DashboardHealthMetric,
    DashboardHealthStrip,
    DashboardMetric,
    DashboardQueueRow,
    DashboardRouteCard,
    DashboardSparkBucket,
    NavGroup,
    NavItem,
    PersonaCoreConfig,
    PersonaConsoleConfig,
    StatusPill,
    ThemeTokens,
    TokenHealthCheck,
    TokenHealthConfig,
    UserPill,
)
from .render import (
    active_nav_label,
    render_live_controls,
    render_nav_groups,
    render_shell_html,
    render_status_pill,
    render_user_pill,
)
from .token_health import build_token_health_report, render_token_health_panel, token_health_lookup

__all__ = [
    "NavGroup",
    "DashboardAction",
    "DashboardActivityItem",
    "DashboardAdapterCard",
    "DashboardAttention",
    "DashboardAttentionItem",
    "DashboardData",
    "DashboardFilter",
    "DashboardFlow",
    "DashboardFlowBucket",
    "DashboardFlowSegment",
    "DashboardHealthMetric",
    "DashboardHealthStrip",
    "DashboardMetric",
    "DashboardQueueRow",
    "DashboardRouteCard",
    "DashboardSparkBucket",
    "NavItem",
    "PersonaCoreConfig",
    "PersonaConsoleConfig",
    "StatusPill",
    "ThemeTokens",
    "TokenHealthCheck",
    "TokenHealthConfig",
    "UserPill",
    "active_nav_label",
    "build_token_health_report",
    "configure_jinja_loader",
    "register_static_assets",
    "render_dashboard_activity",
    "render_dashboard_adapter_cards",
    "render_dashboard_attention",
    "render_dashboard_filters",
    "render_dashboard_flow",
    "render_dashboard_health_strip",
    "render_dashboard_metrics",
    "render_dashboard_queue",
    "render_dashboard_route_cards",
    "render_dashboard_sections",
    "render_live_controls",
    "render_nav_groups",
    "render_shell_html",
    "render_status_pill",
    "render_token_health_panel",
    "render_user_pill",
    "token_health_lookup",
]

__version__ = "1.0.3"


def configure_jinja_loader(*args, **kwargs):
    """Load the optional Jinja integration only when a consumer asks for it."""

    from .jinja import configure_jinja_loader as _configure_jinja_loader

    return _configure_jinja_loader(*args, **kwargs)
