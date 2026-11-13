"""Independent audit of every number the site shows, straight from NASA's raw PSI files.

It does NOT use scripts/import_psi.py or the site's code to count: it parses data/source/psi/* itself, computes the
numbers, then opens the built site in a browser and requires the rendered numbers to match. It also opens a seeded
random sample of record pages and checks each NASA value shown there against the cell in NASA's file.
Run: python tests/data_audit.py   (needs playwright + openpyxl; build first: python scripts/build_site_data.py)
AUDIT_ALL=1 python tests/data_audit.py   checks every record page instead of a seeded sample of 7 per experiment.
"""
import asyncio, csv, json, os, random, re, sys, pathlib, subprocess, warnings
warnings.filterwarnings("ignore")
from playwright.async_api import async_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
PSI = ROOT / "data" / "source" / "psi"
SITE = (ROOT / "site" / "index.html").as_uri()
results = []


def check(name, cond, extra=""):
    results.append((name, bool(cond), extra)); print(("PASS " if cond else "FAIL ") + name, extra)


def norm(s):
    return " ".join(str(s).split())


def num(s):
    try:
        return float(str(s).strip())
    except ValueError:
        return None


def rows_csv(name, enc="utf-8-sig"):
    with open(PSI / name, encoding=enc, newline="") as f:
        return list(csv.reader(f))


# ---------- 1. independent counts from NASA's raw files ----------
b2 = rows_csv("PSI-25_experimental_table_BASS-II.csv")
b2h = [norm(h) for h in b2[0]]
B2 = [dict(zip(b2h, [norm(c) for c in r])) for r in b2[1:] if len(r) > 1 and norm(r[1])]
o2s = [num(r["Calibrated initial O2 % by vol"]) for r in B2]
bands = [(13, 15), (15, 17), (17, 19), (19, 21), (21, 23)]
band_counts = [sum(1 for v in o2s if v is not None and lo <= v < hi) for lo, hi in bands]
suspect = notnum = 0
for r in B2:
    s, e = num(r["Calibrated initial O2 % by vol"]), r["Calibrated final O2 % by vol"]
    if num(e) is None:
        notnum += bool(e)
    elif abs(num(e) - s) > 3:
        suspect += 1

fx = rows_csv("PSI-69_experimental_table_FLEX.csv", "cp1252")
fxh = [norm(h) for h in fx[0]]
FX = [dict(zip(fxh, [norm(c) for c in r])) for r in fx[1:] if len(r) > 1 and norm(r[0])]
ends = {}
for r in FX:
    ends[r["Test end"]] = ends.get(r["Test end"], 0) + 1
meth = sum(1 for r in FX if "methanol" in r["Fuel"].lower())
hept = sum(1 for r in FX if "heptane" in r["Fuel"].lower())

import openpyxl
ws = openpyxl.load_workbook(PSI / "PSI-26_as_run_test_matrix_BASS.xlsx", data_only=True)["as run matrix"]
# Header is row 3: col 2 = "As run test no.", col 3 = "Test no.", col 5 = "material", col 26 = O2 (ISS environment, fraction).
# A test row has a whole-number as-run no., a test no. and a material (SETUP / STOW / note rows do not).
def _int(v):
    return isinstance(v, int) or (isinstance(v, float) and v.is_integer()) or (isinstance(v, str) and v.strip().isdigit())
B1 = [row for row in ws.iter_rows(min_row=4, values_only=True)
      if _int(row[2]) and row[3] not in (None, "") and row[5] not in (None, "")]
def b1id(row):
    return "BASSI-%d-%s" % (int(float(row[2])), str(int(row[3])) if isinstance(row[3], float) and row[3].is_integer() else str(row[3]).strip())


def saffire_count(name):
    rr = rows_csv(name)
    return sum(1 for r in rr[1:] if r and norm(r[0]) and "/" not in norm(r[0]) and not norm(r[0]).lower().startswith("note"))


SAF = {"SAFFIRE-I": saffire_count("PSI-98_experimental_table_SAFFIRE-I.csv"),
       "SAFFIRE-II": saffire_count("PSI-99_experimental_table_SAFFIRE-II.csv"),
       "SAFFIRE-III": saffire_count("PSI-100_experimental_table_SAFFIRE-III.csv")}
