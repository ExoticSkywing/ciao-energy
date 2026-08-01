from playwright.sync_api import sync_playwright

URL = "http://45.8.22.65:44118/mirror/index.html?profile-fallback-verify=1"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    page = br...[truncated]