from pathlib import Path

from examples.fixture_app import _default_static_base_for_output, build_fixture_config, render_fixture_page


def test_fixture_uses_public_personacore_config_name():
    config = build_fixture_config()

    assert config.brand_name == "Example Persona"
    assert config.nav_badges["review"] == 4
    assert config.live_interval == 30


def test_fixture_renders_shared_shell_with_generic_data():
    html = render_fixture_page(static_base_url="/static-fixture")

    assert "Runtime Dashboard" in html
    assert "Example Persona" in html
    assert "pc-dashboard-overview" in html
    assert "Adapter health" in html
    assert "pc-adapter-health" in html
    assert "pc-message-surface" in html
    assert "pc-activity-surface" in html
    assert "pc-media-surface" in html
    assert "Owner-private reply summarized for operators." in html
    assert "raw fixture owner private message" not in html
    assert "/media/raw-private-fixture" not in html
    assert "Token Health" in html
    assert "Webhook verify token" in html
    assert "/static-fixture/persona-console.css" in html
    assert "Example Persona" in html
    assert "Operator" in html


def test_fixture_static_output_path_points_to_shared_assets(tmp_path):
    output = tmp_path / "fixture.html"

    static_base = _default_static_base_for_output(output)

    assert static_base.endswith(str(Path("src") / "persona_console" / "static"))
