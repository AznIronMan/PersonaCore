from personaconsole import (
    DashboardData,
    TOKEN_HEALTH_FEATURE,
    TokenHealthCheck,
    TokenHealthConfig,
    build_token_health_report,
    render_dashboard_sections,
    render_token_health_panel,
    token_health_checks_for_providers,
    token_health_config_for_providers,
    token_health_feature_enabled,
    token_health_lookup,
    token_health_provider_keys,
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
        values={"SOCIAL_TOKEN": "raw-secret-token", "WEBHOOK_TOKEN": ""},
    )

    assert report["ok"] is True
    assert report["token_count"] == 2
    assert report["present_count"] == 1
    assert report["missing_count"] == 1
    assert report["warnings"] == 1
    assert "raw-secret-token" not in str(report)
    assert token_health_lookup(report, "social")["status"] == "ready"
    assert token_health_lookup(report, "optional_webhook")["status"] == "degraded"


def test_provider_presets_build_common_integration_checks_without_raw_values():
    config = token_health_config_for_providers(
        ["meta", "ig", "x", "discord"],
        overrides={
            "x": {
                "required": False,
                "secret_names": ["PUBLIC_X_TOKEN"],
                "summary": "Validated by runtime lookup",
            }
        },
    )
    report = build_token_health_report(
        config,
        values={
            "META_TOKEN": "raw-meta-secret",
            "IG_TOKEN": "raw-instagram-secret",
            "PUBLIC_X_TOKEN": "raw-x-secret",
            "DISCORD_TOKEN": "",
        },
    )

    assert TOKEN_HEALTH_FEATURE == "token_health"
    assert "meta" in token_health_provider_keys()
    assert "instagram" in token_health_provider_keys()
    assert "raw-meta-secret" not in str(report)
    assert "raw-instagram-secret" not in str(report)
    assert "raw-x-secret" not in str(report)
    assert token_health_lookup(report, "meta")["status"] == "ready"
    assert token_health_lookup(report, "instagram")["status"] == "ready"
    assert token_health_lookup(report, "x")["required"] is False
    assert token_health_lookup(report, "x")["summary"] == "Validated by runtime lookup"
    assert token_health_lookup(report, "discord")["status"] == "blocked"


def test_provider_presets_reject_unknown_provider_names():
    try:
        token_health_checks_for_providers(["unknown-provider"])
    except ValueError as exc:
        assert "Unknown token health provider" in str(exc)
    else:
        raise AssertionError("unknown provider should fail closed")


def test_token_health_feature_flag_hides_report_and_panel():
    config = token_health_config_for_providers("discord")
    features = {TOKEN_HEALTH_FEATURE: False}

    report = build_token_health_report(config, values={"DISCORD_TOKEN": "raw"}, features=features)
    html = render_token_health_panel(config, values={"DISCORD_TOKEN": "raw"}, features=features)

    assert token_health_feature_enabled(config, {TOKEN_HEALTH_FEATURE: True}) is True
    assert token_health_feature_enabled(config, features) is False
    assert report["enabled"] is False
    assert report["token_count"] == 0
    assert html == ""


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


def test_dashboard_sections_hide_token_health_when_feature_is_disabled():
    html = render_dashboard_sections(
        DashboardData(
            features={TOKEN_HEALTH_FEATURE: False},
            token_health=token_health_config_for_providers("discord"),
        )
    )

    assert "Token Health" not in html
    assert "Discord bot token" not in html
