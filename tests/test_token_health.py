from persona_console import (
    DashboardData,
    TokenHealthCheck,
    TokenHealthConfig,
    build_token_health_report,
    render_dashboard_sections,
    render_token_health_panel,
    token_health_lookup,
)


def test_disabled_token_health_does_not_render():
    report = build_token_health_report(TokenHealthConfig(enabled=False))

    assert report["enabled"] is False
    assert report["token_count"] == 0
    assert render_token_health_panel(report) == ""


def test_token_health_report_is_redacted_and_counts_statuses():
    report = build_token_health_report(
        TokenHealthConfig(
            enabled=True,
            checks=[
                TokenHealthCheck("social", "Social token", "Social", ["SOCIAL_TOKEN"]),
                TokenHealthCheck(
                    "optional_webhook",
                    "Webhook token",
                    "Webhooks",
                    ["WEBHOOK_TOKEN"],
                    required=False,
                ),
            ],
        ),
        values={"SOCIAL_TOKEN": "fixture-token-value", "WEBHOOK_TOKEN": ""},
    )

    assert report["ok"] is True
    assert report["token_count"] == 2
    assert report["present_count"] == 1
    assert report["missing_count"] == 1
    assert report["warnings"] == 1
    assert "fixture-token-value" not in str(report)
    assert token_health_lookup(report, "social")["status"] == "ready"
    assert token_health_lookup(report, "optional_webhook")["status"] == "degraded"


def test_required_missing_token_blocks_report():
    report = build_token_health_report(
        {
            "enabled": True,
            "checks": [
                {
                    "key": "messaging",
                    "label": "Messaging token",
                    "secret_names": "MESSAGING_TOKEN",
                    "required": True,
                }
            ],
        },
        values={},
    )

    assert report["ok"] is False
    assert report["blocked_required"] == 1
    assert token_health_lookup(report, "messaging")["missing"] == ("MESSAGING_TOKEN",)


def test_token_health_supports_runtime_lookup_and_hidden_secret_names():
    seen: list[str] = []

    def lookup(name: str) -> str:
        seen.append(name)
        return "configured" if name == "RUNTIME_TOKEN" else ""

    report = build_token_health_report(
        TokenHealthConfig(
            enabled=True,
            show_secret_names=False,
            checks=[TokenHealthCheck("runtime", "Runtime token", secret_names=["RUNTIME_TOKEN"])],
        ),
        lookup=lookup,
    )

    row = token_health_lookup(report, "runtime")
    assert seen == ["RUNTIME_TOKEN"]
    assert row["present"] is True
    assert row["secret_names"] == ()
    assert row["missing"] == ()


def test_token_health_renderer_escapes_labels_and_sources():
    html = render_token_health_panel(
        TokenHealthConfig(
            enabled=True,
            checks=[
                TokenHealthCheck(
                    "unsafe",
                    "<Social>",
                    "<Group>",
                    ["TOKEN_<unsafe>"],
                    configured=True,
                    detail="<detail>",
                )
            ],
        )
    )

    assert "&lt;Social&gt;" in html
    assert "&lt;Group&gt;" in html
    assert "TOKEN_&lt;unsafe&gt;" in html
    assert "&lt;detail&gt;" in html
    assert "<Social>" not in html


def test_dashboard_sections_render_token_health_when_enabled():
    html = render_dashboard_sections(
        DashboardData(
            token_health=TokenHealthConfig(
                enabled=True,
                checks=[TokenHealthCheck("discord", "Messaging provider token", configured=True)],
            )
        )
    )

    assert "Token Health" in html
    assert "Messaging provider token" in html
    assert "pc-token-health" in html
