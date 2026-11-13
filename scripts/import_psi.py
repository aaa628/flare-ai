"""Import test records from NASA Physical Sciences Informatics (PSI) data files in data/source/psi/.

Every value is copied as stored in NASA's file (strings untouched; spreadsheet numbers written in their shortest
form, long computed decimals rounded to 4 places and marked). Nothing is invented: a blank cell stays blank.
Every record carries the file name and row it came from.

Writes:
  data/bass1_psi.csv        BASS (BASS-I), PSI-26 "As Run Test Matrix" spreadsheet, sheet "as run matrix"
  data/saffire_psi.csv      SAFFIRE-I/II/III, PSI-98/99/100 "Experimental table" CSVs
  data/bass2_psi_extra.csv  BASS-II tests that are in PSI-25's table but not in the NASA report's Appendix A (O20-O22)
  data/flex_psi.csv         FLEX (Flame Extinguishment Experiment), PSI-69 "Experimental table" CSV (Windows-1252 encoded)

The same functions are used by build_site_data.py to re-read the source files and confirm each CSV row still
equals its source cells (rows edited by hand drop to "unchecked").
Usage: python scripts/import_psi.py      (needs openpyxl)
"""
import csv
import datetime as dt
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source" / "psi"
OUT = {"bass1": ROOT / "data" / "bass1_psi.csv",
       "saffire": ROOT / "data" / "saffire_psi.csv",
       "bass2x": ROOT / "data" / "bass2_psi_extra.csv",
       "flex": ROOT / "data" / "flex_psi.csv"}
COLS = ["id", "experiment", "pi", "source_id", "source_file", "source_row", "material_raw", "flow_mode",
        "airflow_raw", "o2_raw", "o2_note", "o2_vol_pct", "outcome_raw", "qc_flag", "observation", "fields_json",
        "verified_by", "verified_date", "verifier_notes"]
DATA_COLS = [c for c in COLS if not c.startswith("verified")]  # compared with the source on every build


def show(v):
    """A spreadsheet cell as text, without inventing precision."""
    if v is None:
        return ""
    if isinstance(v, (dt.datetime, dt.date)):
        return v.strftime("%Y-%m-%d")
    if isinstance(v, float):
        if v.is_integer():
            return str(int(v))
        s = repr(v)
        return s if len(s.split(".")[1]) <= 4 else f"{v:.4f} (rounded)"
    return " ".join(str(v).split())


def pct(frac_text):
    """O2 logged as a fraction (0.221) -> vol% (22.1). Only for plain numbers; returns '' otherwise."""
    try:
        f = float(frac_text.replace(" (rounded)", ""))
    except ValueError:
        return ""
    return f"{f * 100:.2f}".rstrip("0").rstrip(".") if 0 < f < 1 else ""


def bass1_rows():
    import openpyxl
    path = SRC / "PSI-26_as_run_test_matrix_BASS.xlsx"
    ws = openpyxl.load_workbook(path, data_only=True)["as run matrix"]
    hdr = [show(c) for c in next(ws.iter_rows(min_row=3, max_row=3, values_only=True))]
    out = []
    for n, row in enumerate(ws.iter_rows(min_row=4, values_only=True), start=4):
        r = [show(c) for c in row] + [""] * 40
        asrun, test, sample, mat = r[2], r[3], r[4], r[5]
        if not (asrun.isdigit() and test and mat):  # skips SETUP, STOW, soot cleaning, notes
            continue
        fields = [[hdr[i], r[i]] for i in (0, 1, 4, 6, 7, 8, 9, 10, 13, 14, 25, 26, 27, 28) if r[i]]
        out.append({
            "id": f"BASSI-{asrun}-{test}", "experiment": "BASS-I", "source_id": "PSI-26",
            "source_file": path.name + ', sheet "as run matrix"', "source_row": str(n),
            "material_raw": mat, "flow_mode": "", "airflow_raw": r[10],
            "o2_raw": r[26], "o2_note": "O2 as logged under “ISS environment” in the as-run matrix (fraction by volume); vol% = fraction × 100",
            "o2_vol_pct": pct(r[26]), "observation": r[29], "fields_json": json.dumps(fields, ensure_ascii=False)})
    return out


def read_csv(name, encoding="utf-8-sig"):
    with (SRC / name).open(newline="", encoding=encoding, errors="replace") as f:
        return list(csv.reader(f))


def flex_rows():
    """FLEX (PSI-69): one row per droplet-combustion test on the ISS. NASA's file is Windows-1252 encoded; its
    en dash (\u2013) marks "no value" and is kept as printed. Headers are kept exactly as NASA wrote them."""
    name = "PSI-69_experimental_table_FLEX.csv"
    rows = read_csv(name, encoding="cp1252")
    hdr = [" ".join(h.split()) for h in rows[0]]
    ids = [r[1].strip() for r in rows[1:] if len(r) > 1]
    out = []
    for n, r in enumerate(rows[1:], start=2):
        r = [" ".join(c.split()) for c in r] + [""] * 20
        if not r[0]:
            continue
        col = dict(zip(hdr, r))
        flags = []
        if col["Ambient pressure; mmHg"] in ("0", "0.0"):
            flags.append("pressure_printed_zero")
        if ids.count(r[1]) > 1:
            flags.append("duplicate_identifier")
        o2 = col["O initial ambient composition; mole fraction"]
        try:
            o2pct = f"{float(o2) * 100:.2f}".rstrip("0").rstrip(".")
        except ValueError:
            o2pct = ""
        fields = [[h, v] for h, v in col.items() if v and h not in ("FLEX Test #", "Fuel", "Test end")]
        out.append({
            "id": "FLEX-" + r[0], "experiment": "FLEX", "pi": "", "source_id": "PSI-69", "source_file": name,
            "source_row": str(n), "material_raw": col["Fuel"] + " droplet", "flow_mode": "", "airflow_raw": "",
            "o2_raw": o2, "o2_note": "O2 mole fraction of the ambient gas (NASA header: \u201cO initial ambient composition; mole fraction\u201d); \u00d7100 shown as mole %",
            "o2_vol_pct": o2pct, "outcome_raw": col["Test end"], "qc_flag": ";".join(flags), "observation": "",
            "fields_json": json.dumps(fields, ensure_ascii=False)})
    return out


