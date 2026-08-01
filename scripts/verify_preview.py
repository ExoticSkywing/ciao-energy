from pathlib import Path
from playwright.sync_api import sync_playwright

out = Path("docs/evidence")
out.mkdir(parents=True, exist_ok=True)

with sync_playwright() as playwright:
    browser = playwright.chromium.launch(headless=True, args=["--disable-dev-shm-usage"])
    for name, width, height in [("desktop", 1536, 864), ("mobile", 390, 844)]:
        page = browser.new_page(viewport={"width": width, "height": height})
        console_errors: list[str] = []
        page.on("console", lambda message: console_errors.append(f"console:{message.type}:{message.text}") if message.type == "error" else None)
        page.on("pageerror", lambda error: console_errors.append(f"pageerror:{error}"))
        page.goto("http://172.17.0.1:3005/", wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(2500)
        response = page.reload(wait_until="networkidle", timeout=60000)
        page.wait_for_timeout(800)
        page.screenshot(path=str(out / f"{name}-hero.png"), full_page=False)
        can_count = page.locator(".hero .fallback-can").count()
        can_boxes = []
        for index in range(can_count):
            can_boxes.append(page.locator(".hero .fallback-can").nth(index).bounding_box())
        right_arrow = page.locator("button[aria-label='Goût suivant']")
        right_arrow_box = right_arrow.bounding_box() if right_arrow.count() else None
        menu = page.locator(".menu-button")
        if menu.count():
            menu.click()
            page.wait_for_timeout(350)
            menu_open = page.locator(".menu-panel.open").count() == 1
            menu.click()
        else:
            menu_open = False
        page.locator("button[aria-label='Coco Citron Vert']").click()
        page.wait_for_timeout(250)
        flavor_text = page.locator(".hero h1").inner_text().replace("\n", " ")
        flavor_switched = "Coco" in flavor_text and "Citron Vert" in flavor_text
        page.locator("#FAQ").scroll_into_view_if_needed()
        faq_button = page.locator(".faq-item > button").first
        faq_button.click()
        page.wait_for_timeout(350)
        faq_open = page.locator(".faq-item.open").count() == 1
        page.locator("#newsletter").scroll_into_view_if_needed()
        page.locator("#newsletter input[type='email']").fill("test@example.com")
        page.locator("#newsletter form button").click()
        page.wait_for_timeout(250)
        status_text = page.locator("#newsletter [role='status']").inner_text()
        print({
            "viewport": name,
            "http": response.status if response else None,
            "hero_can_count": can_count,
            "hero_can_boxes": can_boxes,
            "right_arrow_box": right_arrow_box,
            "menu_open": menu_open,
            "flavor_switched": flavor_switched,
            "faq_open": faq_open,
            "newsletter_status": status_text,
            "console_errors": console_errors,
        }, flush=True)
        page.close()
    browser.close()