EXP = {"BASS-II": len(B2), "BASS-I": len(B1), "FLEX": len(FX), **SAF}
TOTAL = sum(EXP.values())
print("Independent counts from NASA files:", EXP, "total", TOTAL, "| BASS-II O2 bands", band_counts,
      "| flags suspect/notnum", suspect, notnum, "| FLEX ends", ends, "| methanol/heptane", meth, hept)

# ---------- 2. built data vs raw counts ----------
js = (ROOT / "site" / "data" / "data.js").read_text(encoding="utf-8")
D = json.loads(js[js.index("{"): js.rindex("}") + 1])
check("built record count equals NASA rows", len(D["records"]) == TOTAL, f"{len(D['records'])} vs {TOTAL}")
check("records per experiment equal NASA rows", D["counts"]["experiments"] == EXP, str(D["counts"]["experiments"]))
check("every record machine-checked (re-read equals NASA file)", D["counts"]["machine"] == TOTAL)
check("every record signed (team sign-off) and signed == machine-checked", D["counts"]["verified"] == TOTAL == D["counts"]["machine"])
check("no unchecked records", D["counts"]["unchecked"] == 0)
check("24 investigations, one per PSI catalog file", D["counts"]["investigations"] == len(list((PSI / "catalog").glob("*.json"))) == 24)
flags = {}
for r in D["records"]:
    for f in filter(None, r.get("qc_flag", "").split(";")):
        flags[f] = flags.get(f, 0) + 1
check("BASS-II flags match the raw values", flags.get("o2_final_reading_suspect", 0) == suspect and flags.get("o2_final_not_numeric", 0) == notnum, str(flags))

# Records vs the previous build (git history): the NASA files are byte-identical, so every BASS-I, FLEX and SAFFIRE
# record must carry exactly the same data as before.
old_js = subprocess.run(["git", "show", "d72897d~1:site/data/data.js"], capture_output=True, text=True, cwd=ROOT).stdout
if old_js:
    OLDD = json.loads(old_js[old_js.index("{"): old_js.rindex("}") + 1])
    OLD = {r["id"]: r for r in OLDD["records"]}
    keys = ["experiment", "pi", "source_id", "source_file", "source_row", "material_raw", "flow_mode", "airflow_raw", "o2_raw", "o2_vol_pct", "outcome_raw", "fields"]
    same = diff = 0
    for r in D["records"]:
        o = OLD.get(r["id"])
        if r["experiment"] == "BASS-II" or not o:
            continue
        if all(r.get(k) == o.get(k) for k in keys):
            same += 1
        else:
            diff += 1
    check("BASS-I, FLEX and SAFFIRE records identical to the previous build", diff == 0 and same == len(B1) + len(FX) + sum(SAF.values()), f"same {same}, differ {diff}")
    strip = lambda L: [{k: v for k, v in x.items() if k != "retrieved"} for x in L]
    check("investigation data identical to the previous build (except retrieval date)", strip(OLDD["investigations"]) == strip(D["investigations"]))
    # BASS-II: every PSI-25 value must equal NASA's cell (and, where the old report row exists, the start O2 must equal the PSI value it was cross-checked against)
    b2bad = []
    for r in D["records"]:
        if r["experiment"] != "BASS-II":
            continue
        src = B2[int(r["source_row"]) - 2]
        if "BASSII-" + src["Test #"] != r["id"] or r["o2_vol_pct"] != src["Calibrated initial O2 % by vol"] or r["material_raw"] != src["Fuel Sample Material"]:
            b2bad.append(r["id"])
        for k, v in r["fields"]:
            if src.get(k) != v:
                b2bad.append(r["id"] + ":" + k)
    check("BASS-II: id, material, start O2 and every field equal NASA's PSI-25 cells", not b2bad, str(b2bad[:5]))


