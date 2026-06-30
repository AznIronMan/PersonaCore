from personaconsole import (
    ADAPTER_HEALTH_FEATURE,
    AdapterHealthCard,
    AdapterHealthConfig,
    AdapterHealthSparkBucket,
    adapter_health_feature_enabled,
    render_adapter_health_panel,
)


def test_adapter_health_panel_renders_and_escapes_runtime_data():
    html = render_adapter_health_panel(
        AdapterHealthConfig(
            enabled=True,
            title="<Adapter Health>",
            cards=[
                AdapterHealthCard(
                    "<Messages>",
                    "<healthy>",
                    href="/messages?route=<dm>",
                    tone="healthy",
                    route="<inbound/outbound>",
                    policy="<runtime policy>",
                    last_in="<2m>",
                    last_out="<1m>",
                    counts=[{"label": "<0 failed>", "tone": "ok"}, "<128 in/24h>"],
                    detail="<detail>",
                    action_hint="<inspect>",
                    sparkline=[
                        AdapterHealthSparkBucket(
                            "<now>",
                            140,
                            href="/messages?bucket=<now>",
                            tone="blue",
                            title="<now title>",
                        )
                    ],
                )
            ],
        )
    )

    assert 'id="adapter-health"' in html
    assert "pc-adapter-health" in html
    assert '<article class="pc-dashboard-adapter pc-dashboard-tone-good">' in html
    assert '<a class="pc-dashboard-adapter' not in html
    assert 'href="/messages?route=&lt;dm&gt;"' in html
    assert 'href="/messages?bucket=&lt;now&gt;"' in html
    assert "&lt;Adapter Health&gt;" in html
    assert "&lt;Messages&gt;" in html
    assert "&lt;runtime policy&gt;" in html
    assert "&lt;0 failed&gt;" in html
    assert "pc-dashboard-tone-good" in html
    assert "pc-dashboard-tone-info" in html
    assert "height: 100%" in html


def test_adapter_health_feature_flag_hides_panel():
    config = AdapterHealthConfig(enabled=True, cards=[AdapterHealthCard("Messages", "healthy")])

    assert adapter_health_feature_enabled(config, {ADAPTER_HEALTH_FEATURE: True}) is True
    assert adapter_health_feature_enabled(config, {ADAPTER_HEALTH_FEATURE: False}) is False
    assert render_adapter_health_panel(config, features={ADAPTER_HEALTH_FEATURE: False}) == ""


def test_adapter_health_empty_state_and_disabled_config():
    disabled = AdapterHealthConfig(enabled=False, cards=[AdapterHealthCard("Messages", "healthy")])
    empty = AdapterHealthConfig(enabled=True, empty_label="<No adapters>")

    assert render_adapter_health_panel(disabled) == ""
    assert "&lt;No adapters&gt;" in render_adapter_health_panel(empty)


def test_adapter_health_accepts_plain_sequence_for_dashboard_compatibility():
    html = render_adapter_health_panel(
        [
            {
                "label": "Workers",
                "status": "lagging",
                "tone": "degraded",
                "counts": [{"label": "1 queued", "tone": "warn"}],
            }
        ]
    )

    assert "Workers" in html
    assert "lagging" in html
    assert "pc-dashboard-tone-warn" in html
