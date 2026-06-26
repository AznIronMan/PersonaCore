from __future__ import annotations

import argparse
import os
from pathlib import Path

from personacore import (
    ACTIVITY_FEATURE,
    MEDIA_FEATURE,
    MESSAGES_FEATURE,
    ActivityEvent,
    ActivitySurfaceConfig,
    AdminPrivacyContext,
    DashboardActivityItem,
    DashboardAdapterCard,
    DashboardAttention,
    DashboardAttentionItem,
    DashboardData,
    DashboardFilter,
    DashboardFlow,
    DashboardFlowBucket,
    DashboardFlowSegment,
    DashboardHealthMetric,
    DashboardHealthStrip,
    DashboardMetric,
    DashboardQueueRow,
    DashboardRouteCard,
    DashboardSparkBucket,
    MediaArtifactCard,
    MediaSurfaceConfig,
    MessageAttachment,
    MessageConversation,
    MessageSurfaceConfig,
    MessageTranscriptItem,
    NavGroup,
    NavItem,
    OwnerPrivateScopePolicy,
    PersonaCoreConfig,
    StatusPill,
    SurfaceBadge,
    ThemeTokens,
    TokenHealthCheck,
    TokenHealthConfig,
    UserPill,
    register_static_assets,
    render_dashboard_sections,
    render_shell_html,
    render_surface_sections,
)


def build_fixture_config(*, static_base_url: str = "/persona-console/static") -> PersonaCoreConfig:
    return PersonaCoreConfig(
        brand_name="Example Persona",
        page_title="Runtime Dashboard",
        page_subtitle="Shared admin overview",
        active="dashboard",
        features={MESSAGES_FEATURE: True, ACTIVITY_FEATURE: True, MEDIA_FEATURE: True},
        nav_groups=[
            NavGroup(
                "Core",
                [
                    NavItem("Dashboard", "/", active="dashboard"),
                    NavItem("Messages", "/messages", active="messages", badge="messages", feature=MESSAGES_FEATURE),
                    NavItem("Activity", "/activity", active="activity", feature=ACTIVITY_FEATURE),
                ],
                key="core",
            ),
            NavGroup(
                "Operations",
                [
                    NavItem("Review Queue", "/review", active="review", badge="review"),
                    NavItem("Media", "/media", active="media", feature=MEDIA_FEATURE),
                    NavItem("Workers", "/workers", active="workers", badge="workers"),
                ],
                key="operations",
            ),
            NavGroup(
                "Runtime",
                [
                    NavItem("Configuration", "/configuration", active="configuration"),
                    NavItem("Health", "/health", active="health"),
                ],
                key="runtime",
            ),
        ],
        nav_badges={"messages": 12, "review": 4, "workers": 1},
        status_pills=[
            StatusPill("Runtime healthy", "good"),
            StatusPill("Review 4", "info"),
            StatusPill("Worker lag", "warn"),
        ],
        user=UserPill(
            display_name="Operator",
            username="operator",
            tier="admin",
            source="fixture",
        ),
        app_version="v1.0.9-fixture",
        static_base_url=static_base_url,
        theme=ThemeTokens(
            accent="rgb(20 184 166)",
            accent_soft="rgb(153 246 228)",
            accent_surface="rgb(19 78 74 / 0.36)",
            background="rgb(11 18 32)",
            surface="rgb(17 24 39)",
            surface_raised="rgb(17 24 39 / 0.98)",
            surface_muted="rgb(31 41 55 / 0.74)",
        ),
        live_url="/fragments/dashboard",
        live_interval=30,
        live_hold_selector="[data-live-hold]",
    )


