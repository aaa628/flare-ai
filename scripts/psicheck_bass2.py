"""Compare data/bass2_draft.csv with NASA's own BASS-II spreadsheet in PSI (PSI-25 "Experimental table").

This is a second, independent NASA source for the same tests (the first is the report PDF). For each row it
compares the sample number, calibrated initial/final O2, initial/final CO2 and initial/final CO (the PSI table
has no raw-sensor O2 columns). Different ways of writing "no value" (blank, dashes, 'none', 'failed') count as
equal, and 'OR' equals '+OR' (over range). Everything else that differs is reported, never "fixed": where the
report and the spreadsheet disagree, the site shows both.

Writes one column, psi_check ("agrees: ..." or "DIFFERS: ..."); every other column is preserved.
Usage: python scripts/psicheck_bass2.py
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "bass2_draft.csv"
PSI = ROOT / "data" / "source" / "psi" / "PSI-25_experimental_table_BASS-II.csv"
PAIRS = [("sample_no", "Sample #"),
         ("o2_cal_initial", "Calibrated initial O2 % by vol"), ("o2_cal_final", "Calibrated final O2 % by vol"),
         ("co2_initial", "Initial CO2 % by vol"), ("co2_final", "Final CO2 % by vol"),
         ("co_initial_ppm", "Initial CO (ppm)"), ("co_final_ppm", "Final CO (ppm)")]
LABEL = {"sample_no": "sample no.", "o2_cal_initial": "calibrated O2 start", "o2_cal_final": "calibrated O2 end",
         "co2_initial": "CO2 start", "co2_final": "CO2 end", "co_initial_ppm": "CO start", "co_final_ppm": "CO end"}


def norm(s):
    s = " ".join((s or "").split()).replace("–", "-").replace("−", "-")
    if re.fullmatch(r"-*|none|failed", s, re.I):
        return ""
    if s.upper() in ("OR", "+OR"):
        return "+OR"
    try:
        return float(s)
    except ValueError:
        return s.lower()


def psi_table():
    with PSI.open(newline="", encoding="utf-8-sig") as f:
        rows = list(csv.reader(f))
    hdr = [" ".join(h.split()) for h in rows[0]]
    return {r[1].strip(): dict(zip(hdr, r)) for r in rows[1:] if len(r) > 1 and r[1].strip()}


def compare(rows):
    psi = psi_table()
    out = {}
    for r in rows:
        sid = r["id"].split("-")[1]
        p = psi.get(sid)
        if p is None:
            out[r["id"]] = "DIFFERS: test not in NASA's PSI table"
            continue
        diffs = [f"{LABEL[a]}: report {r[a] or 'blank'}, PSI table {p[b].strip() or 'blank'}"
                 for a, b in PAIRS if norm(r[a]) != norm(p[b])]
        out[r["id"]] = ("DIFFERS: " + "; ".join(diffs)) if diffs else \
            "agrees: NASA PSI table (PSI-25) has the same sample no., calibrated O2, CO2 and CO"
    return out


def main():
    with CSV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        fields, rows = list(rd.fieldnames), list(rd)
    if "psi_check" not in fields:
        fields.insert(fields.index("raw_text"), "psi_check")
    res = compare(rows)
    for r in rows:
        r["psi_check"] = res[r["id"]]
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    bad = {k: v for k, v in res.items() if not v.startswith("agrees")}
    print(f"{len(rows) - len(bad)} of {len(rows)} rows agree with NASA's PSI table")
    for k, v in bad.items():
        print(" ", k, v)


if __name__ == "__main__":
    main()
