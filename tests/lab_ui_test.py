"""Browser test of the Intelligence Lab page. The server function is SIMULATED (no API key, no cost):
1) served over http with /api/ask mocked -> answer, grade, basis labels and citation links render;
2) a mocked 429 -> falls back to keyword search; 3) opened from file:// -> offline keyword search, no network call.
Run: python tests/lab_ui_test.py"""
import asyncio, json, mimetypes, pathlib, sys
from playwright.async_api import async_playwright
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ok = True
def check(name, cond, extra=""):
    global ok
    ok &= bool(cond); print(("PASS " if cond else "FAIL ") + name + ("" if cond else " " + str(extra)))

ANSWER = {"status": "answered", "grade": "strong", "summary": "Two investigations ran tests at 30% O2 or more at 10.2 psi or less.", "model": "claude-opus-5-5",
          "key_points": [{"text": "ACME CFI-G ran 48 such tests.", "basis": "nasa_record", "citations": ["PSI-159"]},
                         {"text": "Solid materials were not tested above 23% O2.", "basis": "interpretation", "citations": ["PSI-25", "brief-moon"]}],
          "gaps": ["No partial-gravity data."], "dropped_points": 1,
          "citations": [{"id": "PSI-159", "kind": "investigation", "title": "ACME CFI-G", "route": "#/investigation/PSI-159", "source": "NASA PSI PSI-159"},
                        {"id": "PSI-25", "kind": "investigation", "title": "BASS-II", "route": "#/investigation/PSI-25", "source": "NASA PSI PSI-25"},
                        {"id": "brief-moon", "kind": "brief", "title": "Brief", "route": "#/investigations", "source": "challenge brief"}],
          "evidence": [{"id": "PSI-159", "kind": "investigation", "title": "ACME CFI-G", "route": "#/investigation/PSI-159", "source": "NASA PSI", "score": 9.1}]}

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page(); errs = []; pg.on("pageerror", lambda e: errs.append(str(e)))
        calls = []
        mode = {"status": 200}
        async def site(route):
            path = route.request.url.split("http://flare.test/", 1)[1].split("#")[0].split("?")[0] or "index.html"
            f = SITE / path
            if not f.is_file(): return await route.fulfill(status=404, body="nf")
            await route.fulfill(status=200, content_type=mimetypes.guess_type(str(f))[0] or "text/plain", body=f.read_bytes())
        async def api(route):
            calls.append(json.loads(route.request.post_data or "{}"))
            if mode["status"] == 200: await route.fulfill(status=200, content_type="application/json", body=json.dumps(ANSWER))
            else: await route.fulfill(status=429, content_type="application/json", body=json.dumps({"error": "Question limit reached for now."}))
        await pg.route("http://flare.test/**", site)       # registered first = checked last
        await pg.route("http://flare.test/api/ask", api)
        await pg.goto("http://flare.test/index.html#/lab"); await pg.wait_for_selector(".lab-form")
        check("lab: page explains retrieve -> answer -> check", await pg.locator(".lab-how li").count() == 3)
        check("lab: example questions include an abstain example", await pg.locator(".abst-ex").count() == 1)
        await pg.click(".lab-ex .chip-btn >> nth=0"); await pg.wait_for_selector(".lab-answer")
        t = await pg.inner_text(".lab-out")
        check("lab: sends only the question to the server", calls and list(calls[0].keys()) == ["question"], calls)
        check("lab: answer, grade and grade rule shown", "Evidence grade: Strong" in t and "Grade rule" in t and "not chosen by the AI" in t)
        check("lab: each point labelled NASA record vs AI interpretation", "NASA record" in t.replace("NASA RECORD", "NASA record") or "NASA RECORD" in t)
        check("lab: citation chips link to site pages", await pg.locator('.lab-answer a.cite[href="#/investigation/PSI-159"]').count() == 1)
        check("lab: dropped-point notice and no-probability disclaimer", "removed because their citations" in t and "no fire probabilities" in t)
        mode["status"] = 429
        await pg.fill("#labq", "Which tests used Nomex fabric in BASS?"); await pg.click("button:has-text('Ask the Lab')"); await pg.wait_for_selector(".lab-local")
        check("lab: server limit -> keyword-search fallback with the reason", "Question limit reached" in await pg.inner_text(".lab-local"))
        n = len(calls)
        await pg.goto((SITE / "index.html").as_uri() + "#/lab"); await pg.wait_for_selector(".lab-form")
        await pg.fill("#labq", "How did FLEX methanol droplet tests end?"); await pg.click("button:has-text('Ask the Lab')"); await pg.wait_for_selector(".lab-local")
        t = await pg.inner_text(".lab-local")
        check("lab (file://): offline keyword search, no network call", "online site" in t and len(calls) == n and "FLEX" in t)
        check("lab: no JS errors", not errs, errs)
        await pg.set_viewport_size({"width": 390, "height": 800}); await pg.goto("http://flare.test/index.html#/lab"); await pg.wait_for_selector(".lab-form")
        check("lab: no horizontal scroll at 390px", await pg.evaluate("document.documentElement.scrollWidth") <= 392)
        await b.close()
asyncio.run(main())
print("\nALL LAB UI CHECKS PASSED" if ok else "\nSOME LAB UI CHECKS FAILED"); sys.exit(0 if ok else 1)
