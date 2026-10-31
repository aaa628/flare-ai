"""Build the investigation catalogue (all NASA PSI Combustion Science investigations) for the website.

Inputs (committed): data/source/psi/catalog/*.json (NASA PSI metadata, verbatim fields), data/source/psi/tables/*.csv
(NASA experiment tables, as served), data/investigations_curated.csv (our labels, each with its basis), and the BASS-I
records in data/bass1_psi.csv (the PSI-26 experiment table has no O2 or pressure column; the as-run matrix does).

Test conditions are read ONLY from the columns listed in COND below; each value keeps its source column and unit.
Unit conversions (fraction -> %, mmHg/atm/bar -> psi) are arithmetic only. Anything that is not a plain number is
reported as "not parsed" with the text NASA printed. Exploration-atmosphere thresholds come from the challenge brief:
O2 >= 30 % and pressure <= 10.2 psi (planned Moon base and pressurized rovers).
"""
import csv
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CAT = ROOT / "data" / "source" / "psi" / "catalog"
TAB = ROOT / "data" / "source" / "psi" / "tables"
PSI_PER_UNIT = {"psi": 1.0, "atm": 14.6959, "bar": 14.5038, "mmHg": 0.0193368}
O2_MIN, P_MAX = 30.0, 10.2

# table file -> (o2 column, o2 unit, o2 meaning, pressure column, pressure unit, airflow column)
COND = {
    "PSI-25_Experimental table_BASS-II.csv": ("Calibrated initial O2 % by vol", "percent", "chamber O2 at start", None, None, "Air display"),
    "PSI-69_Experimental table_FLEX.csv": ("O initial ambient composition; mole fraction", "fraction", "ambient O2 (header reads “O”)", "Ambient pressure; mmHg", "mmHg", None),
    "PSI-68_Experimental table_Flex2.csv": ("Oxygen Mole Fraction", "fraction", "PLANNED ambient O2 (test matrix, not results)", "Ambient Pressure (atm)", "atm", "Flow Velocity (cm/s)"),
    "PSI-39_Experimental table_CFI.csv": ("Oxygen", "fraction", "ambient O2", "Pressure", "atm", None),
    "PSI-10_Experimental table_Flame Design_Normal Flame.csv": ("XO2 (init)", "fraction", "ambient O2 (normal flames)", "pinit (atm)", "atm", None),
    "PSI-10_Experimental table_Flame Design_Inverse Flame.csv": ("XO2", "fraction", "O2 in the burner flow (inverse flames: the room holds fuel)", "pinit (atm)", "atm", None),
    "PSI-159_Experimental table_CFI-G_Normal Flames.csv": ("XO2 before test", "fraction", "ambient O2 (normal flames)", "approx p (bar)", "bar", None),
    "PSI-159_Experimental table_CFI-G_Inverse Flames.csv": ("XO2", "fraction", "O2 in the burner flow (inverse flames: the room holds fuel)", "approx p (bar)", "bar", None),
    "PSI-20_Experimental table_ACME BRE.csv": ("Oxygen Conc (percent)", "percent", "ambient O2", None, None, None),
    "PSI-23_Experimental table_ACME s-Flame.csv": ("Atmosphere*", "approx-text", "ambient O2, approximate (\u201c~21% O2 with N2\u201d as printed)", None, None, None),
    "PSI-98_Experimental table_SAFFIRE-1.csv": ("Percent O2", "percent", "O2, approximate as printed", None, None, "Air Flow (cm/s)"),
    "PSI-99_Experimental table_SAFFIRE-2.csv": ("Percent O2 (Note 1)", "percent", "O2 derived from CO2 (NASA Note 1)", None, None, "Air Flow (cm/s)"),
    "PSI-100_Experimental table_SAFFIRE-3.csv": (None, None, None, None, None, "Air Flow"),
    "PSI-102_Experimental table_SAME.csv": (None, None, None, None, None, "Air Flow (cm/s)"),
    "PSI-101_Experimental table_SAME-R.csv": (None, None, None, None, None, "Inlet velocity (cm/s)"),
    "PSI-107_Experimental table_Spice.csv": (None, None, None, None, None, "Air Rate (cm/s)"),
}


