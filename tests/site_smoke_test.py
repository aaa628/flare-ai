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
        idx = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
        check("index.html loads assets with relative links (offline + any static host)",
              'href="css/style.css"' in idx and 'src="js/app.js"' in idx and "raw.githubusercontent" not in idx)
        C = await pg.evaluate("window.FLARE_DATA.counts")
        RECS = await pg.evaluate("window.FLARE_DATA.records.map(r => [r.id, r.level])")
        lv = dict(RECS)
        mach_id = next(i for i, l in RECS if l == "machine")
        none_id = next((i for i, l in RECS if l == "none"), None)
        print("counts:", C)
        t = await pg.inner_text("main")
        stats = await pg.inner_text(".hero-side")
        check("default: evidence legend shows the real counts", all(str(C[k]) in stats for k in ("verified", "machine", "unchecked")), stats.replace("\n", " | "))
        check("overview: human sign-off shown separately and prominently (0 of N, not a sign-off)", "of " + str(C["records"]) in stats and "not a sign-off" in stats.lower() and await pg.locator(".signoff-box").count() == 1)
        check("overview: automated checks listed with exact counts", str(C["pdf_match"]) + " of 126" in stats and str(C["psi_agree"]) + " of 126" in stats)
        check("overview: each chart says what it includes and leaves out", await pg.locator(".qcard .limits").count() == 2 and "Left out" in t)
        check("overview: says what the site can answer + one primary action", "what this site can answer" in t.lower() and await pg.locator(".hero .btn").count() == 1)
        check("overview: experiment families kept separate", await pg.locator("table.methods tbody tr").count() == 3)
        check("overview: every chart has a how-to-read line and unit", await pg.locator(".qcard").count() == await pg.locator(".qcard .howto").count() == await pg.locator(".qcard .unit-pill").count() == 2)
        check("default: three check levels explained", all(x in t.lower() for x in ("machine-checked", "verified", "unchecked")))
        check("default: charts drawn from shown rows", C["shown"] == 0 or "Which experiments does the evidence come from?" in t)
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
        check("compare: 4 measure charts, donut, rules card, table, 3 stat tiles", await pg.locator(".vcard .chart.viz:not(.donut)").count() == 8 and await pg.locator(".donut").count() == 1 and await pg.locator(".tile").count() == 3 and "How this comparison works" in t)
        check("compare: no averages claim", "No averages" in t)
        await pg.hover(".chart.viz .mark >> nth=0"); await pg.wait_for_timeout(150)
        check("compare: hover tooltip shows NASA value", "17.7" in await pg.inner_text(".viz-tip"))
        await pg.goto(SITE+"#/compare/BASSII-B1,BASSI-1-1"); await pg.wait_for_selector(".refuse-card")
        check("compare: refuses across experiments, draws no charts", await pg.locator(".chart.viz").count() == 0 and await pg.locator(".refuse-card").count() == 1)
        check("compare: refusal shows the differing methods next to the reason", await pg.locator(".precheck .pc-warn").count() >= 2)
        check("compare: refusal lists which conditions failed", await pg.locator(".refuse-card ul.conds li.fail").count() == 3)
        await pg.goto(SITE+"#/compare"); await pg.wait_for_selector(".examples")
        check("compare: empty state offers worked, limited and refusal examples", await pg.locator(".ex").count() == 4 and await pg.locator(".ex-refused").count() == 1)
        await pg.click(".ex-worked >> nth=0"); await pg.wait_for_selector(".viz-grid")
        check("compare: worked example opens a full comparison", "BASSII-P13a" in pg.url and await pg.locator(".vcard .chart.viz").count() >= 4)
        await pg.goto(SITE+"#/compare/BASSII-P22a,BASSII-P22b,BASSII-O12"); await pg.wait_for_selector(".viz-grid")
        t = await pg.inner_text("main")
        check("compare: flagged O2 and +OR excluded with reasons", "flagged as suspect" in t and "+OR" in t and "not confirmed" in t)
        check("compare: caution when flow direction differs", "Flow direction differs" in t)
        check("compare: 'before charting' panel lists source, method and missing fields", all(x in t.lower() for x in ("before charting", "how oxygen was recorded", "missing or suspect here")))
        check("compare: every chart card says what it left out, next to the chart", await pg.locator(".limits").count() == 4 and await pg.locator(".limits.has").count() >= 3)
        check("compare: every SVG chart has a text alternative", await pg.evaluate("[...document.querySelectorAll('svg.chart')].every(s => (s.getAttribute('aria-label')||'').length > 20 && s.querySelector('title'))"))
        check("compare: raw-O2 axis reaches the tallest bar (no clipping)", await pg.evaluate("""(() => { const c=[...document.querySelectorAll('.vcard')].find(e=>e.textContent.includes('Oxygen, raw sensor')); if(!c) return true;
          return [...c.querySelectorAll('svg.chart path.mark')].every(p => p.getBBox().y >= 15); })()"""))
        await pg.set_viewport_size({"width":390,"height":844})
        check("compare: no horizontal scroll at 390px", await pg.evaluate("document.documentElement.scrollWidth") <= 392)
        await pg.set_viewport_size({"width":1280,"height":900})
        await pg.goto(SITE+"#/experiment/BASSI-1-1"); await pg.wait_for_selector(".cols")
        t = await pg.inner_text("main")
        check("BASS-I detail: source file + row + DOI link", "as run matrix" in t and "row 4" in t and "DOI" in t, t[:200])
        check("BASS-I detail: O2 shown converted, with NASA's field name and the x100 method", "0.221" in t and "22.1 vol%" in t and "O2 % by volume" in t and "Multiplied by 100" in t)
        check("BASS-I detail: exact NASA source file is served by the site", (ROOT / "site" / "sources" / "psi" / "PSI-26_as_run_test_matrix_BASS.xlsx").exists())
        await pg.goto(SITE+"#/experiment/SAFFIREII-2-5"); await pg.wait_for_selector(".cols")
        t = await pg.inner_text("main")
        check("SAFFIRE-II detail: provenance shows NASA field name and unit", "Air Flow (cm/s)" in t and "cm/s" in t, t[:200])
        check("SAFFIRE-II detail: every NASA column kept under technical details", "2.1 mm/s" in await pg.text_content(".tech"))
        check("SAFFIRE-II detail: opens NASA dataset page and the exact file", await pg.locator('a[href*="psi.nasa.gov/physci/repo/data/investigations/PSI-99"]').count() == 1 and await pg.locator('a[href="sources/psi/PSI-99_experimental_table_SAFFIRE-II.csv"]').count() == 1)
        await pg.goto(SITE+"#/experiment/"+mach_id); await pg.wait_for_selector(".cols")
        t = await pg.inner_text("main")
        check("default: machine-checked detail says no person has signed it", "No person has signed this record" in t and "machine-checked" in t.lower(), mach_id)
        check("default: machine-checked detail never claims a PDF check by a person", "Checked against the PDF by" not in t)
        await pg.screenshot(path=SH+"01b_detail_machine.png", full_page=True)

        # 2. preview mode
        await pg.goto(SITE+"?preview=draft"); await pg.wait_for_selector(".chart")
        check("preview: banner visible", await pg.is_visible("#preview-banner"))
        check("preview: banner says NO check", "NO check" in await pg.inner_text("#preview-banner"))
        stats = await pg.inner_text(".hero-side")
        check("preview: legend still shows the real counts", str(C["unchecked"]) in stats, stats.replace("\n"," | "))
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
        check("explorer: active filter chip shown for the search", await pg.locator(".fchip").count() == 1)
        await pg.click(".active-filters button:has-text('Reset all')"); await pg.wait_for_selector("tbody tr.row")
        check("explorer: sticky table headings", await pg.evaluate("getComputedStyle(document.querySelector('table.records thead th')).position") == "sticky")
        check("explorer: O2 start carries its method tag", "cal." in (await pg.inner_text("tbody tr.row >> nth=0")).lower())
        await pg.focus("tbody tr.row >> nth=0"); await pg.keyboard.press("Enter"); await pg.wait_for_timeout(200)
        check("explorer: Enter on a focused row opens the record", "#/experiment/" in pg.url)
        check("detail: header groups identity, checks and source reference", await pg.locator(".record-head h1").count() == 1 and await pg.locator(".record-head .checks li").count() >= 3 and "source reference" in (await pg.inner_text(".record-head")).lower())
        check("detail: report record links to the PDF at its page", await pg.locator('.record-head a[href*="TM-20210011385.pdf#page="]').count() == 1)
        check("detail: provenance table + technical details lower on the page", await pg.locator(".prov-t tbody tr").count() >= 4 and await pg.locator("details.tech").count() == 1)
        await pg.goto(SITE+"#/explorer"); await pg.wait_for_selector("tbody tr.row")
        n = await pg.locator("tbody tr.row").count(); check("clear resets to all", n == C["records"], str(n))
        await pg.screenshot(path=SH+"03_explorer.png")

        # order check: first row should be B1 then B2 (natural, not string order)
        ids = await pg.locator("tbody tr.row td.id a").all_inner_texts()
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
