from pathlib import Path

from examples.fixture_app import (
    _default_static_base_for_output,
    build_fixture_config,
    render_chat_fixture_page,
    render_fixture_page,
    render_login_fixture_page,
    render_public_settings_fixture_page,
    render_public_splash_fixture_page,
)


def test_fixture_uses_public_personaconsole_config_name():
    config = build_fixture_config()

    assert config.brand_name == "Example Persona"
    assert config.nav_badges["review"] == 4
    assert config.nav_badges["people"] == 3
    assert config.nav_badges["lists"] == 2
    assert config.features["people"] is True
    assert config.features["admin_list"] is True
    assert config.features["operations"] is True
    assert config.features["bridge_ops"] is True
    assert config.features["command_intake"] is True
    assert config.features["availability_monitor"] is True
    assert config.features["persona"] is True
    assert config.features["persona_editor"] is True
    assert config.features["agent_ops"] is True
    assert config.features["terminal_stream"] is True
    assert config.features["settings_editor"] is True
    assert config.features["system_health"] is True
    assert config.features["journal"] is True
    assert config.features["public_presence"] is True
    assert config.brand_assets is not None
    assert config.live_interval == 30


def test_fixture_renders_shared_shell_with_generic_data():
    html = render_fixture_page(static_base_url="/static-fixture")

    assert "Admin Overview" in html
    assert "Example Persona" in html
    assert "pc-dashboard-overview" in html
    assert "Operator Attention" in html
    assert "pc-admin-list-surface" in html
    assert "Generic List" in html
    assert "Example public row" in html
    assert "Owner-private list cell summarized for operators." in html
    assert "Owner-private list card summarized for operators." in html
    assert "raw fixture private admin-list summary" not in html
    assert "raw fixture private admin-list card summary" not in html
    assert "/lists/private-raw" not in html
    assert "pc-detail-dossier-surface" in html
    assert "Example Detail" in html
    assert "Owner-private dossier field summarized for operators." in html
    assert "Owner-private context is summarized without raw prose." in html
    assert "Owner-private table row summarized for operators." in html
    assert "Owner-private timeline event summarized for operators." in html
    assert "Owner-private audit value summarized." in html
    assert "raw fixture private detail dossier field" not in html
    assert "raw fixture private detail dossier section" not in html
    assert "raw fixture private detail dossier table" not in html
    assert "raw fixture private detail dossier timeline" not in html
    assert "raw fixture private detail dossier audit" not in html
    assert "/detail/raw-private" not in html
    assert "/detail/source/raw-private" not in html
    assert "/detail/timeline/raw-private" not in html
    assert "pc-people-surface" in html
    assert "Example Consumer" in html
    assert "Owner-private notes are summarized for operators." in html
    assert "raw fixture private people note" not in html
    assert "pc-review-surface" in html
    assert "Decision Board" in html
    assert "Owner-private review summary withheld for operators." in html
    assert "Owner-private queue summarized for operators." in html
    assert "raw fixture private review summary" not in html
    assert "raw fixture private queue summary" not in html
    assert "pc-journal-surface" in html
    assert "pc-journal-theme-paper" in html
    assert "A steady day in the runtime" in html
    assert "pc-journal-theme-swatch-matrix" in html
    assert "pc-operations-surface" in html
    assert "Review pending replies" in html
    assert "Owner-private log line summarized for operators." in html
    assert "raw fixture private log line" not in html
    assert "Settings Posture" in html
    assert "pc-persona-surface" in html
    assert "Owner-private persona state summarized for operators." in html
    assert "Owner-private continuity item summarized for operators." in html
    assert "raw fixture private persona" not in html
    assert "pc-persona-editor-surface" in html
    assert "Persona Editor" in html
    assert "Voice rule proposal" in html
    assert "Owner-private profile field summarized for operators." in html
    assert "Owner-private trait summarized for operators." in html
    assert "Owner-private rule summarized for operators." in html
    assert "Owner-private proposal change summarized for operators." in html
    assert "new secret staged" in html
    assert "raw fixture private persona editor profile" not in html
    assert "raw fixture private persona editor trait" not in html
    assert "raw fixture private persona editor rule" not in html
    assert "raw fixture private persona editor secret" not in html
    assert "new raw fixture persona editor secret" not in html
    assert "raw fixture private persona editor before" not in html
    assert "raw fixture private persona editor after" not in html
    assert "pc-agent-ops-surface" in html
    assert "Owner-private agent session summarized for operators." in html
    assert "raw fixture private agent" not in html
    assert "pc-terminal-stream" in html
    assert "Read-Only Terminal" in html
    assert "Owner-private terminal event summarized for operators." in html
    assert "raw fixture private terminal event" not in html
    assert "pc-bridge-ops-surface" in html
    assert "Bridge Operations" in html
    assert "Verify endpoint" in html
    assert "Inbound queue" in html
    assert "Worker heartbeat" in html
    assert "Email provider" in html
    assert "Owner-private delivery failure summarized for operators." in html
    assert "raw fixture private bridge delivery failure" not in html
    assert "/bridge-ops/deliveries/raw-private" not in html
    assert "pc-command-intake-surface" in html
    assert "Command Intake" in html
    assert "Preview command" in html
    assert "Owner-private command prompt summarized for operators." in html
    assert "Owner-private parsed parameter summarized for operators." in html
    assert "Owner-private command candidate summarized for operators." in html
    assert "Owner-private command risk summarized for operators." in html
    assert "Owner-private queued command summarized for operators." in html
    assert "Owner-private command history summarized for operators." in html
    assert "raw fixture private command prompt" not in html
    assert "raw fixture private command parsed parameter" not in html
    assert "raw fixture private command candidate summary" not in html
    assert "raw fixture private command candidate detail" not in html
    assert "raw fixture private command risk summary" not in html
    assert "raw fixture private command queued command" not in html
    assert "raw fixture private command queue detail" not in html
    assert "raw fixture private command history" not in html
    assert "raw fixture private command history detail" not in html
    assert "/commands/queue/raw-private" not in html
    assert "/commands/history/raw-private" not in html
    assert "pc-availability-monitor-surface" in html
    assert "Availability Monitor" in html
    assert "Schedule Windows" in html
    assert "Daytime window" in html
    assert "Queue latency" in html
    assert "Review gate" in html
    assert "Reply preflight" in html
    assert "Owner-private availability window summarized for operators." in html
    assert "Owner-private availability scenario summarized for operators." in html
    assert "Owner-private availability event summarized for operators." in html
    assert "raw fixture private availability window" not in html
    assert "raw fixture private availability detail" not in html
    assert "raw fixture private availability scenario" not in html
    assert "raw fixture private availability event" not in html
    assert "/availability/windows/raw-private" not in html
    assert "/availability/scenarios/raw-private" not in html
    assert "/availability/events/raw-private" not in html
    assert "pc-settings-editor" in html
    assert "Runtime Settings" in html
    assert "Provider API key" in html
    assert "configured" in html
    assert "restart required" in html
    assert "raw fixture private settings secret" not in html
    assert "pc-system-health-surface" in html
    assert "System Health" in html
    assert "Runtime database" in html
    assert "Secret Coverage" in html
    assert "Readiness" in html
    assert "Owner-private system audit summarized for operators." in html
    assert "raw fixture private system audit" not in html
    assert "/audit/raw-private-fixture" not in html
    assert "pc-public-settings-surface" in html
    assert "Public Presence" in html
    assert "Small logo URL" in html
    assert "Save media" in html
    assert "Adapter health" in html
    assert "pc-adapter-health" in html
    assert "pc-message-surface" in html
    assert "pc-message-controls" in html
    assert "Raw rows" in html
    assert "Selected conversation" in html
    assert "pc-activity-surface" in html
    assert "pc-media-surface" in html
    assert "pc-media-library-surface" in html
    assert "Media Library" in html
    assert "Import Media" in html
    assert "Example portrait anchor" in html
    assert "Voice note" in html
    assert "Reference document" in html
    assert "Owner-private library item summarized for operators." in html
    assert "Safe media library metadata." in html
    assert "Owner-private reply summarized for operators." in html
    assert "raw fixture owner private message" not in html
    assert "raw fixture private media library title" not in html
    assert "raw fixture private media library detail" not in html
    assert "raw fixture private media library metadata" not in html
    assert "/media/raw-private-library" not in html
    assert "/media/raw-private-fixture" not in html
    assert "/oauth/callback" not in html
    assert "Token Health" in html
    assert "Webhook verify token" in html
    assert "/static-fixture/persona-console.css" in html
    assert "/static-fixture/persona-public.css" in html
    assert "Example Persona" in html
    assert "Operator" in html


