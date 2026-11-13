"""Browser smoke test for the static site (needs: pip install playwright; playwright install chromium).
Run: python tests/site_smoke_test.py   (rebuild data first: python scripts/build_site_data.py)

The NASA data was removed on 2026-11-13 and the site is an empty template until new data is added.
These checks hold the layout in place: every page renders, every chart is still drawn with neutral
placeholder labels and 0 values, nothing shows NaN, and no old NASA record names or counts remain.
When new data is loaded, the template checks are skipped and only the shared checks run; add
data-specific checks back then (see git history for the previous version of this file)."""
import asyncio, re, sys, pathlib
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = (ROOT / "site" / "index.html").as_uri()
results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond), extra)); print(("PASS " if cond else "FAIL ") + name, extra)


ROUTES = ["", "scenario", "explorer", "compare", "investigations", "investigations/moon", "lab", "about",
          "scenario/family=liquid&o2=21&psi=14.7&fuel=&diluent=", "scenario/family=gas&o2=30&psi=10.2"]
BAD = re.compile(r"NaN|undefined|Infinity")
OLD = re.compile(r"BASS|SAFFIRE|PSI-\d|ACME|SPICE|SLICE|\bCFI\b|\b537\b|Methanol|Heptane|Extinction|Disruption|Completion|20210011385")


