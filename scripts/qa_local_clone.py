from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from playwright.async_api import async_playwright


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://172.17.0.1:44118/")
    parser.add_argument("--chromium", required=True)
    parser.add_argument("--out", default="docs/evidence/exact-clone-desktop.png")
    args = parser.parse_args()

    console_errors: list[str] = []
    page_errors: list[str] = []
    failed_requests: list[str] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=args.chromium,
            headless=True,
            args=["--no-sandbox", "--disable-dev-shm-usage"],
        )
        page = await browser.new_page(viewport={"width": 1440, "height": 900})
        page.on(
            "console",
            lambda message: console_errors.append(message.text)
            if message.type == "error"
            else None,
        )
        page.on("pageerror", lambda error: page_errors.append(str(error)))
        page.on(
            "requestfailed",
            lambda request: failed_requests.append(
                f"{request.url} :: {request.failure or 'failed'}"
            ),
        )
        await page.goto(args.url, wait_until="domcontentloaded", timeout=120_000)
        await page.wait_for_timeout(18_000)

        data = await page.evaluate(
            """
            () => {
              const frame = document.querySelector('iframe');
              const doc = frame?.contentDocument;
              const win = frame?.contentWindow;
              return {
                topUrl: location.href,
                iframe: frame ? frame.getBoundingClientRect().toJSON() : null,
                frameUrl: win?.location.href || null,
                readyState: doc?.readyState || null,
                title: doc?.title || null,
                canvasCount: doc?.querySelectorAll('canvas').length || 0,
                canvasRect: doc?.querySelector('canvas')?.getBoundingClientRect().toJSON() || null,
                gsap: typeof win?.gsap,
                scrollTrigger: typeof win?.ScrollTrigger,
                splitText: typeof win?.SplitText,
                gsapBooted: Boolean(win?.__gsapBooted),
                lenis: Boolean(win?.lenis),
                loaderDisplay: doc?.querySelector('.loader')
                  ? getComputedStyle(doc.querySelector('.loader')).display
                  : null,
                scrollHeight: doc?.documentElement.scrollHeight || 0,
                bodyText: doc?.body?.innerText?.slice(0, 300) || ''
              };
            }
            """
        )

        out = Path(args.out)
        out.parent.mkdir(parents=True, exist_ok=True)
        await page.screenshot(path=str(out), full_page=False)
        report = {
            "data": data,
            "console_errors": console_errors,
            "page_errors": page_errors,
            "failed_requests": failed_requests,
            "screenshot": str(out),
        }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
