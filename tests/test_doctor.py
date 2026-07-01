import json
import subprocess
import sys

from personaconsole.doctor import doctor_report_to_text, run_consumer_integration_doctor


def test_consumer_integration_doctor_passes_current_source():
    report = run_consumer_integration_doctor(expected_version="1.0.50")
    data = report.as_dict()

    assert report.ok is True
    assert data["personaconsole"]["version"] == "1.0.50"
    assert data["persona_console_compat"]["version"] == "1.0.50"
    assert data["personacore_compat"]["version"] == "1.0.50"
    assert data["personaconsole"]["path"] == ""
    assert data["persona_console_compat"]["path"] == ""
    assert data["personacore_compat"]["path"] == ""
    assert "raw-doctor-secret" not in str(data)
    assert any(check["key"] == "adapter_health_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "availability_monitor_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "admin_list_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "admin_access_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "detail_dossier_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "media_library_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "infrastructure_posture_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "controls_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "token_health_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "surface_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "people_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "review_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "journal_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "public_presence_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "public_profile_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "presence_monitor_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "runtime_task_board_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "operations_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "worker_operations_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "persona_editor_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "bridge_ops_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "command_intake_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "settings_editor_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "system_health_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "owner_private_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "shell_render" and check["ok"] for check in data["checks"])


def test_consumer_integration_doctor_detects_expected_version_mismatch():
    report = run_consumer_integration_doctor(expected_version="0.0.0")

    assert report.ok is False
    assert any(check.key == "expected_version_match" and not check.ok for check in report.checks)


def test_consumer_integration_doctor_text_is_public_safe_by_default():
    report = run_consumer_integration_doctor(expected_version="1.0.50")
    text = doctor_report_to_text(report)

    assert "PersonaConsole consumer integration doctor: ok" in text
    assert "- personaconsole: ok version=1.0.50" in text
    assert "- persona_console_compat: ok version=1.0.50" in text
    assert "- personacore_compat: ok version=1.0.50" in text
    assert "raw-doctor-secret" not in text
    assert "raw-doctor-private-availability" not in text
    assert "raw-doctor-private-admin-list" not in text
    assert "raw-doctor-private-admin-access" not in text
    assert "raw-doctor-admin-auth" not in text
    assert "raw-doctor-private-detail-dossier" not in text
    assert "raw-doctor-private-media-library" not in text
    assert "raw-doctor-private-infrastructure" not in text
    assert "raw-doctor-private-message" not in text
    assert "raw-doctor-private-people-note" not in text
    assert "raw-doctor-private-review-summary" not in text
    assert "raw-doctor-private-journal" not in text
    assert "raw-doctor-public-presence" not in text
    assert "raw-doctor-private-public-profile" not in text
    assert "raw-doctor-private-presence" not in text
    assert "raw-doctor-private-runtime-task" not in text
    assert "raw-doctor-private-operations" not in text
    assert "raw-doctor-private-worker-ops" not in text
    assert "raw-doctor-private-persona-editor" not in text
    assert "raw-doctor-persona-state-secret" not in text
    assert "raw-doctor-private-bridge-delivery" not in text
    assert "raw-doctor-private-command" not in text
    assert "raw-doctor-settings-secret" not in text
    assert "raw-doctor-private-system-audit" not in text
    assert report.personaconsole.path == ""
    assert report.persona_console_compat.path == ""
    assert report.personacore_compat.path == ""


def test_consumer_integration_doctor_script_json():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/consumer_integration_doctor.py",
            "--expected-version",
            "1.0.50",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["personaconsole"]["version"] == "1.0.50"
    assert payload["persona_console_compat"]["version"] == "1.0.50"
    assert payload["personacore_compat"]["version"] == "1.0.50"
    assert payload["personaconsole"]["path"] == ""
    assert "raw-doctor-secret" not in result.stdout
    assert "raw-doctor-private-availability" not in result.stdout
    assert "raw-doctor-private-admin-list" not in result.stdout
    assert "raw-doctor-private-admin-access" not in result.stdout
    assert "raw-doctor-admin-auth" not in result.stdout
    assert "raw-doctor-private-detail-dossier" not in result.stdout
    assert "raw-doctor-private-media-library" not in result.stdout
    assert "raw-doctor-private-infrastructure" not in result.stdout
    assert "raw-doctor-private-message" not in result.stdout
    assert "raw-doctor-private-people-note" not in result.stdout
    assert "raw-doctor-private-review-summary" not in result.stdout
    assert "raw-doctor-private-journal" not in result.stdout
    assert "raw-doctor-public-presence" not in result.stdout
    assert "raw-doctor-private-public-profile" not in result.stdout
    assert "raw-doctor-private-presence" not in result.stdout
    assert "raw-doctor-private-runtime-task" not in result.stdout
    assert "raw-doctor-private-operations" not in result.stdout
    assert "raw-doctor-private-worker-ops" not in result.stdout
    assert "raw-doctor-private-persona-editor" not in result.stdout
    assert "raw-doctor-persona-state-secret" not in result.stdout
    assert "raw-doctor-private-bridge-delivery" not in result.stdout
    assert "raw-doctor-private-command" not in result.stdout
    assert "raw-doctor-settings-secret" not in result.stdout
    assert "raw-doctor-private-system-audit" not in result.stdout
