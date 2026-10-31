"""Independent automated cross-check of data/bass2_draft.csv against the report text.

WHAT THIS IS: a machine consistency check. It does NOT replace a person comparing rows with the
NASA PDF. It never writes verified_by / verified_date; those stay human-only.

Checks (a row must pass ALL to be marked machine-checked; any doubt -> left for a human, with the reason):
  1. TABLE/PAGE: the row's source_page lies in the page range of the Appendix A table for its
     investigator letter. Page ranges come from a fresh scan of table headings in the source text
     (independent of the row parser).
  2. TOKENS: re-tokenising raw_text, the 8 gas fields are exactly the 8 consecutive printed tokens
     that immediately precede the observation, and the observation is exactly the rest of the row.
     (A blank field must correspond to a printed dash.) Also the test ID and sample number are printed in the row.
  3. ALIGNMENT: calibrated - raw starting O2 lies in 0.2..2.5 vol% (in this report it is ~1.0 for
     nearly every row, so a shifted column breaks it). This check does not use the parser at all.
  4. RANGES: starting O2 10..25 vol%, CO2 0..6 vol%, CO >= -5 ppm (tiny negatives are instrument offset as printed), all eight readings numeric.
  5. NO FLAGS: no qc_flag, parse_ok == "yes".

Rows that fail ONLY the soft checks (3, 4, 5: flags, dashes/non-numeric NASA entries, unusual offset) can still pass
if data/ai_review_bass2.csv has a row-by-row review finding for them. They must still pass the strict text checks
(1, 2, test id, sample number), so an edited row still fails. Their flags stay on the row and on the site.

Writes auto_checked_by / auto_checked_date / auto_check_notes only; every other column is preserved.
Safe to re-run. Usage: python scripts/crosscheck_bass2.py
"""
import csv
import re
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "bass2_draft.csv"
SRC = ROOT / "data" / "source" / "TM-20210011385.txt"
BY = "Claude (automated cross-check; no human PDF comparison)"
AUTO_COLS = ["auto_checked_by", "auto_checked_date", "auto_check_notes"]
LETTER_TABLE = {"B": 1, "F": 2, "P": 3, "M": 4, "O": 5, "T": 6}
PAGE_RE = re.compile(r"^NASA/TM-20210011385\s+(\d+)")
TABLE_RE = re.compile(r"^TABLE A\.(\d)\.")
DASH = re.compile(r"^-+$|^none$", re.I)
REVIEW = ROOT / "data" / "ai_review_bass2.csv"


def load_review():
    if not REVIEW.exists():
        return {}
    with REVIEW.open(newline="", encoding="utf-8") as f:
        return {r["id"]: r for r in csv.DictReader(f) if r.get("finding", "").strip()}


def num(s):
    s = (s or "").replace("–", "-").replace("−", "-").strip()
    return float(s) if re.fullmatch(r"-?\d+(\.\d+)?", s) else None


def table_pages():
    """{table number: (first page, last page)}: pages on which that table's own headings
    ("TABLE A.k.-..." and "TABLE A.k.-Concluded") appear in Appendix A of the source text."""
    lines = SRC.read_text(errors="replace").splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("Appendix A.\u2014Test Matrices") and i > 3000)
    end = next(i for i, l in enumerate(lines) if i > start and l.startswith("Appendix B.\u2014"))
    page = None
    for k in range(start, 0, -1):  # page in force at the start of Appendix A
        m = PAGE_RE.match(lines[k])
        if m:
            page = int(m.group(1))
            break
    seen = {}
    for i in range(start, end):
        m = PAGE_RE.match(lines[i])
        if m:
            page = int(m.group(1))
        t = TABLE_RE.match(lines[i])
        if t:
            seen.setdefault(int(t.group(1)), []).append(page)
    return {k: (min(v), max(v)) for k, v in sorted(seen.items())}


