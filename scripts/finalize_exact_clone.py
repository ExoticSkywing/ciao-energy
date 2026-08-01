from __future__ import annotations

import html as html_module
import json
import re
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
SITE = ROOT / "public" / "mirror"
VENDOR = SITE / "vendor"
ROUTES = {
    "": "https://www.ciaoenergy.com/",
    "mentions-legales": "https://www.ciaoenergy.com/mentions-legales",
    "cgu": "https://www.ciaoenergy.com/cgu",
    "politique-de-confidentialite": "https://www.ciaoenergy.com/politique-de-confidentialite",
}
TEXT_SUFFIXES = {".html", ".css", ".js", ".mjs", ".json", ".svg", ".xml", ".txt"}


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    return urllib.request.urlopen(req, timeout=60).read().decode("utf-8")


def local_for_url(url: str) -> str | None:
    parsed = urlsplit(html_module.unescape(url))
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return None
    direct = VENDOR / parsed.netloc / parsed.path.lstrip("/")
    if parsed.path.endswith("/") or direct.is_dir():
        direct = direct / "index.html"
    if direct.is_file():
        return "/" + direct.relative_to(SITE).as_posix()
    parent = direct.parent
    if not parent.exists():
        return None
    stem = direct.stem
    suffix = direct.suffix
    candidates = sorted(parent.glob(f"{stem}__q_*{suffix}"))
    if len(candidates) == 1:
        return "/" + candidates[0].relative_to(SITE).as_posix()
    return None


def rewrite_urls(text: str) -> str:
    urls = sorted(set(re.findall(r'https?://[^\s"\'<>\\)]+', text)), key=len, reverse=True)
    for raw in urls:
        cleaned = raw.rstrip(";,}")
        local = local_for_url(cleaned)
        if local:
            text = text.replace(cleaned, local)
    return text


def sanitize(text: str) -> str:
    text = re.sub(r'<script[^>]+cloud\.umami\.is/script\.js[^>]*></script>', '', text, flags=re.I)
    text = re.sub(r'<script[^>]+sibforms\.com/forms/end-form/build/main\.js[^>]*></script>', '', text, flags=re.I)
    text = re.sub(
        r'<script>\s*\(function \(\) \{\s*var loaded = false;.*?</script>',
        '',
        text,
        flags=re.I | re.S,
    )
    text = re.sub(r'action="https://13bac9db\.sibforms\.com/serve/[^"]+"', 'action="#newsletter"', text)
    demo = r'''
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
    return text.replace("</body>", demo + "</body>")


def main() -> None:
    SITE.mkdir(parents=True, exist_ok=True)
    route_results = []
    for route, url in ROUTES.items():
        html = fetch(url)
        html = sanitize(rewrite_urls(html))
        destination = SITE / ("index.html" if not route else f"{route}/index.html")
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(html, encoding="utf-8")
        route_results.append({"route": "/" + route, "bytes": destination.stat().st_size})

    rewritten = 0
    for path in VENDOR.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            source = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        result = rewrite_urls(source)
        if result != source:
            path.write_text(result, encoding="utf-8")
            rewritten += 1

    manifest = {
        "source": "https://www.ciaoenergy.com",
        "routes": route_results,
        "vendor_files": sum(1 for p in VENDOR.rglob("*") if p.is_file()),
        "rewritten_text_files": rewritten,
        "safety": {
            "analytics_removed": True,
            "newsletter_submission_disabled": True,
            "recaptcha_loader_removed": True,
        },
    }
    (ROOT / "docs" / "mirror-build.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(manifest, ensure_ascii=False))


if __name__ == "__main__":
    main()
