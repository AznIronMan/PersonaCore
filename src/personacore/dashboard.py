"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.dashboard import (
    dashboard_metrics_from_counts,
    format_dashboard_metric_value,
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
    render_dashboard_summary_grid,
)

__all__ = [
    "dashboard_metrics_from_counts",
    "format_dashboard_metric_value",
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
    "render_dashboard_summary_grid",
]
