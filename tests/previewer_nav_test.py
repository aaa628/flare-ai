"""Regression test: in-app navigation must survive hosted HTML previewers.

Previewers (htmlpreview, githack-style viewers, some IDE panes) serve index.html from one
origin and inject <base href="https://raw...../site/">. A plain href="#/explorer" then resolves
against the BASE, so the click navigates away to the raw file (shown as unstyled text).

This test simulates that: the page is served from http://previewer.test/view with a <base> tag
pointing at http://raw.test/site/, where index.html is served as text/plain (like raw.githubusercontent.com)
and assets get proper MIME types. Needs: pip install playwright && playwright install chromium

Run: python tests/previewer_nav_test.py
"""
import asyncio
import mimetypes
import pathlib
import re
import sys

from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE_DIR = ROOT / "site"
RAW = "http://raw.test/site/"
PAGE = "http://previewer.test/view"
results = []


def check(name, cond, extra=""):
    results.append(bool(cond))
    print(("PASS " if cond else "FAIL ") + name, extra)


async def txt(pg, sel):
    """inner text or '' (never raises): a missing element is a failed check, not a crash."""
    try:
        return await pg.locator(sel).first.inner_text(timeout=1500)
    except Exception:
        return ""


def page_html():
    html = (SITE_DIR / "index.html").read_text(encoding="utf-8")
    # accept both relative assets and absolute raw.githubusercontent assets: map them onto RAW
    html = re.sub(r"https://raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/site/", "", html)
    return html.replace("<head>", f'<head><base href="{RAW}">', 1)


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={"width": 1280, "height": 900})
        pg = await ctx.new_page()
        errors = []
        pg.on("pageerror", lambda e: errors.append(str(e)))

        async def previewer(route):
            await route.fulfill(status=200, content_type="text/html; charset=utf-8", body=page_html())

        async def raw(route):
            rel = route.request.url[len(RAW):].split("?")[0].split("#")[0] or "index.html"
            f = SITE_DIR / rel
            if not f.is_file():
                return await route.fulfill(status=404, body="not found")
            if rel == "index.html":  # raw hosts show HTML as plain text
                return await route.fulfill(status=200, content_type="text/plain; charset=utf-8", body=f.read_text(encoding="utf-8"))
            ctype = mimetypes.guess_type(str(f))[0] or "text/plain"
            await route.fulfill(status=200, content_type=ctype, body=f.read_bytes())

        await pg.route("http://previewer.test/**", previewer)
        await pg.route("http://raw.test/**", raw)

        async def start(q=""):
            await pg.goto(PAGE + q)
            await pg.wait_for_selector("h1")

        await start()
        check("page renders with CSS (accent button colour applied)",
              await pg.evaluate("getComputedStyle(document.querySelector('.btn')).backgroundColor") != "rgba(0, 0, 0, 0)")

        await pg.click("text=Open Flame Explorer")
        await pg.wait_for_timeout(300)
        check("'Open Flame Explorer' stays on the previewer page", pg.url.startswith(PAGE), pg.url)
        check("'Open Flame Explorer' shows the Explorer view", "Flame Explorer" in await txt(pg, "h1"))

        await start()
        await pg.click("text=How we handle evidence")
        await pg.wait_for_timeout(300)
        check("'How we handle evidence' stays on the previewer page", pg.url.startswith(PAGE), pg.url)
        check("'How we handle evidence' shows About", "About Flare AI" in await txt(pg, "h1"))

        # nav links, brand link, back link, and a test row link
        await start()
        await pg.click("#nav a[data-route=explorer]")
        await pg.wait_for_timeout(200)
        check("nav 'Flame Explorer' works", pg.url.startswith(PAGE) and "Flame Explorer" in await txt(pg, "h1"), pg.url)
        await pg.click("a.brand")
        await pg.wait_for_timeout(200)
        check("brand link returns to Overview", pg.url.startswith(PAGE) and "NASA" in await txt(pg, "h1"), pg.url)

        # preview mode toggle (JS-built URLs must not resolve against <base>)
        await start()
        await pg.click("text=Team preview: show unchecked rows")
        await pg.wait_for_selector(".chart")
        check("preview toggle stays on previewer origin", pg.url.startswith("http://previewer.test/"), pg.url)
        check("preview banner visible after toggle", await pg.is_visible("#preview-banner"))
        await pg.click("a:has-text('Flame Explorer') >> nth=0")  # nav
        await pg.wait_for_selector("tbody tr.row")
        await pg.click("tbody tr.row td.id a >> nth=0")
        await pg.wait_for_selector(".cols")
        check("test row link opens detail on previewer", pg.url.startswith("http://previewer.test/") and "#/experiment/" in pg.url, pg.url)
        await pg.click("text=Exit preview")
        await pg.wait_for_timeout(400)
        check("exit preview stays on previewer origin", pg.url.startswith("http://previewer.test/"), pg.url)
        check("exit preview hides banner", await pg.is_hidden("#preview-banner"))

        # skip link must not break routing
        await start()
        await pg.focus(".skip")
        await pg.keyboard.press("Enter")
        await pg.wait_for_timeout(200)
        check("skip link keeps us on the page and view intact", pg.url.startswith(PAGE) and await pg.locator("h1").count() > 0, pg.url)

        check("no JS errors", not errors, str(errors))
        await b.close()


asyncio.run(main())
print(f"\n{sum(results)} / {len(results)} checks passed")
sys.exit(0 if all(results) else 1)
