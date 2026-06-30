from personaconsole import (
    ACTIVITY_FEATURE,
    MEDIA_FEATURE,
    MESSAGES_FEATURE,
    ActivityEvent,
    ActivitySurfaceConfig,
    AdminPrivacyContext,
    DashboardAction,
    DashboardFilter,
    DashboardMetric,
    MediaArtifactCard,
    MediaSurfaceConfig,
    MessageAttachment,
    MessageConversation,
    MessageSurfaceConfig,
    MessageTranscriptItem,
    OwnerPrivateScopePolicy,
    SurfaceBadge,
    activity_surface_feature_enabled,
    media_surface_feature_enabled,
    message_surface_feature_enabled,
    render_activity_surface,
    render_media_surface,
    render_message_surface,
    render_surface_sections,
)


def _policy() -> OwnerPrivateScopePolicy:
    return OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})


def _owner() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="owner_private",
        viewer_person_key="owner",
        allowed_scopes=("public", "operator", "owner_private"),
    )


def _operator() -> AdminPrivacyContext:
    return AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )


def _message_config() -> MessageSurfaceConfig:
    return MessageSurfaceConfig(
        enabled=True,
        title="<Messages>",
        filters=[
            DashboardFilter("<All>", "/messages?platform=all", key="12", active=True),
            DashboardFilter("Provider", "/messages?platform=provider", key="7"),
        ],
        metrics=[
            DashboardMetric("Threads", 2, "/messages", "visible"),
            DashboardMetric("Selected", "1", "/messages?thread=thread-1", "active", tone="info"),
        ],
        actions=[DashboardAction("Raw rows", "/messages?view=raw", tone="neutral")],
        conversations=[
            MessageConversation(
                "thread-1",
                "<Direct thread>",
                href="/messages/thread-1?raw=<1>",
                provider="<provider>",
                participant="<participant>",
                summary="raw owner-private summary",
                safe_alternate="operator-safe thread summary",
                timestamp="now",
                unread=2,
                tone="warn",
                privacy_scope="owner_private",
                badges=[SurfaceBadge("<private>", "warn")],
            )
        ],
        transcript=[
            MessageTranscriptItem(
                "<Owner>",
                "raw owner-private dm text",
                timestamp="09:41",
                direction="outgoing",
                provider="<provider>",
                meta="<audit meta>",
                href="/messages/thread-1/raw-message",
                privacy_scope="owner_private",
                safe_alternate="operator-safe dm summary",
                attachments=[
                    MessageAttachment(
                        "raw private media filename",
                        href="/media/raw-private-file",
                        preview_url="/media/raw-private-preview",
                        media_type="image",
                        detail="raw attachment detail",
                        safe_alternate="operator-safe attachment",
                        privacy_scope="owner_private",
                        tone="info",
                    )
                ],
            )
        ],
        selected_key="thread-1",
        conversation_title="Threads",
        transcript_title="Selected thread",
        transcript_meta="1 visible message",
    )


def test_message_surface_redacts_owner_private_content_for_operator():
    html = render_message_surface(
        _message_config(),
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert 'id="messages"' in html
    assert "&lt;Messages&gt;" in html
    assert "pc-message-controls" in html
    assert "&lt;All&gt;" in html
    assert "Raw rows" in html
    assert "Threads" in html
    assert "Selected thread" in html
    assert "1 visible message" in html
    assert "operator-safe thread summary" in html
    assert "operator-safe dm summary" in html
    assert "operator-safe attachment" in html
    assert "raw owner-private" not in html
    assert "raw-private-file" not in html
    assert "raw-private-preview" not in html
    assert "is-private" in html


def test_message_surface_owner_can_see_raw_private_content_and_links():
    html = render_message_surface(
        _message_config(),
        privacy_policy=_policy(),
        privacy_context=_owner(),
    )

    assert "raw owner-private summary" in html
    assert "raw owner-private dm text" in html
    assert "raw private media filename" in html
    assert "/media/raw-private-file" in html
    assert "/media/raw-private-preview" in html
    assert "operator-safe dm summary" not in html


def test_surface_feature_flags_hide_enabled_configs():
    messages = MessageSurfaceConfig(enabled=True, conversations=[MessageConversation("one", "One")])
    activity = ActivitySurfaceConfig(enabled=True, events=[ActivityEvent("Runtime", "Started")])
    media = MediaSurfaceConfig(enabled=True, cards=[MediaArtifactCard("Asset")])

    assert message_surface_feature_enabled(messages, {MESSAGES_FEATURE: True}) is True
    assert activity_surface_feature_enabled(activity, {ACTIVITY_FEATURE: True}) is True
    assert media_surface_feature_enabled(media, {MEDIA_FEATURE: True}) is True
    assert render_message_surface(messages, features={MESSAGES_FEATURE: False}) == ""
    assert render_activity_surface(activity, features={ACTIVITY_FEATURE: False}) == ""
    assert render_media_surface(media, features={MEDIA_FEATURE: False}) == ""


def test_activity_and_media_surfaces_redact_and_strip_private_urls():
    activity = ActivitySurfaceConfig(
        enabled=True,
        events=[
            ActivityEvent(
                "DM",
                "raw private activity title",
                href="/activity/raw",
                summary="raw private activity summary",
                privacy_scope="owner_private",
            )
        ],
    )
    media = MediaSurfaceConfig(
        enabled=True,
        cards=[
            MediaArtifactCard(
                "raw private artifact",
                href="/artifact/raw",
                preview_url="/artifact/raw-preview",
                detail="raw private artifact detail",
                safe_alternate="operator-safe media summary",
                privacy_scope="owner_private",
            )
        ],
    )

    html = render_surface_sections(
        activity=activity,
        media=media,
        privacy_policy=_policy(),
        privacy_context=_operator(),
    )

    assert 'id="activity"' in html
    assert 'id="media"' in html
    assert "[owner-private content withheld]" in html
    assert "operator-safe media summary" in html
    assert "raw private activity" not in html
    assert "raw private artifact" not in html
    assert "/activity/raw" not in html
    assert "/artifact/raw" not in html
    assert "/artifact/raw-preview" not in html


def test_private_scope_without_policy_fails_closed():
    html = render_media_surface(
        MediaSurfaceConfig(
            enabled=True,
            cards=[
                {
                    "label": "raw label",
                    "href": "/raw-file",
                    "preview_url": "/raw-preview",
                    "privacy_scope": "owner_private",
                    "safe_alternate": "safe card",
                }
            ],
        )
    )

    assert "safe card" in html
    assert "raw label" not in html
    assert "/raw-file" not in html
    assert "/raw-preview" not in html


def test_surface_empty_states_are_explicit():
    html = render_surface_sections(
        messages=MessageSurfaceConfig(enabled=True),
        activity=ActivitySurfaceConfig(enabled=True),
        media=MediaSurfaceConfig(enabled=True),
    )

    assert "No conversations found." in html
    assert "Select a conversation" in html
    assert "No recent activity found." in html
    assert "No media artifacts found." in html
