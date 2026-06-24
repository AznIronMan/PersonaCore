# Configuration Model

PersonaCore should use configuration to make one distro fit many runtimes.
Configuration should be explicit, typed where practical, and safe to expose in
public examples.

## Layers

- `PersonaCoreConfig` or the current compatibility `PersonaConsoleConfig`:
  shell-level configuration for brand label, page title, nav, badges, status
  pills, user pill, theme, static paths, live refresh, and layout width.
- Feature settings: runtime-level switches that decide which shared modules are
  mounted or rendered.
- Capability flags: facts about what the runtime can do, such as whether it has
  conversations, media, review queues, workers, scheduling, or external adapter
  health.
- Feature-specific settings: opt-in module configuration such as token health
  checks, labels, required/optional state, and runtime-owned data lookups.
- Data providers: runtime-owned callables or routes that supply rows, counts,
  summaries, and partial refresh fragments to shared render primitives.

## Public Example Shape

```python
from persona_console import NavGroup, NavItem, PersonaConsoleConfig

config = PersonaConsoleConfig(
    brand_name="Example Persona",
    page_title="Dashboard",
    page_subtitle="Runtime overview",
    active="dashboard",
    nav_groups=[
        NavGroup(
            "Core",
            [
                NavItem("Dashboard", "/", active="dashboard"),
                NavItem("Messages", "/messages", active="messages"),
            ],
        ),
        NavGroup(
            "Review",
            [
                NavItem("Queue", "/review", active="review", badge="review"),
            ],
        ),
    ],
    nav_badges={"review": 3},
)
```

Public examples must remain generic. Private consumers can inject private
labels, paths, and data at runtime from their own repositories.

As the public API moves to PersonaCore naming, examples should prefer:

```python
from personacore import NavGroup, NavItem, PersonaCoreConfig
```

The older `persona_console` path should remain available as a compatibility
alias during the v1.x transition.

## Format Recommendation

Use typed Python dataclasses and plain dictionaries as the primary runtime
configuration model. They are fast, dependency-light, easy to construct from
consumer code, and compatible with all current Python runtime styles.

Support optional JSON loading through the standard library for deployments that
want declarative files. Avoid mandatory YAML, Pydantic, or other heavy
configuration dependencies in the core import path. If richer validation is
needed later, keep it optional.

## Feature Flag Direction

Future shared configuration should make common feature modules selectable:

```python
features = {
    "dashboard": True,
    "messages": True,
    "media": False,
    "review": True,
    "workers": False,
    "scheduling": False,
}
```

Feature flags should hide navigation and UI modules by default when disabled.
They should not import optional dependencies or private adapters unless the
feature is enabled and the consumer provides the integration.

## Token Health

Token health is a shared, opt-in feature. PersonaCore should not read private
`.env` files or runtime databases on its own. A consuming runtime enables the
feature, names the checks it wants to expose, and passes a settings/env mapping
or lookup callable into the redacted report builder.

```python
from personacore import TokenHealthCheck, TokenHealthConfig, build_token_health_report

token_health = TokenHealthConfig(
    enabled=True,
    checks=[
        TokenHealthCheck(
            "social_api",
            "Social API token",
            "Social",
            ["SOCIAL_API_TOKEN"],
            required=True,
        ),
        TokenHealthCheck(
            "webhook_verify",
            "Webhook verify token",
            "Webhooks",
            ["WEBHOOK_VERIFY_TOKEN"],
            required=False,
        ),
    ],
)

report = build_token_health_report(token_health, values=runtime_settings)
```

The returned report is safe to render or expose through an admin health route:
raw values are never copied into the report. Consumers may hide secret key names
with `TokenHealthConfig(show_secret_names=False)` when even source names should
stay runtime-local.

## Extension Rules

- Prefer adding a generic capability or data provider over adding
  persona-specific branching.
- Keep render helpers tolerant of missing optional data.
- Keep runtime-owned mutation endpoints in the consumer app unless the mutation
  is truly generic.
- Keep secret-bearing and deployment-specific behavior out of PersonaCore.
