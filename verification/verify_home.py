from playwright.sync_api import sync_playwright
import time
import os

def run_cuj(page):
    print("Navigating to home page...")
    page.goto("http://localhost:3000")
    page.wait_for_timeout(2000)

    print("Taking homepage screenshot...")
    page.screenshot(path="verification/screenshots/home.png", full_page=True)

    print("Navigating to events page...")
    page.goto("http://localhost:3000/events")
    page.wait_for_timeout(2000)

    print("Taking events screenshot...")
    page.screenshot(path="verification/screenshots/events.png", full_page=True)

    print("Navigating to submit report page...")
    page.goto("http://localhost:3000/submit")
    page.wait_for_timeout(2000)

    print("Filling submit form...")
    page.locator('input[name="submitterName"]').fill("John Doe")
    page.wait_for_timeout(500)
    page.locator('input[name="contactEmail"]').fill("john@example.com")
    page.wait_for_timeout(500)
    page.locator('input[name="title"]').fill("Testing Report Submission")
    page.wait_for_timeout(500)
    page.locator('input[name="activityDate"]').fill("2026-03-15")
    page.wait_for_timeout(500)
    page.locator('textarea[name="summary"]').fill("This is a summary of the activity.")
    page.wait_for_timeout(500)
    page.locator('textarea[name="content"]').fill("This is the full report detailing everything that happened during the Catholic evangelization activity.")
    page.wait_for_timeout(500)

    page.locator('input[type="checkbox"]').check()
    page.wait_for_timeout(500)

    print("Submitting form...")
    page.get_by_role("button", name="Submit Report").click()
    page.wait_for_timeout(3000)

    print("Taking success screenshot...")
    page.screenshot(path="verification/screenshots/submit_success.png")
    page.wait_for_timeout(2000)

if __name__ == "__main__":
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            record_video_dir="verification/videos",
            viewport={'width': 1280, 'height': 800}
        )
        page = context.new_page()
        try:
            run_cuj(page)
        finally:
            context.close()
            browser.close()
