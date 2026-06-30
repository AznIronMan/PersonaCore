from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Mapping, Sequence


OWNER_PRIVATE_ADMIN_FEATURE = "owner_private_admin"
WITHHELD_PRIVATE_TEXT = "[owner-private content withheld]"


class PrivacyRenderMode(str, Enum):
    RAW = "raw"
    SAFE_ALTERNATE = "safe_alternate"
    WITHHELD = "withheld"
    HIDDEN = "hidden"


def _normalize_key(value: object) -> str:
    return str(value or "").strip().lower().replace("-", "_").replace(" ", "_")


def _dedupe(values: Sequence[str]) -> tuple[str, ...]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        clean = _normalize_key(value)
        if clean and clean not in seen:
            seen.add(clean)
            result.append(clean)
    return tuple(result)


@dataclass(frozen=True)
class AdminPrivacyContext:
    access_tier: str = "operator"
    viewer_person_key: str = ""
    allowed_scopes: Sequence[str] = field(default_factory=tuple)
    read_only: bool = False

    @classmethod
    def from_mapping(cls, value: Mapping[str, Any] | None) -> "AdminPrivacyContext":
        data = dict(value or {})
        scopes = data.get("allowed_scopes") or data.get("scopes") or ()
        if isinstance(scopes, str):
            scopes = [part.strip() for part in scopes.split(",")]
        return cls(
            access_tier=str(data.get("access_tier") or data.get("tier") or "operator"),
            viewer_person_key=str(data.get("viewer_person_key") or data.get("person_key") or ""),
            allowed_scopes=tuple(str(scope) for scope in scopes if str(scope or "").strip()),
            read_only=bool(data.get("read_only")),
        )

    @property
    def normalized_tier(self) -> str:
        return _normalize_key(self.access_tier)

    @property
    def normalized_person_key(self) -> str:
        return _normalize_key(self.viewer_person_key)


@dataclass(frozen=True)
class OwnerPrivateScopePolicy:
    owner_private_scopes: Mapping[str, Sequence[str]] = field(default_factory=dict)
    aliases: Mapping[str, str] = field(default_factory=dict)
    direct_surfaces: Sequence[str] = (
        "dm",
        "direct",
        "direct_message",
        "private_dm",
        "private_message",
        "discord_dm",
        "instagram_dm",
        "phone_sms",
        "sms",
    )

    def __post_init__(self) -> None:
        scopes: dict[str, tuple[str, ...]] = {}
        for scope, owners in self.owner_private_scopes.items():
            clean_scope = _normalize_key(scope)
            if clean_scope:
                scopes[clean_scope] = _dedupe(tuple(str(owner) for owner in owners))
        alias_map = {
            _normalize_key(alias): _normalize_key(target)
            for alias, target in self.aliases.items()
            if _normalize_key(alias) and _normalize_key(target)
        }
        direct = _dedupe(tuple(str(surface) for surface in self.direct_surfaces))
        object.__setattr__(self, "owner_private_scopes", scopes)
        object.__setattr__(self, "aliases", alias_map)
        object.__setattr__(self, "direct_surfaces", direct)

    def canonical_scope(self, scope: str | None) -> str:
        clean = _normalize_key(scope)
        seen: set[str] = set()
        while clean in self.aliases and clean not in seen:
            seen.add(clean)
            clean = self.aliases[clean]
        return clean

    def is_owner_private_scope(self, scope: str | None) -> bool:
        return self.canonical_scope(scope) in self.owner_private_scopes

    def owner_scopes_for_person(self, person_key: str | None) -> tuple[str, ...]:
        clean_person = _normalize_key(person_key)
        if not clean_person:
            return ()
        return tuple(
            scope
            for scope, owners in self.owner_private_scopes.items()
            if clean_person in owners
        )

    def scope_owners(self, scope: str | None) -> tuple[str, ...]:
        return tuple(self.owner_private_scopes.get(self.canonical_scope(scope), ()))

    def context_scopes(self, context: AdminPrivacyContext | Mapping[str, Any] | None) -> tuple[str, ...]:
        privacy = context if isinstance(context, AdminPrivacyContext) else AdminPrivacyContext.from_mapping(context)
        raw_scopes = tuple(str(scope) for scope in privacy.allowed_scopes)
        if not raw_scopes:
            raw_scopes = (privacy.access_tier,)
        return tuple(self.canonical_scope(scope) for scope in raw_scopes if self.canonical_scope(scope))

    def is_direct_surface(self, surface: str | None) -> bool:
        return _normalize_key(surface) in self.direct_surfaces


