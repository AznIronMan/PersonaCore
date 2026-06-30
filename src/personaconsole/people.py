from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .models import (
    PeopleSurfaceConfig,
    PersonListRow,
    PersonRelationshipSummary,
    PersonTag,
    SurfaceBadge,
)
from .privacy import (
    WITHHELD_PRIVATE_TEXT,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    feature_enabled,
    render_private_text,
)

PEOPLE_FEATURE = "people"

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "red": "bad",
    "rose": "bad",
    "warn": "warn",
    "warning": "warn",
    "degraded": "warn",
    "amber": "warn",
    "yellow": "warn",
    "good": "good",
    "healthy": "good",
    "ok": "good",
    "ready": "good",
    "success": "good",
    "green": "good",
    "info": "info",
    "blue": "info",
    "cyan": "info",
    "neutral": "neutral",
    "unknown": "neutral",
    "": "neutral",
}


def _mapping(value: Any) -> dict[str, Any]:
    if value is None:
        return {}
    if is_dataclass(value):
        return asdict(value)
    if isinstance(value, Mapping):
        return dict(value)
    return {}


def _coerce(value: T | Mapping[str, object], cls: type[T], defaults: Mapping[str, Any] | None = None) -> T:
    if isinstance(value, cls):
        return value
    data = {**(defaults or {}), **_mapping(value)}
    allowed = {field.name for field in fields(cls)}
    data = {key: value for key, value in data.items() if key in allowed}
    return cls(**data)


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _attrs(**attrs: str) -> str:
    parts = []
    for name, value in attrs.items():
        if value:
            parts.append(f' {name.replace("_", "-")}="{escape(value, quote=True)}"')
    return "".join(parts)


def people_surface_feature_enabled(
    config: PeopleSurfaceConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, PeopleSurfaceConfig)
    return bool(model.enabled) and feature_enabled(
        features,
        str(model.feature or PEOPLE_FEATURE),
        default=True,
    )


def render_people_surface(
    config: PeopleSurfaceConfig | Mapping[str, object],
    *,
    features: Mapping[str, bool] | None = None,
    privacy_policy: OwnerPrivateScopePolicy | None = None,
    privacy_context: AdminPrivacyContext | Mapping[str, Any] | None = None,
) -> str:
    model = _coerce(config, PeopleSurfaceConfig)
    if not people_surface_feature_enabled(model, features):
        return ""

    rows = [_coerce(row, PersonListRow) for row in model.rows]
    body = "".join(_person_row_html(row, policy=privacy_policy, context=privacy_context) for row in rows)
    if not body:
        body = (
            '<tr><td colspan="8" class="pc-people-empty">'
            f"{escape(str(model.empty_label or 'No people found.'))}</td></tr>"
        )

    return f"""
<section id="people" class="pc-dashboard-panel pc-people-surface">
  {_panel_head(model.title, model.subtitle)}
  {_people_toolbar(model)}
  {_new_person_panel(model)}
  <div class="pc-people-table-wrap">
    <table class="pc-people-table">
      <thead>
        <tr>
          <th>Name</th>
          <th>External ID</th>
          <th>Trust</th>
          <th>Linked users</th>
          <th>Tags</th>
          <th>Relationship</th>
          <th>Notes summary</th>
          <th>Updated</th>
        </tr>
      </thead>
      <tbody>{body}</tbody>
    </table>
  </div>
</section>
"""


def _panel_head(title: str, subtitle: str) -> str:
    return (
        '<div class="pc-dashboard-panel-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(title or "People"))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(subtitle or ""))}</div>'
        "</div></div>"
    )


def _people_toolbar(config: PeopleSurfaceConfig) -> str:
    if not config.search_action:
        return ""
    reset = ""
    if config.reset_href:
        reset = f'<a class="pc-people-button pc-people-button-muted" href="{escape(config.reset_href, quote=True)}">Reset</a>'
    checked = " checked" if config.unlinked_checked else ""
    return f"""
  <form class="pc-people-toolbar" action="{escape(config.search_action, quote=True)}" method="get">
    <label class="pc-people-search">
      <span>Search</span>
      <input name="q" value="{escape(str(config.search_value), quote=True)}" placeholder="{escape(str(config.search_placeholder), quote=True)}">
    </label>
    <label class="pc-people-check">
      <input type="checkbox" name="{escape(str(config.unlinked_name or 'unlinked'), quote=True)}" value="1"{checked}>
      <span>Unlinked only</span>
    </label>
    <input type="hidden" name="sort" value="{escape(str(config.sort), quote=True)}">
    <input type="hidden" name="direction" value="{escape(str(config.direction), quote=True)}">
    <button class="pc-people-button" type="submit">{escape(str(config.filter_label or "Filter"))}</button>
    {reset}
  </form>
"""


def _new_person_panel(config: PeopleSurfaceConfig) -> str:
    if not config.new_person_html:
        return ""
    open_attr = " open" if config.new_person_open else ""
    return f"""
  <details class="pc-people-new-person"{open_attr}>
    <summary>{escape(str(config.new_person_label or "+ New person"))}</summary>
    <div class="pc-people-new-person-body">{config.new_person_html}</div>
  </details>
"""


