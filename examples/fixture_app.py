from __future__ import annotations

import argparse
import os
from pathlib import Path

from personacore import (
    ACTIVITY_FEATURE,
    MEDIA_FEATURE,
    MESSAGES_FEATURE,
    PEOPLE_FEATURE,
    REVIEW_FEATURE,
    ActivityEvent,
    ActivitySurfaceConfig,
    AdminPrivacyContext,
    DashboardAction,
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
    PeopleSurfaceConfig,
    PersonListRow,
    PersonRelationshipSummary,
    PersonTag,
    PersonaCoreConfig,
    ReviewAgendaItem,
    ReviewBoardRow,
    ReviewQueueCard,
    ReviewQueueSection,
    ReviewSurfaceConfig,
    StatusTab,
    StatusPill,
    SurfaceBadge,
    ThemeTokens,
    TokenHealthCheck,
    TokenHealthConfig,
    UserPill,
    register_static_assets,
    render_dashboard_sections,
    render_people_surface,
    render_review_surface,
    render_shell_html,
    render_status_tabs,
    render_surface_sections,
)

TASKS_FEATURE = "tasks"
WORKERS_FEATURE = "workers"
LOGS_FEATURE = "logs"
SETTINGS_FEATURE = "settings"


def build_fixture_config(*, static_base_url: str = "/persona-console/static") -> PersonaCoreConfig:
    return PersonaCoreConfig(
        brand_name="Example Persona",
        page_title="Admin Overview",
        page_subtitle="Reference-style shared admin workspace",
        active="dashboard",
        features={
            MESSAGES_FEATURE: True,
            ACTIVITY_FEATURE: True,
            MEDIA_FEATURE: True,
            PEOPLE_FEATURE: True,
            REVIEW_FEATURE: True,
            TASKS_FEATURE: True,
            WORKERS_FEATURE: True,
            LOGS_FEATURE: True,
            SETTINGS_FEATURE: True,
        },
        nav_groups=[
            NavGroup(
                "Overview",
                [
                    NavItem("Overview", "/", active="dashboard"),
                    NavItem("Activity", "/activity", active="activity", feature=ACTIVITY_FEATURE),
                ],
                key="overview",
            ),
            NavGroup(
                "Conversations",
                [
                    NavItem("Messages", "/messages", active="messages", badge="messages", feature=MESSAGES_FEATURE),
                    NavItem("People", "/people", active="people", badge="people", feature=PEOPLE_FEATURE),
                    NavItem("Media", "/media", active="media", badge="media", feature=MEDIA_FEATURE),
                ],
                key="conversations",
            ),
            NavGroup(
                "Operations",
                [
                    NavItem("Review Queue", "/review", active="review", badge="review"),
                    NavItem("Tasks", "/tasks", active="tasks", badge="tasks", feature=TASKS_FEATURE),
                    NavItem("Workers", "/workers", active="workers", badge="workers", feature=WORKERS_FEATURE),
                ],
                key="operations",
            ),
            NavGroup(
                "System",
                [
                    NavItem("Logs", "/logs", active="logs", badge="logs", feature=LOGS_FEATURE),
                    NavItem("Settings", "/settings", active="settings", feature=SETTINGS_FEATURE),
                    NavItem("Health", "/health", active="health"),
                ],
                key="system",
            ),
        ],
        nav_badges={"messages": 12, "people": 3, "media": 9, "review": 4, "tasks": 6, "workers": 1, "logs": 2},
        status_pills=[
            StatusPill("Runtime active", "good"),
            StatusPill("Admin active", "good"),
            StatusPill("Review 4", "info"),
            StatusPill("Worker lag", "warn"),
        ],
        user=UserPill(
            display_name="Operator",
            username="operator",
            tier="admin",
            source="fixture",
        ),
        app_version="v1.0.15-fixture",
        static_base_url=static_base_url,
        theme=ThemeTokens(
            accent="rgb(239 71 111)",
            accent_soft="rgb(251 113 133)",
            accent_surface="rgb(80 25 40 / 0.38)",
            background="rgb(8 9 11)",
            surface="rgb(18 20 22)",
            surface_raised="rgb(24 26 28 / 0.98)",
            surface_muted="rgb(31 36 39 / 0.74)",
            border="rgb(64 70 74)",
            muted="rgb(156 163 175)",
            info="rgb(45 212 191)",
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
            title="Operator Attention",
            subtitle="Shared first-screen rhythm for a generic persona runtime",
            label="Needs operator pass",
            tone="warn",
            count=4,
            refreshed_label="refreshed just now",
            items=[
                DashboardAttentionItem("Review", 4, "Items waiting for operator review.", "/review", tone="warn"),
                DashboardAttentionItem("Credentials", 1, "One optional webhook credential is missing.", "/health", tone="info"),
                DashboardAttentionItem("Workers", "42s", "Queue latency is above target.", "/workers", tone="bad"),
                DashboardAttentionItem("Messages", 12, "Unread conversations need triage.", "/messages", tone="warn"),
            ],
        ),
        filters=[
            DashboardFilter("All", "/", active=True, color="rgb(251 113 133)"),
            DashboardFilter("Messages", "/?surface=messages", key="messages", color="rgb(45 212 191)"),
            DashboardFilter("People", "/?surface=people", key="people", color="rgb(251 191 36)"),
            DashboardFilter("Media", "/?surface=media", key="media", color="rgb(129 140 248)"),
            DashboardFilter("Tasks", "/?surface=tasks", key="tasks", color="rgb(52 211 153)"),
            DashboardFilter("System", "/?surface=system", key="system", color="rgb(248 113 113)"),
        ],
        metrics=[
            DashboardMetric("Services", "6/6", "/health", "Admin, runtime, workers, storage", tone="good"),
            DashboardMetric("Messages", 128, "/messages", "Across active channels", tone="info"),
            DashboardMetric("People", 37, "/people", "Profiles with recent activity"),
            DashboardMetric("Open reviews", 4, "/review", "Needs operator pass", tone="warn"),
            DashboardMetric("Worker latency", "42s", "/workers", "P95 over last hour", tone="bad"),
            DashboardMetric("Artifacts", 9, "/media", "Queued or ready"),
        ],
        routes=[
            DashboardRouteCard("Messages", "/messages", "Scan conversations, summaries, and handoffs.", metric=12, tone="warn"),
            DashboardRouteCard("People", "/people", "Review profiles, notes, and visibility labels.", metric=37, tone="info"),
            DashboardRouteCard("Review Queue", "/review", "Approve, hold, or dismiss items.", metric=4, tone="warn"),
            DashboardRouteCard("Media", "/media", "Track artifacts, previews, and publishing status.", metric=9),
            DashboardRouteCard("Tasks", "/tasks", "Follow queued work and operator-owned next actions.", metric=6),
            DashboardRouteCard("Logs", "/logs", "Read sanitized runtime events and warnings.", metric=2, tone="info"),
            DashboardRouteCard("Settings", "/settings", "Adjust feature flags and integration posture.", metric="on"),
            DashboardRouteCard("Workers", "/workers", "Inspect queue health and retries.", metric="42s", tone="bad"),
        ],
        health=DashboardHealthStrip(
            "Runtime health",
            "/health",
            tone="good",
            meta="fixture runtime sampled just now",
            metrics=[
                DashboardHealthMetric("Runtime", "ok", "request path reachable", tone="good"),
                DashboardHealthMetric("Admin", "ok", "shell and assets loaded", tone="good"),
                DashboardHealthMetric("Workers", "lag", "one queue above target", tone="warn"),
                DashboardHealthMetric("Storage", "ok", "artifact index reachable", tone="good"),
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
            DashboardAdapterCard(
                "Social",
                "healthy",
                "/activity",
                tone="good",
                route="public engagement",
                policy="comments and likes visible by normal scope",
                last_in="5m ago",
                last_out="7m ago",
                counts=["41 events/24h", "0 failed"],
                detail="Public and group activity stays in the normal operator surface.",
            ),
        ],
        flow=DashboardFlow(
            "Conversation Flow",
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
            DashboardQueueRow("Held", 3, "/pending?status=held", tone="info"),
            DashboardQueueRow("Applied", 22, "/pending?status=applied", tone="good"),
            DashboardQueueRow("Failed", 1, "/pending?status=failed", tone="bad"),
            DashboardQueueRow("Cancelled", 2, "/pending?status=cancelled"),
        ],
        activity=[
            DashboardActivityItem("Review", "Four items queued", "/review", "09:42", "Waiting for operator pass.", tone="warn"),
            DashboardActivityItem("Messages", "Conversation summary refreshed", "/messages", "09:38", "Active channel state updated.", tone="info"),
            DashboardActivityItem("People", "Profile snapshot refreshed", "/people", "09:34", "Recent people notes rebuilt with privacy guards.", tone="good"),
            DashboardActivityItem("Workers", "Latency warning", "/workers", "09:31", "One worker is above target.", tone="bad"),
            DashboardActivityItem("Media", "Assets ready", "/media", "09:26", "Three generated assets are ready for inspection.", tone="good"),
        ],
    )
    people_surface = render_people_surface(
        PeopleSurfaceConfig(
            enabled=True,
            title="People",
            subtitle="Canonical people records with shared privacy-aware summaries.",
            search_action="/people",
            rows=[
                PersonListRow(
                    key="example-consumer",
                    label="Example Consumer",
                    href="/people/example-consumer",
                    subtitle='id 301 - "consumer"',
                    external_id="CN0001",
                    trust_label="internal",
                    trust_tone="info",
                    linked_users=4,
                    tags=[
                        PersonTag("Supportive", tone="good"),
                        PersonTag("Warm", tone="info"),
                        PersonTag("Needs review", tone="warn"),
                    ],
                    relationship=PersonRelationshipSummary(
                        label="Persona",
                        score="+54",
                        tone="good",
                        score_percent=78,
                        lanes=[PersonTag("trusted", tone="info"), PersonTag("familiar", tone="good")],
                        labels=[PersonTag("friend", tone="info"), PersonTag("review", tone="warn")],
                    ),
                    notes="Reads as calm and cooperative; the current handoff is clear enough for operator review.",
                    updated="1h ago",
                ),
                PersonListRow(
                    key="example-owner-private",
                    label="Owner-Private Profile",
                    href="/people/example-owner-private",
                    subtitle='id 346 - "owner lane"',
                    external_id="INT-OWNER",
                    trust_label="owner-private",
                    trust_tone="warn",
                    linked_users=1,
                    tags=[
                        PersonTag("Protected", tone="warn"),
                        PersonTag("Direct", tone="info"),
                    ],
                    relationship=PersonRelationshipSummary(
                        label="Persona",
                        score="+45",
                        tone="good",
                        score_percent=72,
                        lanes=[PersonTag("trusted", tone="info")],
                        labels=[PersonTag("private", tone="warn")],
                    ),
                    notes="raw fixture private people note",
                    notes_safe_alternate="Owner-private notes are summarized for operators.",
                    notes_privacy_scope="owner_private",
                    updated="2h ago",
                ),
            ],
            new_person_html='<p class="hint">Consumer runtimes own the actual create form and authorization.</p>',
        ),
        features={PEOPLE_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    review_tabs = render_status_tabs(
        [
            StatusTab("All", "/review", 8, active=True),
            StatusTab("Pending", "/review?status=pending", 4, tone="warn"),
            StatusTab("Ready", "/review?status=ready", 3, tone="good"),
            StatusTab("Failed", "/review?status=failed", 1, tone="bad"),
        ],
        aria_label="Review status",
    )
    review_surface = review_tabs + render_review_surface(
        ReviewSurfaceConfig(
            enabled=True,
            title="Review",
            subtitle="Operator-gated decisions and publishing queues.",
            filters=[
                DashboardFilter("All", "/review", key="8", active=True),
                DashboardFilter("Media", "/review?kind=media", key="1"),
                DashboardFilter("Messages", "/review?kind=message", key="2"),
            ],
            metrics=[
                DashboardMetric("Pending", 4, "/review?status=pending", "needs operator pass", tone="warn"),
                DashboardMetric("Failed", 1, "/review?status=failed", "retry needed", tone="bad"),
                DashboardMetric("Ready", 3, "/review?status=ready", "safe to inspect", tone="good"),
            ],
            actions=[
                DashboardAction("Persona proposals", "/persona/proposals", tone="info"),
                DashboardAction("Media review", "/review/media", tone="warn"),
            ],
            rows=[
                ReviewBoardRow(
                    "proposal",
                    "pending",
                    "persona:voice",
                    "Review proposed tone adjustment before applying.",
                    "/persona/proposals/1",
                    risk="warn",
                    actor="operator",
                    age="12m",
                    badges=[SurfaceBadge("diff", "info")],
                ),
                ReviewBoardRow(
                    "message",
                    "held",
                    "messages:owner-private",
                    "raw fixture private review summary",
                    "/messages/raw-private-review",
                    risk="bad",
                    actor="runtime",
                    age="now",
                    summary_safe_alternate="Owner-private review summary withheld for operators.",
                    summary_privacy_scope="owner_private",
                ),
                ReviewBoardRow(
                    "media",
                    "draft",
                    "media:asset-1",
                    "Generated asset is ready for operator inspection.",
                    "/review/media?q=asset-1",
                    risk="warn",
                    actor="media-worker",
                    age="28m",
                ),
            ],
            agenda=[
                ReviewAgendaItem("Persona proposals", 3, "/persona/proposals", "review queue", "Inspect current/proposed values.", "warn"),
                ReviewAgendaItem("Reflection", 12, "/review/reflection", "mind output", "Classify and link reflection notes.", "good"),
                ReviewAgendaItem("Media", 1, "/review/media", "draft assets", "Review generated artifacts.", "warn"),
                ReviewAgendaItem("Voice", 2, "/creation/voice", "audio clips", "Inspect queued clips.", "info"),
            ],
            queue_sections=[
                ReviewQueueSection(
                    "Publishing Queues",
                    "safe summaries",
                    cards=[
                        ReviewQueueCard(
                            "Example social draft",
                            status="draft",
                            href="/review/social?q=post-1",
                            category="social",
                            summary="Caption is ready for operator review.",
                            meta=[("Key", "post-1"), ("Source", "operator")],
                            tone="warn",
                        ),
                        ReviewQueueCard(
                            "Owner-private queue",
                            status="pending",
                            href="/review/private",
                            category="direct",
                            summary="raw fixture private queue summary",
                            summary_safe_alternate="Owner-private queue summarized for operators.",
                            summary_privacy_scope="owner_private",
                            tone="info",
                        ),
                    ],
                )
            ],
        ),
        features={REVIEW_FEATURE: True},
        privacy_policy=privacy_policy,
        privacy_context=operator_context,
    )
    operator_workspace = """
<section class="pc-dashboard-panel pc-reference-workspace">
  <div class="pc-dashboard-panel-head">
    <div>
      <div class="pc-dashboard-section-title">Operator Workspace</div>
      <p class="pc-dashboard-section-meta">Reference module mix for consumer-owned routes and data.</p>
    </div>
    <span class="pc-dashboard-status"><span class="pc-dashboard-status-dot"></span>3 modules</span>
  </div>
  <div class="grid">
    <article class="card">
      <div class="panel-head">
        <h3>Task Queue</h3>
        <span class="pc-dashboard-tag">runtime-owned</span>
      </div>
      <div class="table-wrap">
        <table>
          <thead><tr><th>Task</th><th>Status</th><th>Next action</th></tr></thead>
          <tbody>
            <tr><td>Review pending replies</td><td>Waiting</td><td>Operator decision</td></tr>
            <tr><td>Refresh profile rollups</td><td>Running</td><td>Watch worker latency</td></tr>
            <tr><td>Publish ready artifact</td><td>Held</td><td>Confirm destination</td></tr>
          </tbody>
        </table>
      </div>
    </article>
    <article class="card">
      <div class="panel-head">
        <h3>Log Tail</h3>
        <span class="pc-dashboard-tag">sanitized</span>
      </div>
      <pre>[09:45] review queued for operator
[09:38] conversation summary refreshed
[09:34] owner-private raw fields withheld
[09:31] worker latency warning</pre>
    </article>
    <article class="card">
      <div class="panel-head">
        <h3>Settings Posture</h3>
        <span class="pc-dashboard-tag">feature flags</span>
      </div>
      <div class="pc-token-health-summary">
        <span><strong>on</strong> messages</span>
        <span><strong>on</strong> people</span>
        <span><strong>on</strong> media</span>
        <span><strong>on</strong> owner-private guards</span>
      </div>
      <p class="hint">Mutation routes, restart controls, and secret lookups stay in the consumer runtime.</p>
    </article>
  </div>
</section>
"""
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
            filters=[
                DashboardFilter("All", "/messages", key="12", active=True, color="rgb(251 113 133)"),
                DashboardFilter("Chat", "/messages?platform=chat", key="7", color="rgb(45 212 191)"),
                DashboardFilter("Direct", "/messages?platform=direct", key="5", color="rgb(251 191 36)"),
            ],
            metrics=[
                DashboardMetric("Visible threads", 2, "/messages", "current filters", tone="info"),
                DashboardMetric("Selected messages", 2, "/messages/thread-1", "thread-1"),
                DashboardMetric("Unread", 2, "/messages?unread=1", "needs pass", tone="warn"),
            ],
            actions=[
                DashboardAction("Raw rows", "/messages?view=raw"),
                DashboardAction("Review queue", "/review", tone="warn"),
            ],
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
            conversation_title="Threads",
            transcript_title="Selected conversation",
            transcript_meta="2 visible messages",
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
    return render_dashboard_sections(dashboard) + people_surface + review_surface + surfaces + operator_workspace + hold_form


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