def render_dashboard_fragment() -> str:
    privacy_policy = OwnerPrivateScopePolicy(owner_private_scopes={"owner_private": ("owner",)})
    operator_context = AdminPrivacyContext(
        access_tier="operator",
        viewer_person_key="operator",
        allowed_scopes=("public", "operator"),
    )
    dashboard = DashboardData(
        attention=DashboardAttention(
            title="Runtime Overview",
            subtitle="Current shared admin state for a generic persona runtime",
            label="Needs operator pass",
            tone="warn",
            count=3,
            refreshed_label="refreshed just now",
            items=[
                DashboardAttentionItem("Review", 4, "Items waiting for operator review.", "/review", tone="warn"),
                DashboardAttentionItem("Workers", "42s", "Queue latency is above target.", "/workers", tone="bad"),
                DashboardAttentionItem("Media", 9, "Jobs queued or processing.", "/media", tone="info"),
            ],
        ),
        filters=[
            DashboardFilter("All routes", "/", active=True, color="rgb(153 246 228)"),
            DashboardFilter("Messages", "/?platform=messages", key="messages", color="rgb(56 189 248)"),
            DashboardFilter("Media", "/?platform=media", key="media", color="rgb(244 114 182)"),
            DashboardFilter("Workers", "/?platform=workers", key="workers", color="rgb(251 191 36)"),
        ],
        metrics=[
            DashboardMetric("Open reviews", 4, "/review", "Needs operator pass", tone="warn"),
            DashboardMetric("Messages today", 128, "/messages", "Across active channels", tone="info"),
            DashboardMetric("Media jobs", 9, "/media", "Queued or processing"),
            DashboardMetric("Worker latency", "42s", "/workers", "P95 over last hour", tone="bad"),
        ],
        routes=[
            DashboardRouteCard("Review Queue", "/review", "Approve, hold, or dismiss items.", metric=4, tone="warn"),
            DashboardRouteCard("Messages", "/messages", "Scan conversations and handoffs.", metric=128, tone="info"),
            DashboardRouteCard("Media", "/media", "Track generation and publishing status.", metric=9),
            DashboardRouteCard("Workers", "/workers", "Inspect queue health and retries.", metric="42s", tone="bad"),
        ],
        health=DashboardHealthStrip(
            "Runtime health",
            "/health",
            tone="good",
            meta="fixture host · sampled just now",
            metrics=[
                DashboardHealthMetric("CPU", "18%", "within normal band", tone="good"),
                DashboardHealthMetric("RAM", "61%", "stable", tone="good"),
                DashboardHealthMetric("Disk", "72%", "watch growth", tone="warn"),
                DashboardHealthMetric("Network", "ok", "adapter reachable", tone="good"),
            ],
        ),
        token_health=TokenHealthConfig(
            enabled=True,
            subtitle="Fixture credentials are status-only examples",
            checks=[
                TokenHealthCheck(
                    "social_provider",
                    "Social provider token",
                    "Social",
                    ["SOCIAL_PROVIDER_TOKEN"],
                    configured=True,
                ),
                TokenHealthCheck(
                    "messaging_provider",
                    "Messaging provider token",
                    "Messaging",
                    ["MESSAGING_PROVIDER_TOKEN"],
                    configured=True,
                ),
                TokenHealthCheck(
                    "webhook_verify",
                    "Webhook verify token",
                    "Webhooks",
                    ["WEBHOOK_VERIFY_TOKEN"],
                    required=False,
                    configured=False,
                ),
            ],
        ),
        adapters=[
            DashboardAdapterCard(
                "Messages",
                "healthy",
                "/messages",
                tone="good",
                route="inbound/outbound",
                policy="reply route enabled",
                last_in="2m ago",
                last_out="1m ago",
                counts=["128 in/24h", "117 out/24h"],
                sparkline=[
                    DashboardSparkBucket("oldest", 28, tone="good"),
                    DashboardSparkBucket("-6h", 42, tone="good"),
                    DashboardSparkBucket("-5h", 36, tone="good"),
                    DashboardSparkBucket("-4h", 63, tone="info"),
                    DashboardSparkBucket("-3h", 50, tone="good"),
                    DashboardSparkBucket("-2h", 74, tone="info"),
                    DashboardSparkBucket("now", 58, tone="good"),
                ],
            ),
            DashboardAdapterCard(
                "Workers",
                "lagging",
                "/workers",
                tone="warn",
                route="background queue",
                policy="retry on failure",
                last_in="4m ago",
                last_out="6m ago",
                counts=[{"label": "1 queued", "tone": "warn"}, {"label": "0 failed", "tone": "good"}],
                detail="One queue is above the expected latency target.",
            ),
        ],
        flow=DashboardFlow(
            "Message flow",
            "Last 12 hours",
            inbound_total=128,
            outbound_total=117,
            buckets=[
                DashboardFlowBucket("00", 20, 16, segments=[DashboardFlowSegment("messages", 80, tone="info")]),
                DashboardFlowBucket("01", 35, 28, segments=[DashboardFlowSegment("messages", 65, tone="info")]),
                DashboardFlowBucket("02", 26, 20, segments=[DashboardFlowSegment("media", 20, tone="warn")]),
                DashboardFlowBucket("03", 50, 46, segments=[DashboardFlowSegment("messages", 72, tone="info")]),
                DashboardFlowBucket("04", 44, 39),
                DashboardFlowBucket("05", 66, 61, segments=[DashboardFlowSegment("media", 30, tone="warn")]),
                DashboardFlowBucket("06", 58, 51),
                DashboardFlowBucket("07", 72, 69, segments=[DashboardFlowSegment("messages", 70, tone="info")]),
                DashboardFlowBucket("08", 65, 60),
                DashboardFlowBucket("09", 84, 76),
                DashboardFlowBucket("10", 62, 57),
                DashboardFlowBucket("11", 77, 70),
            ],
        ),
        queue=[
            DashboardQueueRow("Pending", 4, "/pending?status=pending", tone="warn"),
            DashboardQueueRow("Applied", 22, "/pending?status=applied", tone="good"),
            DashboardQueueRow("Failed", 1, "/pending?status=failed", tone="bad"),
            DashboardQueueRow("Cancelled", 2, "/pending?status=cancelled"),
        ],
        activity=[
            DashboardActivityItem("Review", "Four items queued", "/review", "09:42", "Waiting for operator pass.", tone="warn"),
            DashboardActivityItem("Messages", "Conversation summary refreshed", "/messages", "09:38", "Active channel state updated.", tone="info"),
            DashboardActivityItem("Workers", "Latency warning", "/workers", "09:31", "One worker is above target.", tone="bad"),
            DashboardActivityItem("Media", "Assets ready", "/media", "09:26", "Three generated assets are ready for inspection.", tone="good"),
        ],
    )
    hold_form = """
<section class="panel">
  <div class="panel-head">
    <h2>Live Controls</h2>
    <span class="hint">30s cadence</span>
  </div>
  <form>
    <label>
      Queue filter
      <select data-live-hold>
        <option>All queues</option>
        <option>Review only</option>
        <option>Worker lag</option>
      </select>
    </label>
    <label>
      Operator note
      <textarea rows="4" data-live-hold placeholder="Hold live refresh while editing"></textarea>
    </label>
    <button type="button">Apply</button>
  </form>
</section>
"""
    surfaces = render_surface_sections(
        messages=MessageSurfaceConfig(
            enabled=True,
            conversations=[
                MessageConversation(
                    "thread-1",
                    "Example customer thread",
                    href="/messages/thread-1",
                    provider="Chat",
                    participant="Consumer",
                    summary="Conversation needs a response handoff.",
                    timestamp="09:42",
                    unread=2,
                    tone="warn",
                    badges=[SurfaceBadge("reply", "warn")],
                ),
                MessageConversation(
                    "thread-2",
                    "Owner-private direct thread",
                    href="/messages/thread-2/raw",
                    provider="Direct",
                    participant="Owner",
                    summary="raw fixture private thread text",
                    safe_alternate="Owner-private thread has an operator-safe summary.",
                    timestamp="09:31",
                    tone="info",
                    privacy_scope="owner_private",
                ),
            ],
            selected_key="thread-1",
            transcript=[
                MessageTranscriptItem(
                    "Consumer",
                    "Can you check whether this is ready?",
                    timestamp="09:41",
                    provider="Chat",
                    attachments=[
                        MessageAttachment(
                            "Example attachment",
                            href="/media/example-asset",
                            media_type="image",
                            detail="public-safe fixture asset",
                            tone="info",
                        )
                    ],
                ),
                MessageTranscriptItem(
                    "Owner",
                    "raw fixture owner private message",
                    timestamp="09:40",
                    direction="outgoing",
                    provider="Direct",
                    privacy_scope="owner_private",
                    safe_alternate="Owner-private reply summarized for operators.",
                ),
            ],
        ),
        activity=ActivitySurfaceConfig(
            enabled=True,
            events=[
                ActivityEvent("Review", "Operator queued a decision", "09:45", "Item moved into review.", "/review", tone="warn"),
                ActivityEvent("Media", "Fixture asset ready", "09:35", "Preview generated for operator inspection.", "/media", tone="good"),
            ],
        ),
        media=MediaSurfaceConfig(
            enabled=True,
            cards=[
                MediaArtifactCard(
                    "Example generated asset",
                    href="/media/example-asset",
                    media_type="image",
                    status="ready",
                    detail="Public-safe fixture media card.",
                    timestamp="09:35",
                    provider="Media",
                    tone="good",
                ),
                MediaArtifactCard(
                    "raw fixture private media title",
                    href="/media/raw-private-fixture",
                    preview_url="/media/raw-private-fixture-preview",
                    media_type="image",
                    status="private",
                    detail="raw fixture private media detail",
                    safe_alternate="Owner-private media summarized for operators.",
                    privacy_scope="owner_private",
                    tone="info",
                ),
            ],
        ),
        features={MESSAGES_FEATURE: True, ACTIVITY_FEATURE: True, MEDIA_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    return render_dashboard_sections(dashboard) + surfaces + hold_form


def render_fixture_page(*, static_base_url: str = "/persona-console/static") -> str:
    return render_shell_html(
        build_fixture_config(static_base_url=static_base_url),
        render_dashboard_fragment(),
        current_path="/",
    )


def create_app():
    try:
        from fastapi import FastAPI
        from fastapi.responses import HTMLResponse
    except ImportError as exc:  # pragma: no cover - only hit without FastAPI.
        raise RuntimeError("Install the PersonaCore FastAPI example dependencies first") from exc

    app = FastAPI(title="PersonaCore Fixture")
    register_static_assets(app)

    @app.get("/", response_class=HTMLResponse)
    def dashboard() -> str:
        return render_fixture_page()

    @app.get("/fragments/dashboard", response_class=HTMLResponse)
    def dashboard_fragment() -> str:
        return render_dashboard_fragment()

    return app


def _default_static_base_for_output(output: Path) -> str:
    static_dir = Path(__file__).resolve().parents[1] / "src" / "persona_console" / "static"
    return os.path.relpath(static_dir, output.resolve().parent)


def main() -> None:
    parser = argparse.ArgumentParser(description="Render the public-safe PersonaCore fixture page.")
    parser.add_argument("--output", type=Path, help="Write HTML to this file instead of stdout.")
    parser.add_argument("--static-base-url", help="Override the static asset base URL.")
    args = parser.parse_args()

    static_base_url = args.static_base_url
    if not static_base_url and args.output:
        static_base_url = _default_static_base_for_output(args.output)
    html = render_fixture_page(static_base_url=static_base_url or "/persona-console/static")

    if args.output:
        args.output.write_text(html, encoding="utf-8")
    else:
        print(html)


if __name__ == "__main__":
    main()
