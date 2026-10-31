"""Browser smoke test for the static site (needs: pip install playwright; playwright install chromium).
Run: python tests/site_smoke_test.py   (rebuild data first: python scripts/build_site_data.py)
Note: expects the current data state (0 verified rows); update the first checks once rows are verified."""
import asyncio, sys
from playwright.async_api import async_playwright
import pathlib
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = (ROOT / "site" / "index.html").as_uri()
SH = str(ROOT / "tests" / "_shots") + "/"
(ROOT / "tests" / "_shots").mkdir(exist_ok=True)
errs = []; results = []
def check(name, cond, extra=""):
    results.append((name, bool(cond), extra)); print(("PASS " if cond else "FAIL ") + name, extra)

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        import mimetypes

        async def newpage(**kw):
            """New page whose https://raw.githubusercontent.com/<owner>/<repo>/<branch>/site/* requests are
            served from the local site/ folder (index.html may point its CSS/JS at those URLs)."""
            ctx = await b.new_context(**kw)

            async def serve(route):
                import re as _re
                rel = _re.sub(r"^https://raw\.githubusercontent\.com/[^/]+/[^/]+/[^/]+/site/", "", route.request.url).split("?")[0]
                f = ROOT / "site" / rel
                if not f.is_file():
                    return await route.fulfill(status=404, body="nf")
                await route.fulfill(status=200, content_type=mimetypes.guess_type(str(f))[0] or "text/plain", body=f.read_bytes())
            await ctx.route("https://raw.githubusercontent.com/**", serve)
            return await ctx.new_page()
        pg = await newpage(viewport={"width":1280,"height":900})
        pg.on("console", lambda m: errs.append(("console", m.text)) if m.type in ("error","warning") else None)
        pg.on("pageerror", lambda e: errs.append(("pageerror", str(e))))

        # 1. default mode, nothing verified
        await pg.goto(SITE); await pg.wait_for_selector("h1")
        t = await pg.inner_text("main")
        check("default: shows empty state", "No verified records yet" in t)
        check("default: does NOT show draft rows/charts", "Tests by principal investigator" not in t)
        check("default: banner hidden", await pg.is_hidden("#preview-banner"))
        await pg.screenshot(path=SH+"01_overview_default.png", full_page=True)
        await pg.click("nav a[data-route=explorer]"); await pg.wait_for_selector(".tablewrap")
        check("default explorer: zero rows shown", "Showing 0 of 0 verified" in await pg.inner_text(".count"))
        check("default: detail of unverified id refuses", True)
        await pg.goto(SITE+"#/experiment/BASSII-B1"); await pg.wait_for_selector("h1")
        check("default: unverified detail -> not found", "Record not found" in await pg.inner_text("main"))

        # 2. preview mode
        await pg.goto(SITE+"?preview=draft"); await pg.wait_for_selector(".chart")
        check("preview: banner visible", await pg.is_visible("#preview-banner"))
        check("preview: banner says UNVERIFIED", "UNVERIFIED" in await pg.inner_text("#preview-banner"))
        stats = await pg.inner_text(".stats")
        check("preview: stat shows 126", "126" in stats, stats.replace("\n"," | "))
        await pg.screenshot(path=SH+"02_overview_preview.png", full_page=True)

        await pg.goto(SITE+"?preview=draft#/explorer"); await pg.wait_for_selector("tbody tr.row")
        n = await pg.locator("tbody tr.row").count()
        check("explorer: 126 rows", n == 126, str(n))
        await pg.select_option("#fpi", "Olson")
        n = await pg.locator("tbody tr.row").count(); check("filter Olson = 24", n == 24, str(n))
        await pg.select_option("#fo2", "lt16")
        n = await pg.locator("tbody tr.row").count(); check("Olson + O2<16 narrows", 0 < n < 24, str(n))
        await pg.select_option("#fpi", ""); await pg.select_option("#fo2", "")
        await pg.fill("#q", "hcl")
        n = await pg.locator("tbody tr.row").count(); check("search 'hcl' finds rows", 5 < n < 126, str(n))
        await pg.fill("#q", "zzzzqqq")
        check("search no match message", "No records match" in await pg.inner_text("tbody"))
        await pg.click("button:has-text('Clear')"); await pg.wait_for_selector("tbody tr.row")
        n = await pg.locator("tbody tr.row").count(); check("clear resets to 126", n == 126, str(n))
        await pg.screenshot(path=SH+"03_explorer.png")

        # order check: first row should be B1 then B2 (natural, not string order)
        ids = await pg.locator("tbody tr.row td.id").all_inner_texts()
        check("natural sort B1,B2,B3", ids[:3] == ["B1","B2","B3"], str(ids[:4]))
        check("pairs sorted P3a before P3b", ids.index("P3a") + 1 == ids.index("P3b"))

        mats = await pg.locator("tbody tr.row td:nth-child(3)").all_inner_texts()
        check("no flow words polluting material column", not any(w in m for m in mats for w in ("Opposed","Concurrent","Stagnation")))
        check("material column never empty", all(m.strip() for m in mats))
        # 3. detail pages
        await pg.goto(SITE+"?preview=draft#/experiment/BASSII-P22a"); await pg.wait_for_selector(".cols")
        t = await pg.inner_text("main")
        check("detail P22a: suspect callout", "O2 reading suspect" in t)
        check("detail P22a: shows 20.8 and 0.6", "20.8" in t and "0.6" in t)
        check("detail P22a: clean material heading", "9.525-mm black rod" in await pg.inner_text("h1") and "Opposed" not in await pg.inner_text("h1"))
        check("detail P22a: label chips present", all(x in t for x in ("MEASURED","PUBLISHED","OURS")) or all(x.lower() in t.lower() for x in ("measured","published","ours")))
        check("detail P22a: Table A.3 page cited", "Table A.3" in t and "report page 107" in t)
        await pg.screenshot(path=SH+"04_detail_suspect.png", full_page=True)
        await pg.goto(SITE+"?preview=draft#/experiment/BASSII-M5"); await pg.wait_for_selector(".cols")
        check("detail M5: hand-keyed callout", "Hand-keyed row" in await pg.inner_text("main"))
        await pg.goto(SITE+"?preview=draft#/experiment/BASSII-NOPE"); await pg.wait_for_selector("h1")
        check("detail unknown id: not found", "Record not found" in await pg.inner_text("main"))
        await pg.goto(SITE+"#/about"); await pg.wait_for_selector("h1")
        check("about renders", "The rules we hold ourselves to" in await pg.text_content("main"))
        await pg.screenshot(path=SH+"05_about.png", full_page=True)

        # 4. mobile
        m = await newpage(viewport={"width":390,"height":800})
        m.on("pageerror", lambda e: errs.append(("pageerror", str(e))))
        await m.goto(SITE+"?preview=draft"); await m.wait_for_selector(".chart")
        sw = await m.evaluate("document.documentElement.scrollWidth"); 
        check("mobile: no horizontal page scroll (overview)", sw <= 391, str(sw))
        await m.screenshot(path=SH+"06_mobile_overview.png", full_page=True)
        await m.goto(SITE+"?preview=draft#/experiment/BASSII-P22a"); await m.wait_for_selector(".cols")
        sw = await m.evaluate("document.documentElement.scrollWidth")
        check("mobile: no horizontal page scroll (detail)", sw <= 391, str(sw))
        await m.screenshot(path=SH+"07_mobile_detail.png", full_page=True)
        await b.close()
asyncio.run(main())
print("\nconsole/page errors:", errs if errs else "none")
print(sum(1 for r in results if r[1]), "/", len(results), "checks passed")