def read_table(name):
    raw = (TAB / name).read_bytes()
    try:
        text, enc = raw.decode("utf-8-sig"), "utf-8"
    except UnicodeDecodeError:
        text, enc = raw.decode("cp1252"), "windows-1252"
    rows = [r for r in csv.reader(text.splitlines()) if any(c.strip() for c in r)]
    hdr = [" ".join(h.split()) for h in rows[0]]
    return hdr, [dict(zip(hdr, [" ".join(c.split()) for c in r])) for r in rows[1:]], enc


def numbers(text, unit):
    """Plain numbers in a cell ("21; 26.5; 34" -> three values). Returns ([], reason) if not plain."""
    t = (text or "").strip()
    if not t or re.fullmatch(r"[-–—]+|none|n/a", t, re.I):
        return [], None
    if re.fullmatch(r"\d+00%", t):
        return [], f"“{t}” (spreadsheet percent formatting, e.g. 21 shown as 2100%)"
    if unit == "approx-text":
        found = re.findall(r"~\s*(\d+(?:\.\d+)?)%\s*O2", t) or re.findall(r"~\s*(\d+(?:\.\d+)?)%", t)
        return ([float(x) for x in found], None) if found else ([], f"\u201c{t}\u201d")
    t2 = re.sub(r"\s*(atm|bar|mmHg|%)$", "", t).replace(" or ", " ").replace("or ", "")
    parts = [p.strip() for p in re.split(r"[;,]", t2) if p.strip()]
    if all(re.fullmatch(r"-?\d+(\.\d+)?", p) for p in parts):
        return [float(p) for p in parts], None
    return [], f"“{t}”"


def conditions(name, rows):
    o2c, o2u, o2m, pc, pu, airc = COND.get(name, (None,) * 6)
    out = {"table": name, "rows": len(rows), "o2_col": o2c, "o2_meaning": o2m, "p_col": pc, "p_unit": pu, "air_col": airc,
           "o2_pct": [], "p_psi": [], "p_orig": [], "unparsed": [], "joint": 0, "p_at_high_o2": []}
    for r in rows:
        o2s, ps = [], []
        if o2c:
            vals, why = numbers(r.get(o2c, ""), o2u)
            if why:
                out["unparsed"].append(f"{o2c}: {why}")
            o2s = [v * 100 if o2u == "fraction" else v for v in vals]
        if pc:
            vals, why = numbers(r.get(pc, ""), pu)
            if why:
                out["unparsed"].append(f"{pc}: {why}")
            ps = [v * PSI_PER_UNIT[pu] for v in vals if v > 0]
            if any(v == 0 for v in vals):
                out["unparsed"].append(f"{pc}: “0” (printed as 0; likely missing)")
            out["p_orig"] += [v for v in vals if v > 0]
        out["o2_pct"] += o2s
        out["p_psi"] += ps
        if o2s and ps and max(o2s) >= O2_MIN and "PLANNED" not in (o2m or ""):
            out["p_at_high_o2"].append(min(ps))
            if min(ps) <= P_MAX:
                out["joint"] += 1
    return out


def summarise(c):
    def rng(v, nd=1):
        return [round(min(v), nd), round(max(v), nd)] if v else None
    return {"table": c["table"], "rows": c["rows"], "o2_col": c["o2_col"], "o2_meaning": c["o2_meaning"],
            "o2_range_pct": rng(c["o2_pct"]), "o2_n": len(c["o2_pct"]), "p_col": c["p_col"], "p_unit": c["p_unit"],
            "p_range_orig": rng(c["p_orig"], 3), "p_range_psi": rng(c["p_psi"]), "p_n": len(c["p_psi"]), "air_col": c["air_col"],
            "joint": c["joint"], "p_min_psi_at_o2ge30": round(min(c["p_at_high_o2"]), 2) if c["p_at_high_o2"] else None,
            "high_o2_n": sum(1 for v in c["o2_pct"] if v >= O2_MIN),
            "unparsed": sorted(set(c["unparsed"]))[:6], "unparsed_n": len(c["unparsed"])}


