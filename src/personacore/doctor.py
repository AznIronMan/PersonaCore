"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.doctor import (
    ConsumerIntegrationDoctorReport,
    DoctorCheck,
    ModuleSnapshot,
    doctor_report_to_text,
    main,
    run_consumer_integration_doctor,
)

__all__ = [
    "ConsumerIntegrationDoctorReport",
    "DoctorCheck",
    "ModuleSnapshot",
    "doctor_report_to_text",
    "main",
    "run_consumer_integration_doctor",
]