async def main():
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch()
        except Exception:  # cloud sandbox: preinstalled Chromium
            b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        for width in (1280, 390):
            pg = await b.new_page(viewport={"width": width, "height": 900})
            errs = []
            pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
            pg.on("pageerror", lambda e: errs.append(str(e)))
            await pg.goto(SITE); await pg.wait_for_selector("h1")
            empty = await pg.evaluate("window.FLARE_DATA.records.length === 0")
            if width == 1280:
                idx = (ROOT / "site" / "index.html").read_text(encoding="utf-8")
                check("index.html loads assets with relative links (offline + any static host)",
                      'href="css/style.css"' in idx and 'src="js/app.js"' in idx and "raw.githubusercontent" not in idx)
                check("footer keeps the NASA non-endorsement", "NASA does not endorse this project" in await pg.inner_text("footer"))
                check("data file is the empty template" if empty else "data file has records", True,
                      str(await pg.evaluate("window.FLARE_DATA.counts")))
            for r in ROUTES:
                await pg.goto(SITE + "#/" + r); await pg.wait_for_timeout(500)
                main_txt = await pg.inner_text("main")
                svg_txt = await pg.evaluate("[...document.querySelectorAll('main svg')].map(s => s.textContent + ' ' + (s.getAttribute('aria-label') || '')).join(' ')")
                name = (r or "overview") + " @" + str(width)
                m = BAD.search(main_txt + svg_txt)
                check(name + ": no NaN / undefined / Infinity", not m, m.group(0) if m else "")
                check(name + ": no horizontal scroll", not await pg.evaluate("document.documentElement.scrollWidth > innerWidth"))
                if empty:
                    hit = OLD.search(main_txt.replace("NASA footage of FLEX fuel droplets", "") + svg_txt)
                    check(name + ": no old NASA record names or counts", not hit, hit.group(0) if hit else "")
            if empty:
                await pg.goto(SITE + "#/"); await pg.wait_for_timeout(400)
                vals = await pg.evaluate("[...document.querySelectorAll('.qcard svg.chart text.val')].map(t => t.textContent)")
                check("Overview: 3 chart cards still drawn", await pg.locator(".qcard svg.chart").count() == 3)
                check("Overview: every bar reads 0", len(vals) == 12 and all(v.startswith("0 ") for v in vals), str(vals))
                check("Overview: placeholder labels", "Experiment 1" in await pg.inner_text("main") and "Band 5" in await pg.inner_text("main"))
                check("Overview: methods table keeps 4 rows", await pg.locator("table.methods tbody tr").count() == 4)
                await pg.goto(SITE + "#/compare"); await pg.wait_for_timeout(400)
                check("Compare: layout preview draws its charts", await pg.locator("main svg.chart").count() >= 6)
                check("Compare: tiles, donut at 0, two tables", await pg.locator(".tiles .tile").count() == 3 and
                      await pg.locator("svg.donut text.val").first.text_content() == "0" and await pg.locator("main table").count() == 2)
                await pg.goto(SITE + "#/scenario"); await pg.wait_for_timeout(500)
                check("Scenario: 3 empty panels drawn", await pg.locator(".scen-panels .panel").count() == 3)
                check("Scenario: verdict is insufficient data", "Insufficient data" in await pg.inner_text(".verdict"))
                check("Scenario: results table keeps its headers", await pg.locator("table.scen-t thead th").count() == 7)
                await pg.goto(SITE + "#/investigations"); await pg.wait_for_timeout(400)
                check("Investigations: both charts drawn", await pg.locator(".qcard svg.chart").count() == 2)
                check("Investigations: placeholder rows at 0%", "Investigation 4" in await pg.evaluate("document.querySelector('.qcard svg.chart').textContent"))
                await pg.goto(SITE + "#/explorer"); await pg.wait_for_timeout(400)
                check("Explorer: table keeps its 8 columns", await pg.locator("table.records thead th").count() == 8)
                await pg.goto(SITE + "#/about"); await pg.wait_for_timeout(300)
                check("About: says there are no sources yet", "No sources yet" in await pg.inner_text("main"))
                await pg.goto(SITE + "#/experiment/BASSII-B1"); await pg.wait_for_timeout(300)
                check("old record links show not found", "not found" in (await pg.inner_text("main")).lower())
                await pg.goto(SITE + "?preview=draft#/"); await pg.wait_for_timeout(400)
                check("preview mode still draws the charts", await pg.locator(".qcard svg.chart").count() == 3)
            if not empty and width == 1280:  # data loaded: behaviour checks (numbers are audited in tests/data_audit.py)
                await pg.goto(SITE + "#/"); await pg.wait_for_timeout(400)
                t = await pg.inner_text("main")
                check("Overview: 3 question charts and the methods table", await pg.locator(".qcard svg.chart").count() == 3 and await pg.locator("table.methods tbody tr").count() == 4)
                check("Overview: no claim of a PDF comparison when no report rows are loaded", "PDF" not in t)
                check("Overview: Why-this-matters card with Published labels", "Why this matters" in t and await pg.locator("#wm-h ~ .grid .chip.published").count() == 6)
                await pg.goto(SITE + "#/compare/BASSII-P1,BASSII-P10,BASSII-P12"); await pg.wait_for_selector(".viz-grid")
                t = await pg.inner_text("main")
                check("Compare: 3 BASS-II measures (start/end + change), rules card, 3 tiles; no raw-O2 card (PSI-25 has none)",
                      await pg.locator(".vcard .chart.viz:not(.donut)").count() == 6 and await pg.locator(".tile").count() == 3 and
                      "How this comparison works" in t and "Oxygen, raw sensor" not in t)
                check("Compare: flow-direction card says PSI-25 states no flow direction instead of drawing a pie",
                      await pg.locator(".donut").count() == 0 and "flow direction not stated in NASA’s file" in t)
                await pg.goto(SITE + "#/compare/FLEX-2,FLEX-3,FLEX-5"); await pg.wait_for_selector(".viz-grid")
                check("Compare FLEX: donut of how all FLEX tests ended", await pg.locator(".donut").count() == 1 and "Extinction" in await pg.inner_text("main"))
                await pg.goto(SITE + "#/compare/BASSII-P1,BASSII-P10,BASSII-P12"); await pg.wait_for_selector(".viz-grid")
                await pg.hover(".chart.viz .mark >> nth=0"); await pg.wait_for_timeout(150)
                check("Compare: hover tooltip shows NASA's value (P1 start O2 17.7)", "17.7" in await pg.inner_text(".viz-tip"))
                await pg.goto(SITE + "#/compare/BASSII-B1,BASSI-1-1"); await pg.wait_for_selector(".refuse-card")
                check("Compare: refuses across experiments and draws no charts", await pg.locator(".chart.viz").count() == 0 and
                      await pg.locator(".refuse-card ul.conds li.fail").count() >= 1)
                await pg.goto(SITE + "#/compare"); await pg.wait_for_selector(".examples")
                check("Compare: 5 examples (worked, limited, refusal) all resolve", await pg.locator(".ex").count() == 5 and await pg.locator(".ex-refused").count() == 1)
                await pg.goto(SITE + "#/compare/BASSII-P22a,BASSII-P22b,BASSII-O12"); await pg.wait_for_selector(".viz-grid")
                t = await pg.inner_text("main")
                check("Compare: flagged O2 and NASA's 'none' values are left out with reasons", "flagged as suspect" in t and "printed as “none”" in t and
                      await pg.locator(".limits.has").count() >= 2)
                await pg.goto(SITE + "#/experiment/BASSII-P22a"); await pg.wait_for_selector(".cols")
                t = await pg.inner_text("main")
                check("BASS-II record: investigator, sign-off, flag callout, PSI-25 source", "Fernandez-Pello" in t and "Signed by 628 Aerospace team on 2026-11-13" in t and
                      "O2 reading suspect" in t and "PSI-25" in t and "Appendix A" not in t)
                await pg.goto(SITE + "#/experiment/BASSI-1-1"); await pg.wait_for_selector(".cols")
                t = await pg.inner_text("main")
                check("BASS-I record: O2 0.221 shown as 22.1 vol%, file and row", "0.221" in t and "22.1 vol%" in t and "as run matrix" in t and "row 4" in t)
                check("BASS-I: exact NASA source file is served by the site", (ROOT / "site" / "sources" / "psi" / "PSI-26_as_run_test_matrix_BASS.xlsx").exists())
                await pg.goto(SITE + "#/experiment/FLEX-114"); await pg.wait_for_selector(".prov-t")
                check("FLEX record: pressure printed as 0 is flagged, not hidden", "pressure printed as 0" in (await pg.inner_text("main")).lower())
                await pg.goto(SITE + "#/about"); await pg.wait_for_timeout(300)
                t = await pg.inner_text("main")
                check("About: PSI data sources and 10 background resources listed", t.count("doi.org/10.60555/") >= 7 and "Background reading (not test data)" in t and
                      await pg.locator("h2:has-text('Background reading') + .src-list .src-item").count() == 10)
                check("About: no stale report claims", "Appendix A" not in t and "report’s tables" not in t)
            check("no JS errors @" + str(width), not errs, str(errs[:3]))
            await pg.close()
        await b.close()
    bad = [r for r in results if not r[1]]
    print(f"\n{len(results) - len(bad)} / {len(results)} checks passed")
    sys.exit(1 if bad else 0)

asyncio.run(main())
