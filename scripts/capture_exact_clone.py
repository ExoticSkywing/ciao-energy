from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import mimetypes
import os
import re
from pathlib import Path
from urllib.parse import urlsplit

from playwright.async_api import async_playwright

BLOCKED_HOSTS = {
    "cloud.umami.is",
    "www.google.com",
    "www.gstatic.com",
}
BLOCKED_URL_PARTS = (
    "sibforms.com/serve/",
    "recaptcha",
    "umami.is/api/",
)
TEXT_TYPES = {
    "text/css",
    "text/javascript",
    "application/javascript",
    "application/json",
    "application/manifest+json",
    "image/svg+xml",
    "text/html",
}


def local_path_for(url: str) -> str:
    parsed = urlsplit(url)
    path = parsed.path or "/index.html"
    if path.endswith("/"):
        path += "index.html"
    if parsed.query:
        stem, ext = os.path.splitext(path)
        digest = hashlib.sha1(parsed.query.encode()).hexdigest()[:10]
        path = f"{stem}__q_{digest}{ext}"
    return f"vendor/{parsed.netloc}{path}"


def should_keep(url: str) -> bool:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"}:
        return False
    if parsed.netloc in BLOCKED_HOSTS:
        return False
    return not any(part in url for part in BLOCKED_URL_PARTS)


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="https://www.ciaoenergy.com/")
    parser.add_argument("--out", required=True)
    parser.add_argument("--chromium", required=True)
    args = parser.parse_args()

    out = Path(args.out).resolve()
    out.mkdir(parents=True, exist_ok=True)
    seen: dict[str, dict] = {}

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            executable_path=args.chromium,
            args=["--disable-dev-shm-usage"],
        )
        context = await browser.new_context(viewport={"width": 1440, "height": 900}, device_scale_factor=1)
        page = await context.new_page()

        def remember(response):
            url = response.url
            if should_keep(url):
                seen[url] = {
                    "url": url,
                    "status": response.status,
                    "resource_type": response.request.resource_type,
                    "content_type": response.headers.get("content-type", "").split(";", 1)[0],
                }

        async def save_response(response):
            remember(response)
            url = response.url
            if not should_keep(url) or response.status >= 400:
                return
            try:
                body = await response.body()
                rel = local_path_for(url)
                dest = out / rel
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.write_bytes(body)
                seen[url].update({"saved": True, "local": rel, "bytes": len(body)})
            except Exception as exc:
                seen[url].update({"saved": False, "error": str(exc)})

        pending = set()

        def on_response(response):
            task = asyncio.create_task(save_response(response))
            pending.add(task)
            task.add_done_callback(pending.discard)

        page.on("response", on_response)
        await page.goto(args.url, wait_until="domcontentloaded", timeout=120_000)
        await page.wait_for_timeout(8_000)
        total = await page.evaluate("document.documentElement.scrollHeight")
        for y in range(0, total + 1, 700):
            await page.evaluate("y => window.scrollTo(0, y)", y)
            await page.wait_for_timeout(80)
        await page.evaluate("window.scrollTo(0, 0)")
        await page.wait_for_timeout(3_000)

        # Capture exact reference screenshots after the loader is complete.
        await page.screenshot(path=str(out.parent / "original-desktop-1440x900.png"), full_page=False)
        if pending:
            await asyncio.gather(*list(pending), return_exceptions=True)
        manifest = list(seen.values())

        await browser.close()

    # Base HTML is fetched separately to guarantee the current deployed bytes.
    import urllib.request
    req = urllib.request.Request(args.url, headers={"User-Agent": "Mozilla/5.0"})
    html = urllib.request.urlopen(req, timeout=90).read().decode("utf-8")

    # Remove analytics and active third-party submission scripts. Keep the form DOM/style.
    html = re.sub(r'<script[^>]+cloud\.umami\.is/script\.js[^>]*></script>', '', html, flags=re.I)
    html = re.sub(r'<script[^>]+sibforms\.com/forms/end-form/build/main\.js[^>]*></script>', '', html, flags=re.I)
    html = re.sub(r'<script>\s*\(function \(\) \{\s*var loaded = false;.*?</script>', '', html, flags=re.I | re.S)
    html = re.sub(r'action="https://13bac9db\.sibforms\.com/serve/[^"]+"', 'action="#newsletter"', html)

    # Rewrite every captured absolute resource URL to its project-local equivalent.
    replacements = {item["url"]: "/" + item["local"] for item in manifest if item.get("saved")}
    # Also normalize URL variants without fragments.
    for url in sorted(replacements, key=len, reverse=True):
        html = html.replace(url, replacements[url])

    # Demo-only form behavior: never send personal data while preserving visible feedback.
    safe_form = r'''
<script>
(function () {
  const form = document.getElementById('sib-form');
  if (!form) return;
  form.addEventListener('submit', function (event) {
    event.preventDefault();
    const success = document.getElementById('success-message');
    const error = document.getElementById('error-message');
    if (error) error.style.display = 'none';
    if (success) {
      success.style.display = 'block';
      success.textContent = "Mode démonstration : aucune donnée n’a été envoyée.";
    }
  });
})();
</script>
'''
    html = html.replace("</body>", safe_form + "</body>")
    (out / "index.html").write_text(html, encoding="utf-8")

    # Rewrite captured text files after the complete URL map is known.
    for item in manifest:
        if not item.get("saved") or item.get("content_type") not in TEXT_TYPES:
            continue
        path = out / item["local"]
        try:
            text = path.read_text(encoding="utf-8")
        except Exception:
            continue
        for url in sorted(replacements, key=len, reverse=True):
            text = text.replace(url, replacements[url])
        path.write_text(text, encoding="utf-8")

    (out.parent / "mirror-manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "captured": len(manifest),
        "saved": sum(1 for x in manifest if x.get("saved")),
        "failed": sum(1 for x in manifest if not x.get("saved")),
        "html_bytes": (out / "index.html").stat().st_size,
        "site": str(out),
    }, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
