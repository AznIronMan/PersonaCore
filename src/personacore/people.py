"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.models import (
    PeopleSurfaceConfig,
    PersonListRow,
    PersonRelationshipSummary,
    PersonTag,
)
from personaconsole.people import (
    PEOPLE_FEATURE,
    people_surface_feature_enabled,
    render_people_surface,
)

__all__ = [
    "PEOPLE_FEATURE",
    "PeopleSurfaceConfig",
    "PersonListRow",
    "PersonRelationshipSummary",
    "PersonTag",
    "people_surface_feature_enabled",
    "render_people_surface",
]
