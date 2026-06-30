from personaconsole import (
    DashboardActivityItem,
    DashboardAdapterCard,
    DashboardAttention,
    DashboardAttentionItem,
    DashboardData,
    DashboardFilter,
    DashboardFlow,
    DashboardFlowBucket,
    DashboardHealthMetric,
    DashboardHealthStrip,
    DashboardMetric,
    DashboardMetricSpec,
    DashboardQueueRow,
    DashboardRouteCard,
    TokenHealthCheck,
    TokenHealthConfig,
    dashboard_metrics_from_counts,
    format_dashboard_metric_value,
    render_dashboard_activity,
    render_dashboard_attention,
    render_dashboard_flow,
    render_dashboard_queue,
    render_dashboard_sections,
    render_dashboard_summary_grid,
)


def test_attention_escapes_data_and_falls_back_for_unknown_tone():
    html = render_dashboard_attention(
        DashboardAttention(
            title="<Overview>",
            label="<Needs work>",
            tone="mystery",
            count=2,
            items=[
                DashboardAttentionItem(
                    "<Review>",
                    "<4>",
                    "<unsafe summary>",
                    href="/review",
                    tone="rose",
                )
            ],
        ),
        filters=[DashboardFilter("<All>", "/", active=True, color="rgb(1 2 3)")],
    )

    assert "&lt;Overview&gt;" in html
    assert "&lt;Needs work&gt;" in html
    assert "pc-dashboard-tone-neutral" in html
    assert "pc-dashboard-tone-bad" in html
    assert "&lt;unsafe summary&gt;" in html
    assert "is-active" in html


def test_attention_empty_state_renders_clear_card():
    html = render_dashboard_attention({"clear_title": "All quiet", "extra": "ignored"})

    assert "All quiet" in html
    assert "pc-dashboard-clear" in html


def test_dashboard_sections_accept_plain_dicts_and_skip_missing_sections():
    html = render_dashboard_sections(
        {
            "metrics": [
                {"label": "Messages", "value": 12, "href": "/messages", "unknown": "ignored"},
            ],
            "routes": [
                {"label": "Review", "href": "/review", "summary": "Queue", "metric": 3},
            ],
        }
    )

    assert "pc-dashboard-stat-grid" in html
    assert "Messages" in html
    assert "pc-dashboard-route-grid" in html
    assert "Review" in html
    assert "pc-dashboard-overview" not in html


def test_dashboard_metric_specs_build_summary_cards_from_counts():
    metrics = dashboard_metrics_from_counts(
        {
            "messages": 12345,
            "provider": "example-provider-with-a-long-name",
        },
        [
            DashboardMetricSpec("Messages", "messages", "/messages", "stored messages", tone="good", value_kind="count"),
            {
                "label": "Provider",
                "key": "provider",
                "href": "/runtime/provider",
                "value_kind": "text",
                "max_length": 16,
            },
            {"label": "<Missing>", "key": "missing", "href": "/missing", "default": "<none>"},
        ],
    )

    assert metrics[0].value == "12.3k"
    assert metrics[1].value == "example-provi..."
    assert metrics[2].value == "<none>"

    html = render_dashboard_summary_grid(metrics)

    assert "pc-dashboard-stat-grid" in html
    assert "12.3k" in html
    assert "example-provi..." in html
    assert "&lt;Missing&gt;" in html
    assert "&lt;none&gt;" in html


def test_dashboard_summary_grid_can_render_count_specs_directly():
    html = render_dashboard_summary_grid(
        {"pending": 4, "mode": "observe"},
        [
            {"label": "Pending", "key": "pending", "href": "/review", "value_kind": "count"},
            {"label": "Mode", "key": "mode", "href": "/runtime", "value_kind": "raw"},
        ],
    )

    assert "Pending" in html
    assert ">4</div>" in html
    assert "observe" in html


def test_dashboard_metric_value_formatting_handles_edges():
    assert format_dashboard_metric_value(1_500_000, value_kind="count") == "1.5m"
    assert format_dashboard_metric_value("abcdefgh", value_kind="text", max_length=3) == "..."
    assert format_dashboard_metric_value(None, value_kind="raw") == ""


def test_health_adapters_flow_queue_and_activity_render_expected_surfaces():
    html = render_dashboard_sections(
        DashboardData(
            metrics=[DashboardMetric("Reviews", 4)],
            routes=[DashboardRouteCard("Review", "/review", "Open queue")],
            health=DashboardHealthStrip(
                "Runtime health",
                metrics=[DashboardHealthMetric("CPU", "18%", "ok", tone="green")],
            ),
            token_health=TokenHealthConfig(
                enabled=True,
                checks=[TokenHealthCheck("social", "Social provider token", configured=True)],
            ),
            adapters=[
                DashboardAdapterCard(
                    "Messages",
                    "healthy",
                    counts=[{"label": "0 failed", "tone": "good"}],
                    sparkline=[{"label": "now", "percent": 140, "tone": "blue"}],
                )
            ],
            flow=DashboardFlow(
                buckets=[
                    DashboardFlowBucket("old", inbound_percent=-4, outbound_percent=42),
                    DashboardFlowBucket("now", inbound_percent=125, outbound_percent=75),
                ]
            ),
            queue=[DashboardQueueRow("Pending", 5, total=10, tone="amber")],
            activity=[DashboardActivityItem("Review", "Queued", timestamp="now", summary="Needs pass")],
        )
    )

    assert "Runtime health" in html
    assert "Token Health" in html
    assert "Social provider token" in html
    assert "Adapter health" in html
    assert "height: 100%" in html
    assert "height: 0%" in html
    assert "width: 50%" in html
    assert "Activity timeline" in html


def test_activity_empty_state_is_explicit():
    html = render_dashboard_activity([])

    assert "No recent activity found." in html


def test_flow_without_buckets_is_hidden():
    assert render_dashboard_flow(DashboardFlow()) == ""


def test_queue_percent_handles_zero_total():
    html = render_dashboard_queue([DashboardQueueRow("Pending", 0)])

    assert "width: 0%" in html
