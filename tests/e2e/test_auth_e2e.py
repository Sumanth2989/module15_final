import uuid


BASE_URL = "http://127.0.0.1:8000"


def make_unique_email() -> str:
    return f"e2e_{uuid.uuid4().hex[:8]}@example.com"


def test_register_positive(page):
    email = make_unique_email()
    page.goto(f"{BASE_URL}/static/register.html")

    page.fill("#email", email)
    page.fill("#password", "secret123")
    page.fill("#confirm", "secret123")
    page.click("button[type=submit]")

    page.wait_for_timeout(500)

    text = page.text_content("#message") or ""
    assert "Registration successful" in text


def test_register_short_password_negative(page):
    email = make_unique_email()
    page.goto(f"{BASE_URL}/static/register.html")

    page.fill("#email", email)
    page.fill("#password", "123")
    page.fill("#confirm", "123")
    page.click("button[type=submit]")

    page.wait_for_timeout(500)

    text = page.text_content("#message") or ""
    assert "Password must be at least 6" in text


def test_login_positive(page):
    email = make_unique_email()

    # first register
    page.goto(f"{BASE_URL}/static/register.html")
    page.fill("#email", email)
    page.fill("#password", "secret123")
    page.fill("#confirm", "secret123")
    page.click("button[type=submit]")
    page.wait_for_timeout(500)

    # then login
    page.goto(f"{BASE_URL}/static/login.html")
    page.fill("#email", email)
    page.fill("#password", "secret123")
    page.click("button[type=submit]")

    page.wait_for_timeout(500)
    text = page.text_content("#message") or ""
    assert "Login successful" in text


def test_login_wrong_password_negative(page):
    email = make_unique_email()

    # register once
    page.goto(f"{BASE_URL}/static/register.html")
    page.fill("#email", email)
    page.fill("#password", "secret123")
    page.fill("#confirm", "secret123")
    page.click("button[type=submit]")
    page.wait_for_timeout(500)

    # try wrong password
    page.goto(f"{BASE_URL}/static/login.html")
    page.fill("#email", email)
    page.fill("#password", "wrongpass")
    page.click("button[type=submit]")

    page.wait_for_timeout(500)
    text = page.text_content("#message") or ""
    assert "Invalid credentials" in text