# ---------- 2b. Scenario Check counts, computed independently ----------
# Same published rule as the page: inside = O2 within +-1.5 points AND pressure within +-1.5 psi; oxygen-only = O2 within
# the window where no pressure was recorded; omitted = no usable O2. Conversions: atm x 14.6959, mmHg x 0.0193368.
def solid_tests():
    out = []
    for r in B2:  # BASS-II: calibrated starting O2, no per-test pressure
        out.append((num(r["Calibrated initial O2 % by vol"]), None))
    for row in B1:  # BASS-I: O2 logged as a fraction (x100), pressure in atm
        o2 = row[26] * 100 if isinstance(row[26], (int, float)) and 0 < row[26] < 1 else None
        pa = row[27] if isinstance(row[27], (int, float)) else None
        out.append((o2, pa * 14.6959 if pa is not None else None))
    out += [(None, None)] * sum(SAF.values())  # SAFFIRE: approximate or no O2 -> omitted
    return out
def liquid_tests():
    out = []
    for r in FX:
        o2, mm = num(r["O initial ambient composition; mole fraction"]), num(r["Ambient pressure; mmHg"])
        out.append((o2 * 100 if o2 is not None else None, mm * 0.0193368 if mm else None))
    return out
def classify(tests, o2, psi):
    c = {"inside": 0, "partial": 0, "outside": 0, "omitted": 0}
    for to2, tp in tests:
        if to2 is None:
            c["omitted"] += 1
        elif tp is not None:
            c["inside" if abs(to2 - o2) <= 1.5 and abs(tp - psi) <= 1.5 else "outside"] += 1
        else:
            c["partial" if abs(to2 - o2) <= 1.5 else "outside"] += 1
    return c
PRESETS = [(21, 14.7), (30, 10.2), (100, 4.3), (34, 10.4)]
SCEN = {(fam, o2, psi): classify(solid_tests() if fam == "solid" else liquid_tests(), o2, psi) for fam in ("solid", "liquid") for o2, psi in PRESETS}


