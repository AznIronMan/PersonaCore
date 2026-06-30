"""Deprecated personacore compatibility wrapper for personaconsole."""

from personaconsole.models import (
    ReviewAgendaItem,
    ReviewBoardRow,
    ReviewQueueCard,
    ReviewQueueSection,
    ReviewSurfaceConfig,
)
from personaconsole.review import (
    REVIEW_FEATURE,
    render_review_surface,
    review_surface_feature_enabled,
)

__all__ = [
    "REVIEW_FEATURE",
    "ReviewAgendaItem",
    "ReviewBoardRow",
    "ReviewQueueCard",
    "ReviewQueueSection",
    "ReviewSurfaceConfig",
    "render_review_surface",
    "review_surface_feature_enabled",
]
