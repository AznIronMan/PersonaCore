import personaconsole


PRIVATE_HOSTS = ("private-auth.example", "private-static.example")


def _brand() -> personaconsole.BrandAssets:
    return personaconsole.BrandAssets(
        name="Example <Runtime>",
        small_logo_url="/assets/admin-small.svg",
        wordmark_url="/assets/admin-wordmark.svg",
        home_url="/",
    )


def test_admin_login_page_renders_safe_no_js_form_and_escaped_status():
    html = personaconsole.render_admin_login_page(
        personaconsole.AdminLoginPageConfig(
            brand=_brand(),
            title="Admin Login",
            subtitle="Operator session required.",
            form_action="/login",
            next_path="/runtime?tab=overview",
            username_value="operator <one>",
            status_message="<b>Invalid</b>",
            status_tone="bad",
            summary_items=(
                personaconsole.AdminAuthSummaryItem("Session", "required", "info", "Use an operator account."),
            ),
            help_links=(personaconsole.AdminAuthLink("Help", "/help"),),
            legal_links=(personaconsole.AdminAuthLink("Privacy", "/privacy"),),
        )
    )

    assert "pc-admin-login-page" in html
    assert "persona-console.css" in html
    assert "/assets/admin-wordmark.svg" in html
    assert 'method="post" action="/login"' in html
    assert 'name="next" value="/runtime?tab=overview"' in html
    assert 'name="username"' in html
    assert 'name="password" type="password"' in html
    assert "autocomplete=\"current-password\"" in html
    assert "JavaScript is not required for this form." in html
    assert "pc-admin-auth-summary-info" in html
    assert "&lt;b&gt;Invalid&lt;/b&gt;" in html
    assert "operator &lt;one&gt;" in html
    assert "<b>Invalid</b>" not in html
    assert not any(host in html for host in PRIVATE_HOSTS)


def test_admin_login_page_sanitizes_hosted_urls_and_blocked_next_path():
    html = personaconsole.render_admin_login_page(
        {
            "brand": {
                "name": "Example Runtime",
                "small_logo_url": "https://private-auth.example/logo.svg",
                "home_url": "https://private-auth.example/",
            },
            "form_action": "https://private-auth.example/login",
            "next_path": "https://private-auth.example/runtime",
            "static_base_url": "https://private-static.example/persona-console/static",
            "help_links": [{"label": "Unsafe", "href": "https://private-auth.example/help"}],
        }
    )
    blocked = personaconsole.render_admin_login_page(
        personaconsole.AdminLoginPageConfig(next_path="/login/password-change?next=/runtime")
    )

    assert 'action="/login"' in html
    assert 'name="next" value="/"' in html
    assert '/persona-console/static/persona-console.css' in html
    assert "pc-admin-auth-logo-fallback" in html
    assert "Unsafe" not in html
    assert 'name="next" value="/"' in blocked
    assert not any(host in html for host in PRIVATE_HOSTS)


def test_admin_password_change_page_renders_disabled_state_and_min_length():
    html = personaconsole.render_admin_password_change_page(
        personaconsole.AdminPasswordChangePageConfig(
            brand=_brand(),
            subject_label="Operator <One>",
            subtitle="Operator <One> needs a new password.",
            next_path="/runtime",
            min_length=8,
            disabled=True,
            status_message="This password-change session expired.",
            summary_items=(
                {"label": "Challenge", "value": "expired", "tone": "warn", "detail": "Sign in again."},
            ),
        )
    )

    assert "pc-admin-password-change-page" in html
    assert 'action="/login/password-change"' in html
    assert 'name="next" value="/runtime"' in html
    assert 'name="new_password" type="password"' in html
    assert 'name="confirm_password" type="password"' in html
    assert 'minlength="8"' in html
    assert " disabled" in html
    assert "pc-admin-auth-summary-warn" in html
    assert "Operator &lt;One&gt; needs a new password." in html
    assert "This password-change session expired." in html
    assert not any(host in html for host in PRIVATE_HOSTS)