# ---------- 3. rendered pages vs raw counts ----------
async def main():
    async with async_playwright() as p:
        try:
            b = await p.chromium.launch()
        except Exception:
            b = await p.chromium.launch(executable_path="/opt/pw-browsers/chromium")
        pg = await b.new_page(viewport={"width": 1280, "height": 900})
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        await pg.goto(SITE + "#/"); await pg.wait_for_timeout(600)
        bars = await pg.evaluate("""[...document.querySelectorAll('.qcard svg.chart')].map(s =>
            [...s.querySelectorAll('text')].map(t => t.textContent))""")

        def pairs(texts):
            out = {}
            for i in range(0, len(texts) - 1, 2):
                m = re.match(r"(\d+) ", texts[i + 1])
                if m:
                    out[texts[i]] = int(m.group(1))
            return out
        exp_bars, o2_bars, end_bars = (pairs(t) for t in bars[:3])
        check("Overview chart 1: records per experiment = NASA rows", exp_bars == EXP, str(exp_bars))
        want_bands = {f"{lo}-{hi} vol%": n for (lo, hi), n in zip(bands, band_counts)}
        check("Overview chart 2: BASS-II oxygen bands = NASA values", o2_bars == want_bands, f"{o2_bars} vs {want_bands}")
        check("Overview chart 3: FLEX test ends = NASA labels", end_bars == ends, f"{end_bars} vs {ends}")
        main_t = await pg.inner_text("main")
        check("Overview hero states the total", f"gathers {TOTAL} fire tests" in main_t)
        check("Overview FLEX note: methanol/heptane counts", f"{meth} methanol, {hept} heptane" in main_t)
        legend = await pg.evaluate("[...document.querySelectorAll('.hero-side .ev-item .ev-n')].map(e => e.textContent)")
        check("Legend: verified, machine-checked, unchecked", legend == [str(TOTAL), str(TOTAL), "0"], str(legend))
        check("Sign-off box: all records signed", f"{TOTAL} of {TOTAL}" in await pg.inner_text(".signoff-box"))
        rows = await pg.evaluate("[...document.querySelectorAll('table.methods tbody tr')].map(tr => [tr.cells[0].textContent, tr.cells[1].textContent])")
        want_rows = [["BASS-II", str(EXP["BASS-II"])], ["BASS-I", str(EXP["BASS-I"])], ["FLEX", str(EXP["FLEX"])], ["SAFFIRE", str(sum(SAF.values()))]]
        check("Methods table record counts", rows == want_rows, str(rows))
        check("Why-this-matters card: 3 fires + 3 spinoffs with NASA links", await pg.locator("#wm-h ~ .grid li").count() == 6 and
              await pg.locator("#wm-h ~ .grid li a[href*='nasa.gov']").count() == 6)
        await pg.goto(SITE + "#/explorer"); await pg.wait_for_timeout(800)
        check("Explorer lists every record", await pg.locator("table.records tbody tr.row").count() == TOTAL)
        await pg.goto(SITE + "#/investigations"); await pg.wait_for_timeout(600)
        check("Investigations page shows 24", "Showing 24 of 24" in await pg.inner_text("main"))

        scen_bad = []
        for (fam, o2, psi), want in SCEN.items():
            q = f"family={fam}&o2={o2}&psi={psi}" + ("&fuel=&diluent=" if fam == "liquid" else "")
            await pg.goto(SITE + "#/scenario/" + q); await pg.wait_for_timeout(500)
            v = await pg.inner_text(".verdict")
            got = {k: int(m.group(1)) if (m := re.search(r"(\d+) " + pat, v)) else None for k, pat in
                   [("inside", "inside the window"), ("partial", "oxygen-only"), ("outside", "outside the window"), ("omitted", "omitted")]}
            if got != want:
                scen_bad.append((q, got, want))
        check(f"Scenario Check verdict counts = independent count, {len(SCEN)} presets x fuel families", not scen_bad, str(scen_bad[:3]))

        # random record audit: NASA values on the record page equal the cells in NASA's file
        rnd = random.Random(628)
        by_exp = {}
        for r in D["records"]:
            by_exp.setdefault(r["experiment"], []).append(r)
        sample = []
        for e, L in sorted(by_exp.items()):
            sample += L if os.environ.get("AUDIT_ALL") else rnd.sample(L, min(len(L), 7))  # AUDIT_ALL=1: every record
        raw = {"PSI-25_experimental_table_BASS-II.csv": b2, "PSI-69_experimental_table_FLEX.csv": fx,
               "PSI-98_experimental_table_SAFFIRE-I.csv": rows_csv("PSI-98_experimental_table_SAFFIRE-I.csv"),
               "PSI-99_experimental_table_SAFFIRE-II.csv": rows_csv("PSI-99_experimental_table_SAFFIRE-II.csv"),
               "PSI-100_experimental_table_SAFFIRE-III.csv": rows_csv("PSI-100_experimental_table_SAFFIRE-III.csv")}
        bad = []
        for r in sample:
            await pg.goto(SITE + "#/experiment/" + r["id"]); await pg.wait_for_timeout(250)
            await pg.evaluate("document.querySelectorAll('main details').forEach(d => d.open = true)")  # collapsed sections count too
            t = norm(await pg.inner_text("main"))
            if r["source_file"] in raw:
                tab = raw[r["source_file"]]
                # every cell of NASA's row must be on the page, except SAFFIRE's camera video file names (not measurements)
                cells = [norm(c) for h, c in zip(tab[0], tab[int(r["source_row"]) - 1]) if not norm(h).lower().startswith("camera")]
                missing = [c for c in cells if c and c not in t]
            else:  # BASS-I spreadsheet: material and logged O2 fraction (shown x100)
                row = next(x for x in B1 if b1id(x) == r["id"])
                missing = [c for c in [norm(row[5])] if c not in t]
                o2 = row[26]
                if isinstance(o2, (int, float)) and 0 < o2 < 1:
                    shown = f"{o2 * 100:.2f}".rstrip("0").rstrip(".")
                    if shown not in t:
                        missing.append("O2 " + shown)
            if missing:
                bad.append((r["id"], missing[:3]))
            if "628 Aerospace team" not in t:
                bad.append((r["id"], ["sign-off line"]))
        check(f"record audit: {len(sample)} random records show NASA's exact cell values and the sign-off", not bad, str(bad[:5]))
        check("no JS errors during the audit", not errs, str(errs[:3]))
        await b.close()

asyncio.run(main())
bad = [r for r in results if not r[1]]
print(f"\n{len(results) - len(bad)} / {len(results)} audit checks passed")
sys.exit(1 if bad else 0)