def bass1_conditions():
    """BASS-I: O2 and pressure come from the as-run matrix (already imported to data/bass1_psi.csv)."""
    rows = list(csv.DictReader((ROOT / "data" / "bass1_psi.csv").open(encoding="utf-8")))
    o2, p = [], []
    for r in rows:
        try:
            o2.append(float(r["o2_vol_pct"]))
        except ValueError:
            pass
        for k, v in json.loads(r["fields_json"]):
            if k.lower().startswith("pressure"):
                try:
                    p.append(float(v.replace(" (rounded)", "")))
                except ValueError:
                    pass
    joint = 0  # BASS-I O2 never reached 30 %
    return {"table": "PSI-26_as_run_test_matrix_BASS.xlsx (sheet “as run matrix”)", "rows": len(rows),
            "o2_col": "O2 % by volume", "o2_meaning": "O2 logged as a fraction under “ISS environment”",
            "o2_range_pct": [round(min(o2), 1), round(max(o2), 1)] if o2 else None, "o2_n": len(o2),
            "p_col": "pressure, atm", "p_unit": "atm", "p_range_orig": [round(min(p), 3), round(max(p), 3)] if p else None,
            "p_range_psi": [round(min(p) * PSI_PER_UNIT["atm"], 1), round(max(p) * PSI_PER_UNIT["atm"], 1)] if p else None,
            "p_n": len(p), "air_col": "Air display", "joint": joint, "p_min_psi_at_o2ge30": None, "high_o2_n": 0, "unparsed": [], "unparsed_n": 0}


def catalog():
    cur = {r["accession"]: r for r in csv.DictReader((ROOT / "data" / "investigations_curated.csv").open(encoding="utf-8"))}
    out = []
    for f in sorted(CAT.glob("*.json"), key=lambda p: int(p.stem.split("-")[1])):
        m = json.loads(f.read_text(encoding="utf-8"))
        acc = m["accession"]
        tables = []
        for name in m.get("tables", []):
            hdr, rows, enc = read_table(name)
            s = summarise(conditions(name, rows))
            s["columns"] = [h for h in hdr if h]
            s["encoding"] = enc
            tables.append(s)
        if acc == "PSI-26":
            b = bass1_conditions()
            b["columns"] = ["(as-run matrix: 30 columns incl. O2 % by volume, pressure, atm, CO2, mm Hg, Fan display, Air display)"]
            b["encoding"] = "xlsx"
            tables.append(b)
        out.append({**m, "curated": cur.get(acc, {}), "table_summaries": tables,
                    "o2_max_pct": max([t["o2_range_pct"][1] for t in tables if t.get("o2_range_pct") and "PLANNED" not in (t.get("o2_meaning") or "")] or [None], key=lambda x: x or -1),
                    "p_min_psi": min([t["p_range_psi"][0] for t in tables if t.get("p_range_psi") and "PLANNED" not in (t.get("o2_meaning") or "")] or [None], key=lambda x: x if x is not None else 1e9),
                    "joint_tests": sum(t["joint"] for t in tables),
                    "high_o2_tests": sum(t["high_o2_n"] for t in tables if "PLANNED" not in (t.get("o2_meaning") or "")),
                    "p_min_psi_at_o2ge30": min([t["p_min_psi_at_o2ge30"] for t in tables if t.get("p_min_psi_at_o2ge30")] or [None], key=lambda x: x if x is not None else 1e9),
                    "n_tests": sum(t["rows"] for t in tables if not t["table"].startswith("PSI-26_as_run")) if acc != "PSI-26" else tables[-1]["rows"]})
    return out


if __name__ == "__main__":
    for i in catalog():
        print(i["accession"], (i["investigationAcronym"] or i["title"])[:28].ljust(28), "tests", i["n_tests"], "| O2 max", i["o2_max_pct"],
              "| p min psi", i["p_min_psi"], "| >=30% & <=10.2psi", i["joint_tests"], "| p at >=30%", i["p_min_psi_at_o2ge30"], "| unparsed", sum(t["unparsed_n"] for t in i["table_summaries"]))
