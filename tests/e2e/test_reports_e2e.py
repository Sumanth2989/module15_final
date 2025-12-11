import pytest
from playwright.sync_api import Page, expect
import time

BASE_URL = "http://localhost:8000"


def test_visit_report(page: Page):
    TEST_USERNAME = "testuser@example.com"
    TEST_PASSWORD = "password123"

    # login with seeded user
    page.goto(f"{BASE_URL}/login")
    page.fill("input[name='username']", TEST_USERNAME)
    page.fill("input[name='password']", TEST_PASSWORD)
    page.press("input[name='password']", "Enter")
    time.sleep(1)

    # go to report page
    page.goto(f"{BASE_URL}/calculations/report")
    expect(page.locator("body")).to_contain_text("Calculations Report")