def canonical_privacy_scope(scope: str | None, policy: OwnerPrivateScopePolicy | None = None) -> str:
    if policy is None:
        return _normalize_key(scope)
    return policy.canonical_scope(scope)


def can_view_raw_private(
    policy: OwnerPrivateScopePolicy,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
    scope: str | None,
) -> bool:
    privacy = context if isinstance(context, AdminPrivacyContext) else AdminPrivacyContext.from_mapping(context)
    clean_scope = policy.canonical_scope(scope)
    owners = set(policy.scope_owners(clean_scope))
    if not clean_scope or not owners:
        return False
    if privacy.normalized_person_key not in owners:
        return False
    context_scopes = set(policy.context_scopes(privacy))
    return clean_scope in context_scopes or privacy.normalized_tier == clean_scope


def privacy_render_mode(
    policy: OwnerPrivateScopePolicy,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
    scope: str | None,
    *,
    has_safe_alternate: bool = False,
    hide_without_safe_alternate: bool = False,
) -> PrivacyRenderMode:
    clean_scope = policy.canonical_scope(scope)
    if not policy.is_owner_private_scope(clean_scope):
        return PrivacyRenderMode.RAW
    if can_view_raw_private(policy, context, clean_scope):
        return PrivacyRenderMode.RAW
    if has_safe_alternate:
        return PrivacyRenderMode.SAFE_ALTERNATE
    if hide_without_safe_alternate:
        return PrivacyRenderMode.HIDDEN
    return PrivacyRenderMode.WITHHELD


def render_private_text(
    text: str | None,
    *,
    safe_alternate: str | None = None,
    policy: OwnerPrivateScopePolicy,
    context: AdminPrivacyContext | Mapping[str, Any] | None,
    scope: str | None,
    withheld_text: str = WITHHELD_PRIVATE_TEXT,
) -> str:
    mode = privacy_render_mode(
        policy,
        context,
        scope,
        has_safe_alternate=bool(str(safe_alternate or "").strip()),
    )
    if mode == PrivacyRenderMode.RAW:
        return str(text or "")
    if mode == PrivacyRenderMode.SAFE_ALTERNATE:
        return str(safe_alternate or "")
    if mode == PrivacyRenderMode.HIDDEN:
        return ""
    return withheld_text


def owner_private_scope_for_content(
    policy: OwnerPrivateScopePolicy,
    *,
    privacy_scope: str | None = None,
    sender_person_key: str | None = None,
    receiver_person_key: str | None = None,
    participant_person_keys: Sequence[str] = (),
    surface: str | None = None,
    is_direct: bool = False,
) -> str | None:
    explicit_scope = policy.canonical_scope(privacy_scope)
    if policy.is_owner_private_scope(explicit_scope):
        return explicit_scope
    if not is_direct and not policy.is_direct_surface(surface):
        return None
    participants = (
        str(sender_person_key or ""),
        str(receiver_person_key or ""),
        *(str(person) for person in participant_person_keys),
    )
    for person_key in participants:
        scopes = policy.owner_scopes_for_person(person_key)
        if scopes:
            return scopes[0]
    return None


def feature_enabled(features: Mapping[str, bool] | None, key: str, *, default: bool = False) -> bool:
    if not key:
        return True
    if not features:
        return default
    return bool(features.get(key, default))