def check(row, spans, review=None):
    """Returns (problems, offset). review: dict from load_review(); None loads the file, {} = strict mode."""
    if review is None:
        review = load_review()
    problems, hard = [], []
    letter = re.match(r"BASSII-([A-Z])", row["id"]).group(1)
    # 1. table / page
    try:
        pg = int(row["source_page"])
        lo, hi = spans[LETTER_TABLE[letter]]
        if not lo <= pg <= hi:
            hard.append(f"page {pg} outside Table A.{LETTER_TABLE[letter]} pages {lo}-{hi}")
    except (ValueError, KeyError):
        hard.append("page/table could not be checked")
    # 5. flags first (cheap)
    if row["qc_flag"].strip():
        problems.append("has qc_flag: " + row["qc_flag"])
    if row["parse_ok"] != "yes":
        problems.append("parse_ok=" + row["parse_ok"])
    # 4. numeric ranges
    keys = ["o2_cal_initial", "o2_cal_final", "o2_raw_initial", "o2_raw_final",
            "co2_initial", "co2_final", "co_initial_ppm", "co_final_ppm"]
    v = {k: num(row[k]) for k in keys}
    blank = [k for k in keys if v[k] is None]
    if blank:
        problems.append("non-numeric/blank: " + ",".join(blank))
    else:
        if not 10 <= v["o2_cal_initial"] <= 25:
            problems.append("starting O2 out of 10-25")
        if not (0 <= v["co2_initial"] <= 6 and 0 <= v["co2_final"] <= 8):
            problems.append("CO2 out of range")
        if v["co_initial_ppm"] < -5 or v["co_final_ppm"] < -5:  # small negatives are sensor offset, as printed
            problems.append("CO below -5 ppm")
        # 3. alignment invariant
        off = v["o2_cal_initial"] - v["o2_raw_initial"]
        if not 0.2 <= off <= 2.5:
            problems.append(f"cal-raw starting O2 offset {off:.1f} outside 0.2-2.5")
    # 2. token partition
    tokens = row["raw_text"].split()
    expected = [row[k] for k in keys]
    obs = " ".join(row["observation"].split())
    found = False
    for k in range(len(tokens) - 7):
        win = tokens[k:k + 8]
        if all((DASH.match(t) if e == "" else t == e) for e, t in zip(expected, win)) and " ".join(tokens[k + 8:]) == obs:
            found = True
            break
    if not found:
        hard.append("gas fields/observation do not partition the printed row tail")
    short = row["id"].split("-")[1]
    if short not in tokens:
        hard.append("test id not printed in row text")
    if row["sample_no"] not in tokens:
        hard.append("sample number not printed in row text")
    if not obs:
        hard.append("empty observation")
    off = (v["o2_cal_initial"] - v["o2_raw_initial"]) if not blank else None
    if not hard and problems and row["id"] in review:
        return [], off  # soft issues only, explained by a row-by-row review finding
    return hard + problems, off


def main():
    spans = table_pages()
    review = load_review()
    with CSV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        fields, rows = list(rd.fieldnames), list(rd)
    for c in AUTO_COLS:
        if c not in fields:
            fields.insert(fields.index("raw_text") if "raw_text" in fields else len(fields), c)
    today = date.today().isoformat()
    n_ok = 0
    for r in rows:
        problems, off = check(r, spans, review)
        if problems:
            r["auto_checked_by"], r["auto_checked_date"] = "", ""
            r["auto_check_notes"] = "NEEDS HUMAN CHECK: " + "; ".join(problems)
        else:
            n_ok += 1
            r["auto_checked_by"], r["auto_checked_date"] = BY, today
            if r["id"] in review and check(r, spans, {})[0]:
                r["auto_check_notes"] = ("table/page ok; row tail tokens match source; row-by-row review: "
                                         + review[r["id"]]["finding"])
            else:
                r["auto_check_notes"] = ("table/page ok; row tail tokens match source; "
                                         f"calibrated-raw starting O2 offset {off:.1f} vol%")
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print(f"table page spans: {spans}")
    print(f"{n_ok} of {len(rows)} rows machine-checked; {len(rows) - n_ok} left for a human")
    reasons = {}
    for r in rows:
        if r["auto_check_notes"].startswith("NEEDS"):
            for p in r["auto_check_notes"][len("NEEDS HUMAN CHECK: "):].split("; "):
                key = re.sub(r"[\d.]+", "#", p)[:60]
                reasons[key] = reasons.get(key, 0) + 1
    for k, n in sorted(reasons.items(), key=lambda t: -t[1]):
        print(f"  {n:3d}  {k}")


if __name__ == "__main__":
    main()