def test_fixture_renders_public_presence_pages_with_generic_data():
    splash = render_public_splash_fixture_page(static_base_url="/static-fixture")
    login = render_login_fixture_page(static_base_url="/static-fixture")
    chat = render_chat_fixture_page(static_base_url="/static-fixture")
    settings = render_public_settings_fixture_page(static_base_url="/static-fixture")

    assert "pc-public-splash" in splash
    assert "Chat with Example Persona" in splash
    assert "/static-fixture/persona-public.css" in splash
    assert "pc-public-login-page" in login
    assert "Choose any configured method" in login
    assert "pc-connector-option" in login
    assert "pc-public-chat-shell" in chat
    assert "data-pc-chat-form" in chat
    assert "pc-public-settings-surface" in settings
    assert "Reusable splash, login, chat, media, and connector settings." in settings
    assert "private-login.example" not in splash + login + chat + settings
    assert "private-chat.example" not in splash + login + chat + settings


def test_fixture_static_output_path_points_to_shared_assets(tmp_path):
    output = tmp_path / "fixture.html"

    static_base = _default_static_base_for_output(output)

    assert static_base == "/persona-console/static"


def test_fixture_static_output_path_can_be_relative_inside_repo():
    output = Path("build/fixture.html")

    static_base = _default_static_base_for_output(output)

    assert static_base.endswith(str(Path("src") / "personaconsole" / "static"))
