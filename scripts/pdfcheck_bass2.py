"""Compare every row of data/bass2_draft.csv with NASA's own PDF (NASA/TM-20210011385).

WHAT THIS IS: an automated comparison with the text layer of the official PDF, read with
pdftotext (poppler). This is a different extraction from data/source/TM-20210011385.txt, which the
extractor and the cross-check use. It is still a machine check, NOT a person signing off:
it never writes verified_by / verified_date.

For each row, all must hold:
  1. PAGE:     the row is printed on the report page given in source_page (PDF pages 111-121 = report pages 103-113).
  2. ROW:      exactly one table line starts with the test ID and sample number.
  3. READINGS: the 8 gas values are 8 consecutive tokens on that line (a blank = a printed dash), immediately
               followed by the first two words of the observation.
  4. MATERIAL: the material name is the text printed right after the sample number (spaces and line wraps ignored).
  5. NOTE:     the full observation text appears in the PDF row, word for word (spaces and line wraps ignored).

Writes one column, pdf_check ("match: ..." or "MISMATCH: ..."); every other column is preserved.
The PDF (49 MB) is not committed: it is downloaded to data/raw/ (git-ignored) when missing.
Usage: python scripts/pdfcheck_bass2.py      (needs pdftotext: poppler-utils)
"""
import csv
import re
import subprocess
import sys
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "bass2_draft.csv"
PDF = ROOT / "data" / "raw" / "TM-20210011385.pdf"
URL = "https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf"
FIRST, LAST = 111, 121  # PDF pages holding Tables A.1-A.6
DASH = re.compile(r"^-+$|^none$", re.I)
GAS = ["o2_cal_initial", "o2_cal_final", "o2_raw_initial", "o2_raw_final",
       "co2_initial", "co2_final", "co_initial_ppm", "co_final_ppm"]


def ensure_pdf():
    if not PDF.exists():
        PDF.parent.mkdir(parents=True, exist_ok=True)
        print("downloading", URL)
        urllib.request.urlretrieve(URL, PDF)
    return PDF


def pdf_text(mode):
    """[(report page, text)] for the table pages, using pdftotext -layout or -raw."""
    out = []
    for p in range(FIRST, LAST + 1):
        t = subprocess.run(["pdftotext", "-f", str(p), "-l", str(p), mode, str(PDF), "-"],
                           capture_output=True, text=True, check=True).stdout
        m = re.findall(r"NASA/TM-20210011385\s+(\d+)", t)
        out.append((int(m[-1]) if m else None, t))
    return out


def squash(s):
    return re.sub(r"\s+", "", s)


def compare(rows):
    layout = [(pp, l.split()) for pp, t in pdf_text("-layout") for l in t.splitlines()]
    stream = []  # raw-mode token stream for material names (they wrap over several lines)
    for pp, t in pdf_text("-raw"):
        stream += t.split()
    result = {}
    for r in rows:
        sid, smp = r["id"].split("-")[1], r["sample_no"]
        probs = []
        hits = [(pp, tk) for pp, tk in layout if sid in tk[:8] and smp in tk[:9]]
        if len(hits) != 1:
            result[r["id"]] = f"MISMATCH: {len(hits)} table lines start with {sid} {smp}"
            continue
        pp, tk = hits[0]
        if str(pp) != r["source_page"]:
            probs.append(f"printed on page {pp}, not {r['source_page']}")
        exp, obs0 = [r[k] for k in GAS], r["observation"].split()[:2]
        if not any(all((DASH.match(t) if e == "" else t == e) for e, t in zip(exp, tk[i:i + 8]))
                   and tk[i + 8:i + 10] == obs0 for i in range(len(tk) - 7)):
            probs.append("gas readings / observation start differ from the PDF line")
        idx = [i for i in range(len(stream) - 1) if stream[i] == sid and stream[i + 1] == smp]
        mat = squash(r["material_raw"])
        if not any(squash("".join(stream[i + 2:i + 30])).startswith(mat) for i in idx):
            probs.append("material name differs from the PDF")
        obs = squash(r["observation"])
        texts = [squash("".join(stream[i:i + 400])) for i in idx]
        if not obs or not any(t[m.start():].startswith(obs) for t in texts for m in re.finditer(re.escape(obs[:12]), t)):
            probs.append("observation text differs from the PDF")
        result[r["id"]] = ("MISMATCH: " + "; ".join(probs)) if probs else \
            f"match: NASA PDF text layer, report page {pp}, readings + material + full note ({date.today().isoformat()})"
    return result


def main():
    ensure_pdf()
    with CSV.open(newline="", encoding="utf-8") as f:
        rd = csv.DictReader(f)
        fields, rows = list(rd.fieldnames), list(rd)
    if "pdf_check" not in fields:
        fields.insert(fields.index("raw_text"), "pdf_check")
    res = compare(rows)
    for r in rows:
        r["pdf_check"] = res[r["id"]]
    with CSV.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)
    bad = [k for k, v in res.items() if not v.startswith("match")]
    print(f"{len(rows) - len(bad)} of {len(rows)} rows match NASA's PDF")
    for k in bad:
        print(" ", k, res[k])
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