def _person_row_html(
    row: PersonListRow,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    title = _link(row.label or row.key or "Person", row.href, "pc-people-name-link")
    subtitle = f'<div class="pc-people-subtitle">{escape(str(row.subtitle))}</div>' if row.subtitle else ""
    badges = _tags_html(row.badges, class_name="pc-people-inline-badges")
    unlinked = '<span class="pc-person-tag pc-person-tag-warn">unlinked</span>' if row.unlinked else ""
    trust = (
        f'<span class="pc-person-tag pc-person-tag-{_tone(row.trust_tone or row.trust_label)}">{escape(str(row.trust_label))}</span>'
        if row.trust_label
        else '<span class="pc-people-muted">&mdash;</span>'
    )
    tags = _tags_html(row.tags) or '<span class="pc-people-muted">&mdash;</span>'
    relationship = _relationship_html(row.relationship)
    notes = _notes_html(row, policy=policy, context=context)
    return f"""
        <tr>
          <td class="pc-people-name-cell">
            <div>{title}{unlinked}{badges}</div>
            {subtitle}
          </td>
          <td class="pc-people-mono">{escape(str(row.external_id or ""))}</td>
          <td>{trust}</td>
          <td class="pc-people-mono">{escape(str(row.linked_users))}</td>
          <td>{tags}</td>
          <td>{relationship}</td>
          <td>{notes}</td>
          <td class="pc-people-muted pc-people-nowrap">{escape(str(row.updated or ""))}</td>
        </tr>
"""


def _link(label: str, href: str, class_name: str) -> str:
    text = escape(str(label))
    if not href:
        return f'<span class="{class_name}">{text}</span>'
    return f'<a class="{class_name}" href="{escape(str(href), quote=True)}">{text}</a>'


def _tag(raw_tag: PersonTag | SurfaceBadge | Mapping[str, object] | str) -> PersonTag:
    if isinstance(raw_tag, str):
        return PersonTag(raw_tag)
    if isinstance(raw_tag, SurfaceBadge):
        return PersonTag(raw_tag.label, tone=raw_tag.tone)
    return _coerce(raw_tag, PersonTag)


def _tags_html(
    tags: Sequence[PersonTag | SurfaceBadge | Mapping[str, object] | str],
    *,
    class_name: str = "pc-person-tags",
) -> str:
    body = []
    for raw_tag in tags:
        tag = _tag(raw_tag)
        if not tag.label:
            continue
        item = (
            f'<span class="pc-person-tag pc-person-tag-{_tone(tag.tone)}"{_attrs(title=tag.title)}>'
            f"{escape(str(tag.label))}</span>"
        )
        if tag.href:
            item = (
                f'<a class="pc-person-tag pc-person-tag-{_tone(tag.tone)}" '
                f'href="{escape(str(tag.href), quote=True)}"{_attrs(title=tag.title)}>'
                f"{escape(str(tag.label))}</a>"
            )
        body.append(item)
    return f'<div class="{class_name}">{"".join(body)}</div>' if body else ""


def _relationship_html(raw_relationship: PersonRelationshipSummary | Mapping[str, object] | None) -> str:
    if not raw_relationship:
        return '<span class="pc-people-muted">low context</span>'
    relationship = _coerce(raw_relationship, PersonRelationshipSummary)
    score = str(relationship.score)
    if not score:
        return '<span class="pc-people-muted">low context</span>'
    tone = _tone(relationship.tone)
    pct = _clamp_percent(relationship.score_percent)
    lanes = _tags_html(relationship.lanes, class_name="pc-person-relationship-tags")
    labels = _tags_html(relationship.labels, class_name="pc-person-relationship-tags")
    meta = f'<div class="pc-people-muted">{escape(str(relationship.meta))}</div>' if relationship.meta else ""
    return f"""
    <div class="pc-person-relationship">
      <div class="pc-person-relationship-score pc-person-relationship-score-{tone}">
        <span>{escape(str(relationship.label or "Persona"))}</span>
        <strong>{escape(score)}</strong>
      </div>
      <div class="pc-person-relationship-track">
        <span class="pc-person-relationship-fill pc-person-relationship-fill-{tone}" style="width: {pct}%"></span>
      </div>
      {lanes}{labels}{meta}
    </div>
"""


def _notes_html(
    row: PersonListRow,
    *,
    policy: OwnerPrivateScopePolicy | None,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
) -> str:
    text = str(row.notes or "")
    scope = str(row.notes_privacy_scope or "")
    if scope:
        if policy is None:
            text = str(row.notes_safe_alternate or "").strip() or WITHHELD_PRIVATE_TEXT
        else:
            text = render_private_text(
                text,
                safe_alternate=row.notes_safe_alternate,
                policy=policy,
                context=context,
                scope=scope,
            )
    if not text:
        return '<span class="pc-people-muted">&mdash;</span>'
    return f'<div class="pc-people-notes" title="{escape(text, quote=True)}">{escape(text)}</div>'


def _clamp_percent(value: int | float) -> int:
    try:
        number = int(round(float(value)))
    except (TypeError, ValueError):
        number = 0
    return max(0, min(number, 100))
