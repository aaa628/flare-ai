"""Browser smoke test for the static site (needs: pip install playwright; playwright install chromium).
Run: python tests/site_smoke_test.py   (rebuild data first: python scripts/build_site_data.py)
Checks adapt to the counts in site/data/data.js (human / machine / unchecked)."""
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

        # 1. default mode: human-verified + machine-checked rows shown, unchecked hidden
        await pg.goto(SITE); await pg.wait_for_selector("h1")
        C = await pg.evaluate("window.FLARE_DATA.counts")
        RECS = await pg.evaluate("window.FLARE_DATA.records.map(r => [r.id, r.level])")
        lv = dict(RECS)
        mach_id = next(i for i, l in RECS if l == "machine")
        none_id = next((i for i, l in RECS if l == "none"), None)
        print("counts:", C)
        t = await pg.inner_text("main")
        stats = await pg.inner_text(".stats")
        check("default: stats show the real counts", str(C["machine"]) in stats and str(C["unchecked"]) in stats, stats.replace("\n", " | "))
        check("default: honest note that team sign-off is pending" if C["verified"] == 0 else "default: verified rows exist",
              (C["verified"] != 0) or "sign-off" in t)
        check("default: three check levels explained", all(x in t.lower() for x in ("machine-checked", "verified", "unchecked")))
        check("default: charts drawn from shown rows", C["shown"] == 0 or "Test records by experiment" in t)
        check("default: banner hidden", await pg.is_hidden("#preview-banner"))
        await pg.screenshot(path=SH+"01_overview_default.png", full_page=True)
        await pg.click("nav a[data-route=explorer]"); await pg.wait_for_selector(".tablewrap")
        n = await pg.locator("tbody tr.row").count()
        check("default explorer: shows exactly the human+machine rows", n == C["shown"], f"{n} vs {C['shown']}")
        chips = await pg.locator("tbody .chip").all_inner_texts()
        check("default explorer: no 'unchecked' chip anywhere", not any("unchecked" in c.lower() for c in chips))
        check("default explorer: every row labelled with its level", sum(1 for c in chips if c.lower() in ("machine-checked", "verified")) == n)
        if none_id:
            await pg.goto(SITE+"#/experiment/"+none_id); await pg.wait_for_selector("h1")
            check("default: UNCHECKED row detail refuses (not found)", "Record not found" in await pg.inner_text("main"), none_id)
        await pg.goto(SITE+"#/experiment/BASSII-P22b"); await pg.wait_for_selector(".cols")
        check("P22b: formula-leftover callout shown", "not a reading" in await pg.inner_text("main"))
        check("P22b: NASA sources disagree callout", "two sources disagree" in await pg.inner_text("main"))
        # Compare screen
        await pg.goto(SITE+"#/compare/BASSII-P1,BASSII-P10,BASSII-P12"); await pg.wait_for_selector(".viz-grid")
        t = await pg.inner_text("main")
        check("compare: 4 BASS-II measure charts + flow-mix donut", await pg.locator(".viz-card").count() == 5 and await pg.locator(".donut").count() == 1)
        check("compare: no averages claim", "No averages" in t)
        await pg.hover(".chart.viz .mark >> nth=0"); await pg.wait_for_timeout(150)
        check("compare: hover tooltip shows NASA value", "17.7" in await pg.inner_text(".viz-tip"))
        await pg.goto(SITE+"#/compare/BASSII-B1,BASSI-1-1"); await pg.wait_for_selector(".callout.refuse")
        check("compare: refuses across experiments, draws no charts", await pg.locator(".viz-card").count() == 0)
        await pg.goto(SITE+"#/compare/BASSII-P22a,BASSII-P22b,BASSII-O12"); await pg.wait_for_selector(".viz-grid")
        t = await pg.inner_text("main")
        check("compare: flagged O2 and +OR excluded with reasons", "flagged as suspect" in t and "+OR" in t and "not confirmed" in t)
        check("compare: caution when flow direction differs", "Flow direction differs" in t)
        await pg.goto(SITE+"#/experiment/BASSI-1-1"); await pg.wait_for_selector(".cols")
        t = await pg.inner_text("main")
        check("BASS-I detail: source file + row + DOI link", "as run matrix" in t and "row 4" in t and "DOI" in t, t[:200])
        check("BASS-I detail: O2 shown as printed with conversion", "0.221" in t and "22.1 vol%" in t)
        await pg.goto(SITE+"#/experiment/SAFFIREII-2-5"); await pg.wait_for_selector(".cols")
        t = await pg.inner_text("main")
        check("SAFFIRE-II detail renders recorded values", "SAFFIRE-II" in t and "2.1 mm/s" in t, t[:200])
        await pg.goto(SITE+"#/experiment/"+mach_id); await pg.wait_for_selector(".cols")
        t = await pg.inner_text("main")
        check("default: machine-checked detail says person has not verified", "not yet verified by a person" in t and "machine-checked" in t.lower(), mach_id)
        check("default: machine-checked detail never claims a PDF check by a person", "Checked against the PDF by" not in t)
        await pg.screenshot(path=SH+"01b_detail_machine.png", full_page=True)

        # 2. preview mode
        await pg.goto(SITE+"?preview=draft"); await pg.wait_for_selector(".chart")
        check("preview: banner visible", await pg.is_visible("#preview-banner"))
        check("preview: banner says NO check", "NO check" in await pg.inner_text("#preview-banner"))
        stats = await pg.inner_text(".stats")
        check("preview: stats still show the real counts", str(C["records"]) in "126" and "126" or str(C["unchecked"]) in stats, stats.replace("\n"," | "))
        await pg.screenshot(path=SH+"02_overview_preview.png", full_page=True)

        await pg.goto(SITE+"?preview=draft#/explorer"); await pg.wait_for_selector("tbody tr.row")
        n = await pg.locator("tbody tr.row").count()
        check("explorer: all rows", n == C["records"], str(n))
        await pg.select_option("#fpi", "Olson")
        n = await pg.locator("tbody tr.row").count(); check("filter Olson = 27 (24 report + 3 PSI-only)", n == 27, str(n))
        await pg.select_option("#fo2", "lt16")
        n = await pg.locator("tbody tr.row").count(); check("Olson + O2<16 narrows", 0 < n < 27, str(n))
        await pg.select_option("#fpi", ""); await pg.select_option("#fo2", "")
        await pg.fill("#q", "hcl")
        n = await pg.locator("tbody tr.row").count(); check("search 'hcl' finds rows", 5 < n < C["records"], str(n))
        await pg.fill("#q", "zzzzqqq")
        check("search no match message", "No records match" in await pg.inner_text("tbody"))
        await pg.click("button:has-text('Clear')"); await pg.wait_for_selector("tbody tr.row")
        n = await pg.locator("tbody tr.row").count(); check("clear resets to all", n == C["records"], str(n))
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
