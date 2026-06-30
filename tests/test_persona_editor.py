from personaconsole import (
    PERSONA_EDITOR_FEATURE,
    AdminPrivacyContext,
    OwnerPrivateScopePolicy,
    PersonaChangeRow,
    PersonaEditorConfig,
    PersonaProfileField,
    PersonaProfileSection,
    PersonaProposalCard,
    PersonaRuleRow,
    PersonaStateField,
    PersonaTraitRow,
    StatusTab,
    SurfaceAction,
    SurfaceBadge,
    persona_editor_feature_enabled,
    render_persona_editor,
)


def _policy() -> OwnerPrivateScopePolicy:
    return OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})


def _operator() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )


def _owner() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="owner_private",
        viewer_person_key="owner",
        allowed_scopes=("public", "operator", "owner_private"),
    )


def _config() -> PersonaEditorConfig:
    return PersonaEditorConfig(
        enabled=True,
        title="<Persona Editor>",
        subtitle="Profile, traits, rules, state, and proposals",
        tabs=[
            StatusTab("All", "/persona/editor", 9, active=True),
            StatusTab("Pending", "/persona/editor?status=pending", 2, tone="warn"),
        ],
        profile_sections=[
            PersonaProfileSection(
                "identity",
                "Identity",
                "Generic profile section",
                fields=[
                    PersonaProfileField("display", "<Display>", "Example Persona", status="approved", tone="good"),
                    PersonaProfileField(
                        "private-profile",
                        "Private profile note",
                        "raw private profile field",
                        href="/persona/profile/raw-private",
                        privacy_scope="owner_private",
                        safe_alternate="safe profile field",
                    ),
                ],
            )
        ],
        traits=[
            PersonaTraitRow("warmth", "Warmth", "+4", "high", "approved", "good", "Public trait summary"),
            PersonaTraitRow(
                "private-trait",
                "Private trait",
                status="pending-review",
                tone="warn",
                summary="raw private trait summary",
                href="/persona/traits/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe trait summary",
            ),
        ],
        rules=[
            PersonaRuleRow("reply-tone", "Reply Tone", "Keep replies concise.", "voice", 2, "approved", "good"),
            PersonaRuleRow(
                "private-rule",
                "Private Rule",
                "raw private rule text",
                "owner",
                1,
                "draft",
                "info",
                href="/persona/rules/raw-private",
                privacy_scope="owner_private",
                safe_alternate="safe rule text",
            ),
        ],
        state_fields=[
            PersonaStateField("mode", "Runtime mode", "review", status="draft", tone="info", changed=True, pending_value="active"),
            PersonaStateField(
                "state-secret",
                "State secret",
                "raw-state-secret",
                pending_value="new-raw-state-secret",
                pending_display_value="new state staged",
                field_type="secret",
                status="pending-review",
                tone="warn",
                changed=True,
                secret=True,
                actions=[SurfaceAction("Reveal", "/persona/state/reveal", "info")],
            ),
        ],
        proposals=[
            PersonaProposalCard(
                "proposal-one",
                "Trait proposal",
                "pending-review",
                "warn",
                "Review proposed trait update.",
                "operator",
                "trait:warmth",
                "runtime",
                "09:00",
                "/persona/proposals/one",
                changes=[
                    PersonaChangeRow("change-one", "Warmth", "+3", "+4", "pending", "warn", "runtime", "09:00"),
                    PersonaChangeRow(
                        "private-change",
                        "Private change",
                        "raw before private",
                        "raw after private",
                        "held",
                        "bad",
                        "runtime",
                        "09:01",
                        privacy_scope="owner_private",
                        safe_alternate="safe private change",
                    ),
                ],
                badges=[SurfaceBadge("review", "warn")],
                actions=[
                    SurfaceAction("Approve", "/persona/proposals/one/approve", "good", method="post"),
                    SurfaceAction("Archive", "", "neutral", disabled=True),
                ],
            )
        ],
        history=[
            PersonaChangeRow("history-one", "Rule status", "draft", "approved", "applied", "good", "operator", "08:00")
        ],
        actions=[SurfaceAction("New proposal", "/persona/proposals/new", "info")],
    )


def test_persona_editor_renders_sections_proposals_and_redacts_private_text():
    html = render_persona_editor(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert "pc-persona-editor-surface" in html
    assert "&lt;Persona Editor&gt;" in html
    assert "pc-status-tabs" in html
    assert "Identity" in html
    assert "&lt;Display&gt;" in html
    assert "safe profile field" in html
    assert "Traits" in html
    assert "Warmth" in html
    assert "safe trait summary" in html
    assert "Rules" in html
    assert "safe rule text" in html
    assert "Mutable State" in html
    assert "Runtime mode" in html
    assert "changed" in html
    assert "new state staged" in html
    assert "Proposals" in html
    assert "Trait proposal" in html
    assert "Review proposed trait update." in html
    assert 'data-method="POST"' in html
    assert 'aria-disabled="true"' in html
    assert "safe private change" in html
    assert "Change History" in html
    assert "Rule status" in html
    assert "raw private profile field" not in html
    assert "raw private trait summary" not in html
    assert "raw private rule text" not in html
    assert "raw before private" not in html
    assert "raw after private" not in html
    assert "raw-state-secret" not in html
    assert "new-raw-state-secret" not in html
    assert "/persona/profile/raw-private" not in html
    assert "/persona/traits/raw-private" not in html
    assert "/persona/rules/raw-private" not in html


def test_persona_editor_owner_can_see_private_raw_values_and_links():
    html = render_persona_editor(
        _config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw private profile field" in html
    assert "raw private trait summary" in html
    assert "raw private rule text" in html
    assert "raw before private" in html
    assert "raw after private" in html
    assert "/persona/profile/raw-private" in html
    assert "/persona/traits/raw-private" in html
    assert "/persona/rules/raw-private" in html
    assert "safe profile field" not in html


def test_persona_editor_feature_gate_and_empty_state():
    config = PersonaEditorConfig(enabled=True)

    assert persona_editor_feature_enabled(config, {PERSONA_EDITOR_FEATURE: True}) is True
    assert persona_editor_feature_enabled(config, {PERSONA_EDITOR_FEATURE: False}) is False
    assert render_persona_editor(config, features={PERSONA_EDITOR_FEATURE: False}) == ""

    html = render_persona_editor(config)

    assert "No persona editor items configured." in html