def saffire_rows():
    out = []
    for name, exp, sid in [("PSI-98_experimental_table_SAFFIRE-I.csv", "SAFFIRE-I", "PSI-98"),
                           ("PSI-99_experimental_table_SAFFIRE-II.csv", "SAFFIRE-II", "PSI-99"),
                           ("PSI-100_experimental_table_SAFFIRE-III.csv", "SAFFIRE-III", "PSI-100")]:
        rows = read_csv(name)
        hdr = [" ".join(h.split()).replace("?-g", "µg (printed as ?-g)") for h in rows[0]]
        notes = [" ".join(r[0].split()) for r in rows[1:] if r and r[0].lower().startswith("note")]
        prev_mat = ""
        for n, r in enumerate(rows[1:], start=2):
            r = [" ".join(c.split()) for c in r] + [""] * 20
            if not r[0] or "/" in r[0] or r[0].lower().startswith("note"):
                continue  # flow-visualisation rows and notes
            col = {h: r[i] for i, h in enumerate(hdr) if h}
            mat = r[1] or ("not stated in NASA's file (row above: " + prev_mat + ")" if prev_mat else "")
            prev_mat = r[1] or prev_mat
            o2 = next((v for h, v in col.items() if h.lower().startswith("percent o2")), "")
            direction = next((v for h, v in col.items() if h.lower().startswith(("flow direction", "direction"))), "")
            air = next((v for h, v in col.items() if h.lower().startswith("air flow")), "")
            fields = [[h, v] for h, v in col.items() if v and not h.lower().startswith(("sample number", "material", "camera"))]
            fields += [["Note in NASA's file", t] for t in notes]
            out.append({
                "id": f"{exp.replace('-', '')}-{r[0]}", "experiment": exp, "source_id": sid,
                "source_file": name, "source_row": str(n), "material_raw": mat, "flow_mode": direction,
                "airflow_raw": air, "o2_raw": o2,
                "o2_note": "O2 as printed in NASA's table" if o2 else "No O2 value in NASA's table",
                "o2_vol_pct": "", "observation": "", "fields_json": json.dumps(fields, ensure_ascii=False)})
    return out


def bass2_extra_rows(known_ids):
    name = "PSI-25_experimental_table_BASS-II.csv"
    rows = read_csv(name)
    hdr = [" ".join(h.split()) for h in rows[0]]
    out = []
    for n, r in enumerate(rows[1:], start=2):
        r = [" ".join(c.split()) for c in r] + [""] * 20
        if not r[1] or "BASSII-" + r[1] in known_ids:
            continue
        col = dict(zip(hdr, r))
        fields = [[h, v] for h, v in col.items() if v and h not in ("PI", "Test #", "Fuel Sample Material")]
        out.append({
            "id": "BASSII-" + r[1], "experiment": "BASS-II", "pi": col["PI"], "source_id": "PSI-25", "source_file": name,
            "source_row": str(n), "material_raw": col["Fuel Sample Material"], "flow_mode": "",
            "airflow_raw": col.get("Air display", ""), "o2_raw": col.get("Calibrated initial O2 % by vol", ""),
            "o2_note": "Calibrated initial O2 (vol%) from NASA's PSI table; this test is not in the report's Appendix A",
            "o2_vol_pct": col.get("Calibrated initial O2 % by vol", ""), "observation": "",
            "fields_json": json.dumps(fields, ensure_ascii=False)})
    return out


def bass2_known_ids():
    with (ROOT / "data" / "bass2_draft.csv").open(newline="", encoding="utf-8") as f:
        return {r["id"] for r in csv.DictReader(f)}


def expected():
    return {"bass1": bass1_rows(), "saffire": saffire_rows(), "bass2x": bass2_extra_rows(bass2_known_ids()), "flex": flex_rows()}


def write(key, rows):
    """Write rows, keeping any verified_* values a person already entered for the same id."""
    old = {}
    if OUT[key].exists():
        with OUT[key].open(newline="", encoding="utf-8") as f:
            old = {r["id"]: r for r in csv.DictReader(f)}
    ids = [r["id"] for r in rows]
    assert len(ids) == len(set(ids)), "duplicate ids in " + key
    with OUT[key].open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=COLS)
        w.writeheader()
        for r in rows:
            keep = old.get(r["id"], {})
            w.writerow({**{c: "" for c in COLS}, **r,
                        **{c: keep.get(c, "") for c in ("verified_by", "verified_date", "verifier_notes")}})


def main():
    for key, rows in expected().items():
        write(key, rows)
        print(f"{OUT[key].relative_to(ROOT)}: {len(rows)} rows")


if __name__ == "__main__":
    main()
