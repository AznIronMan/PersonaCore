import json
import subprocess
import sys

from persona_console.doctor import doctor_report_to_text, run_consumer_integration_doctor


def test_consumer_integration_doctor_passes_current_source():
    report = run_consumer_integration_doctor(expected_version="1.0.16")
    data = report.as_dict()

    assert report.ok is True
    assert data["persona_console"]["version"] == "1.0.16"
    assert data["personacore"]["version"] == "1.0.16"
    assert data["persona_console"]["path"] == ""
    assert data["personacore"]["path"] == ""
    assert "raw-doctor-secret" not in str(data)
    assert any(check["key"] == "adapter_health_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "controls_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "token_health_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "surface_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "people_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "review_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "owner_private_render" and check["ok"] for check in data["checks"])
    assert any(check["key"] == "shell_render" and check["ok"] for check in data["checks"])


def test_consumer_integration_doctor_detects_expected_version_mismatch():
    report = run_consumer_integration_doctor(expected_version="0.0.0")

    assert report.ok is False
    assert any(check.key == "expected_version_match" and not check.ok for check in report.checks)


def test_consumer_integration_doctor_text_is_public_safe_by_default():
    report = run_consumer_integration_doctor(expected_version="1.0.16")
    text = doctor_report_to_text(report)

    assert "PersonaCore consumer integration doctor: ok" in text
    assert "raw-doctor-secret" not in text
    assert "raw-doctor-private-message" not in text
    assert "raw-doctor-private-people-note" not in text
    assert "raw-doctor-private-review-summary" not in text
    assert report.persona_console.path == ""
    assert report.personacore.path == ""


def test_consumer_integration_doctor_script_json():
    result = subprocess.run(
        [
            sys.executable,
            "scripts/consumer_integration_doctor.py",
            "--expected-version",
            "1.0.16",
            "--json",
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(result.stdout)
    assert payload["ok"] is True
    assert payload["persona_console"]["version"] == "1.0.16"
    assert payload["personacore"]["version"] == "1.0.16"
    assert payload["persona_console"]["path"] == ""
    assert "raw-doctor-secret" not in result.stdout
    assert "raw-doctor-private-message" not in result.stdout
    assert "raw-doctor-private-people-note" not in result.stdout
    assert "raw-doctor-private-review-summary" not in result.stdout
