from __future__ import annotations

from dataclasses import asdict, fields, is_dataclass
from html import escape
from typing import Any, Mapping, Sequence, TypeVar

from .controls import render_status_tabs
from .models import (
    LiveRefreshConfig,
    NavGroup,
    NavItem,
    StatusTab,
    SurfaceAdapterBinding,
    SurfaceAssetRequirement,
    SurfaceRegistration,
    SurfaceRegistryConfig,
    SurfaceRegistryIssue,
    SurfaceRegistryReport,
)
from .privacy import feature_enabled

SURFACE_COMPOSITION_FEATURE = "surface_composition"

DEFAULT_KNOWN_SURFACE_FEATURES = (
    "activity",
    "adapter_health",
    "admin_auth",
    "admin_list",
    "agent_ops",
    "availability_monitor",
    "bridge_ops",
    "command_intake",
    "detail_dossier",
    "journal",
    "media",
    "media_library",
    "messages",
    "operations",
    "people",
    "persona",
    "persona_editor",
    "public_presence",
    "review",
    "settings_editor",
    "surface_composition",
    "system_health",
    "terminal_stream",
    "token_health",
    "worker_operations",
)

T = TypeVar("T")

_TONE_ALIASES = {
    "bad": "bad",
    "blocked": "bad",
    "danger": "bad",
    "down": "bad",
    "error": "bad",
    "failed": "bad",
    "missing": "bad",
    "warn": "warn",
    "warning": "warn",
    "disabled": "warn",
    "pending": "warn",
    "unknown": "neutral",
    "good": "good",
    "configured": "good",
    "enabled": "good",
    "ok": "good",
    "ready": "good",
    "info": "info",
    "neutral": "neutral",
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


def _coerce(value: T | Mapping[str, object] | str, cls: type[T], defaults: Mapping[str, Any] | None = None) -> T:
    if isinstance(value, cls):
        return value
    data = dict(defaults or {})
    if isinstance(value, str):
        if cls is SurfaceAssetRequirement:
            data.update({"key": value, "label": value})
        elif cls is SurfaceAdapterBinding:
            data.update({"key": value, "label": value})
        else:
            data.update({"key": value})
    else:
        data.update(_mapping(value))
    allowed = {field.name for field in fields(cls)}
    data = {key: value for key, value in data.items() if key in allowed}
    return cls(**data)


def _tone(value: object) -> str:
    return _TONE_ALIASES.get(str(value or "").strip().lower(), "neutral")


def _key(value: object, default: str = "surface") -> str:
    raw = str(value or default or "").strip().lower().replace("_", "-")
    safe = "".join(char for char in raw if char.isalnum() or char == "-")
    return safe or default


def _safe_href(href: object) -> bool:
    raw = str(href or "").strip()
    if not raw:
        return True
    lowered = raw.lower()
    if lowered.startswith(("#", "/")) and not lowered.startswith("//"):
        return "\\" not in raw and "/.private" not in lowered and "/private/" not in lowered
    return False


def _issue(key: str, message: str, *, level: str = "warn", surface_key: str = "", field: str = "") -> SurfaceRegistryIssue:
    tone = "bad" if level == "error" else ("info" if level == "info" else "warn")
    return SurfaceRegistryIssue(key=key, message=message, level=level, surface_key=surface_key, field=field, tone=tone)


def surface_registry_feature_enabled(
    config: SurfaceRegistryConfig | Mapping[str, object],
    features: Mapping[str, bool] | None = None,
) -> bool:
    model = _coerce(config, SurfaceRegistryConfig)
    return bool(model.enabled) and feature_enabled(features, str(model.feature or SURFACE_COMPOSITION_FEATURE), default=True)


def surface_registry_feature_flags(config: SurfaceRegistryConfig | Mapping[str, object]) -> dict[str, bool]:
    model = _coerce(config, SurfaceRegistryConfig)
    flags = dict(model.features)
    for raw_surface in model.surfaces:
        surface = _coerce(raw_surface, SurfaceRegistration, {"key": "surface", "label": "Surface"})
        if surface.feature and surface.feature not in flags:
            flags[surface.feature] = bool(surface.enabled)
    return flags


def surface_registry_to_nav_groups(config: SurfaceRegistryConfig | Mapping[str, object]) -> tuple[NavGroup, ...]:
    model = _coerce(config, SurfaceRegistryConfig)
    groups: dict[str, list[NavItem]] = {}
    labels: dict[str, str] = {}
    for raw_group in model.nav_groups:
        group = _coerce(raw_group, NavGroup, {"label": "Navigation", "items": ()})
        group_key = str(group.key or group.label or "navigation")
        labels[group_key] = str(group.label or group_key)
        groups.setdefault(group_key, [])
    for raw_surface in model.surfaces:
        surface = _coerce(raw_surface, SurfaceRegistration, {"key": "surface", "label": "Surface"})
        if not surface.enabled or not surface.href:
            continue
        group_key = str(surface.nav_group or "surfaces")
        labels.setdefault(group_key, group_key.replace("-", " ").title())
        groups.setdefault(group_key, []).append(
            NavItem(
                label=str(surface.nav_label or surface.label),
                href=str(surface.href),
                active=str(surface.active or surface.route_key or surface.key) or None,
                feature=str(surface.feature or ""),
            )
        )
    return tuple(NavGroup(label=labels[key], key=key, items=tuple(items)) for key, items in groups.items() if items)


def build_surface_registry_report(
    config: SurfaceRegistryConfig | Mapping[str, object],
    *,
    available_renderers: Mapping[str, bool] | None = None,
    available_assets: Mapping[str, bool] | None = None,
) -> SurfaceRegistryReport:
    model = _coerce(config, SurfaceRegistryConfig)
    renderer_map = dict(available_renderers or {})
    asset_map = dict(available_assets or {})
    known = set(DEFAULT_KNOWN_SURFACE_FEATURES)
    known.update(str(feature) for feature in model.known_features if str(feature or "").strip())
    issues: list[SurfaceRegistryIssue] = []
    route_keys: dict[str, str] = {}
    enabled_count = 0
    disabled_count = 0

    for feature_key in model.features:
        if feature_key and feature_key not in known:
            issues.append(_issue("unknown-feature", f"Unknown feature flag: {feature_key}", field="features"))

    surfaces = tuple(_coerce(surface, SurfaceRegistration, {"key": "surface", "label": "Surface"}) for surface in model.surfaces)
    for surface in surfaces:
        surface_key = str(surface.key or "")
        feature_key = str(surface.feature or "")
        feature_on = feature_enabled(model.features, feature_key, default=True) if feature_key else True
        surface_enabled = bool(surface.enabled and feature_on)
        if surface_enabled:
            enabled_count += 1
        else:
            disabled_count += 1
            level = "warn" if surface.required else "info"
            issues.append(_issue("disabled-surface", f"Surface is disabled: {surface.label}", level=level, surface_key=surface_key, field="enabled"))

        if feature_key and feature_key not in known:
            issues.append(_issue("unknown-feature", f"Unknown surface feature: {feature_key}", surface_key=surface_key, field="feature"))

        if surface.route_key:
            if surface.route_key in route_keys:
                issues.append(
                    _issue(
                        "duplicate-route-key",
                        f"Duplicate route key {surface.route_key} on {surface_key} and {route_keys[surface.route_key]}",
                        level="error",
                        surface_key=surface_key,
                        field="route_key",
                    )
                )
            route_keys[surface.route_key] = surface_key

        if not _safe_href(surface.href):
            issues.append(_issue("unsafe-href", f"Unsafe href for {surface.label}", level="error", surface_key=surface_key, field="href"))

        if surface_enabled and surface.renderer and not bool(renderer_map.get(surface.renderer, False)):
            issues.append(
                _issue(
                    "missing-renderer",
                    f"Missing required renderer {surface.renderer} for {surface.label}",
                    level="error" if surface.required else "warn",
                    surface_key=surface_key,
                    field="renderer",
                )
            )

        for raw_asset in surface.required_assets:
            asset = _coerce(raw_asset, SurfaceAssetRequirement)
            present = bool(asset.present)
            if asset.key in asset_map:
                present = bool(asset_map[asset.key])
            if not _safe_href(asset.href):
                issues.append(_issue("unsafe-asset-href", f"Unsafe asset href for {asset.label or asset.key}", level="error", surface_key=surface_key, field="required_assets"))
            if asset.required and not present:
                issues.append(
                    _issue(
                        "missing-asset",
                        f"Missing required asset {asset.label or asset.key} for {surface.label}",
                        level="error",
                        surface_key=surface_key,
                        field="required_assets",
                    )
                )

    ok = not any(issue.level == "error" for issue in issues)
    return SurfaceRegistryReport(
        ok=ok,
        surface_count=len(surfaces),
        enabled_count=enabled_count,
        disabled_count=disabled_count,
        issue_count=len(issues),
        issues=tuple(issues),
    )


def surface_registry_report_to_dict(report: SurfaceRegistryReport | Mapping[str, object]) -> dict[str, object]:
    model = _coerce(report, SurfaceRegistryReport)
    return {
        "ok": bool(model.ok),
        "surface_count": model.surface_count,
        "enabled_count": model.enabled_count,
        "disabled_count": model.disabled_count,
        "issue_count": model.issue_count,
        "issues": [asdict(_coerce(issue, SurfaceRegistryIssue)) for issue in model.issues],
    }


def _badge(label: object, tone: object = "neutral") -> str:
    return f'<span class="pc-surface-registry-badge pc-dashboard-tone-{_tone(tone)}">{escape(str(label))}</span>'


def _adapter_html(raw_adapter: SurfaceAdapterBinding | Mapping[str, object] | str) -> str:
    adapter = _coerce(raw_adapter, SurfaceAdapterBinding)
    label = adapter.label or adapter.key
    detail = " · ".join(part for part in (adapter.kind, adapter.owner, adapter.summary) if part)
    return (
        f'<li><strong>{escape(str(label))}</strong>'
        f'{_badge(adapter.status, adapter.tone or adapter.status)}'
        f'<span>{escape(detail)}</span></li>'
    )


def _asset_html(raw_asset: SurfaceAssetRequirement | Mapping[str, object] | str) -> str:
    asset = _coerce(raw_asset, SurfaceAssetRequirement)
    label = asset.label or asset.key
    tone = "good" if asset.present else ("bad" if asset.required else "warn")
    status = "present" if asset.present else "missing"
    href = f'<a href="{escape(str(asset.href), quote=True)}">{escape(str(label))}</a>' if asset.href else escape(str(label))
    return f"<li><strong>{href}</strong>{_badge(status, tone)}<span>{escape(str(asset.summary or asset.kind))}</span></li>"


def _surface_card_html(surface: SurfaceRegistration, report: SurfaceRegistryReport) -> str:
    surface_issues = [_coerce(issue, SurfaceRegistryIssue) for issue in report.issues if _coerce(issue, SurfaceRegistryIssue).surface_key == surface.key]
    issue_html = "".join(f'<li>{_badge(issue.level, issue.tone)}<span>{escape(issue.message)}</span></li>' for issue in surface_issues)
    adapters = "".join(_adapter_html(adapter) for adapter in surface.adapters)
    assets = "".join(_asset_html(asset) for asset in surface.required_assets)
    href = f'<a href="{escape(surface.href, quote=True)}">{escape(surface.href)}</a>' if surface.href else ""
    live = "live" if surface.live_refresh else ""
    return (
        f'<article class="pc-surface-registry-card pc-dashboard-tone-{_tone(surface.tone or surface.status)}">'
        '<div class="pc-surface-registry-card-head">'
        f'<div><strong>{escape(str(surface.label))}</strong><span>{escape(str(surface.key))}</span></div>'
        f'<div>{_badge("enabled" if surface.enabled else "disabled", "good" if surface.enabled else "warn")}{_badge(surface.status, surface.tone or surface.status)}</div>'
        '</div>'
        f'<p>{escape(str(surface.summary))}</p>'
        '<dl>'
        f'<div><dt>Feature</dt><dd>{escape(str(surface.feature))}</dd></div>'
        f'<div><dt>Renderer</dt><dd>{escape(str(surface.renderer))}</dd></div>'
        f'<div><dt>Route</dt><dd>{escape(str(surface.route_key))} {href}</dd></div>'
        f'<div><dt>Theme</dt><dd>{escape(str(surface.theme_key))}</dd></div>'
        f'<div><dt>Live</dt><dd>{escape(live)}</dd></div>'
        '</dl>'
        f'{f"<ul>{issue_html}</ul>" if issue_html else ""}'
        f'{f"<h4>Adapters</h4><ul>{adapters}</ul>" if adapters else ""}'
        f'{f"<h4>Assets</h4><ul>{assets}</ul>" if assets else ""}'
        '</article>'
    )


def render_surface_registry_report(
    config: SurfaceRegistryConfig | Mapping[str, object] | None,
    *,
    features: Mapping[str, bool] | None = None,
    available_renderers: Mapping[str, bool] | None = None,
    available_assets: Mapping[str, bool] | None = None,
) -> str:
    if config is None:
        return ""
    model = _coerce(config, SurfaceRegistryConfig)
    if not surface_registry_feature_enabled(model, features):
        return ""
    report = build_surface_registry_report(model, available_renderers=available_renderers, available_assets=available_assets)
    tabs = render_status_tabs(
        (
            StatusTab("Configured", count=report.surface_count, active=True, tone="info"),
            StatusTab("Enabled", count=report.enabled_count, tone="good"),
            StatusTab("Disabled", count=report.disabled_count, tone="warn"),
            StatusTab("Issues", count=report.issue_count, tone="bad" if not report.ok else "good"),
        ),
        aria_label="Surface registry summary",
    )
    issue_rows = "".join(
        f'<li>{_badge(issue.level, issue.tone)}<span>{escape(issue.message)}</span></li>'
        for issue in (_coerce(raw_issue, SurfaceRegistryIssue) for raw_issue in report.issues)
    )
    issue_html = f'<ul class="pc-surface-registry-issues">{issue_rows}</ul>' if issue_rows else '<p class="pc-dashboard-empty">No registry issues found.</p>'
    cards = "".join(_surface_card_html(_coerce(surface, SurfaceRegistration, {"key": "surface", "label": "Surface"}), report) for surface in model.surfaces)
    if not cards:
        cards = f'<p class="pc-dashboard-empty">{escape(str(model.empty_label))}</p>'
    return (
        f'<section id="{escape(_key(model.key, "surface-registry"), quote=True)}" class="pc-surface-registry pc-dashboard-surface">'
        '<div class="pc-dashboard-overview-head"><div>'
        f'<div class="pc-dashboard-section-title">{escape(str(model.title))}</div>'
        f'<div class="pc-dashboard-section-meta">{escape(str(model.subtitle))}</div>'
        f'</div>{_badge("ok" if report.ok else "needs care", "good" if report.ok else "bad")}</div>'
        f'{tabs}<section class="pc-surface-registry-summary">{issue_html}</section>'
        f'<div class="pc-surface-registry-grid">{cards}</div></section>'
    )
