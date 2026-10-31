"""Build site/data/data.js from data/bass2_draft.csv and data/sources.csv.

Why data.js and not .json: browsers refuse fetch() on file:// pages, so a
plain JS file keeps the site working when index.html is double-clicked.

Every row gets one of three trust levels:
  human   : verified_by AND verified_date filled (a person compared the row with the NASA PDF)
  machine : passed scripts/crosscheck_bass2.py (an automated consistency check, NOT a human PDF check).
            The check is re-run here at build time, so an edited row silently drops to "none".
  none    : neither. Shown only in preview mode (index.html?preview=draft) under a loud warning banner.
The site shows human + machine rows by default, each labelled with its level.
Separately, r["pdf"] is True when the row matched NASA's PDF (scripts/pdfcheck_bass2.py). If the PDF and
pdftotext are available the comparison is re-run here; otherwise the stored pdf_check column is used.

Usage: python scripts/build_site_data.py
"""
import csv
import importlib.util
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
OUT = ROOT / "site" / "data" / "data.js"


def read(name):
    path = DATA / name
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def is_verified(row):
    return bool(row.get("verified_by", "").strip()) and bool(row.get("verified_date", "").strip())


def load_crosscheck():
    spec = importlib.util.spec_from_file_location("crosscheck_bass2", ROOT / "scripts" / "crosscheck_bass2.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def psi_records():
    """Records imported from NASA PSI files. Machine level only if every data column still equals the source file."""
    ip = load("import_psi")
    try:
        exp = ip.expected()
    except ImportError as err:  # openpyxl missing
        print("WARNING: cannot re-read PSI source files (" + str(err) + "); run: pip install openpyxl. PSI rows marked unchecked.")
        exp = None
    out = []
    for key, path in ip.OUT.items():
        rows = read(path.name)
        want = {r["id"]: r for r in exp[key]} if exp else {}
        for r in rows:
            src = want.get(r["id"])
            same = bool(src) and all(r.get(c, "") == src.get(c, "") for c in ip.DATA_COLS)
            r["verified"] = is_verified(r)
            r["machine"] = same and not r["verified"]
            r["level"] = "human" if r["verified"] else "machine" if r["machine"] else "none"
            r["auto_check_notes"] = (f"copied from NASA's PSI file {r['source_file']}, row {r['source_row']}; "
                                     "re-read at build time: every value equals the file") if same else \
                "differs from the NASA source file or could not be re-read"
            r["fields"] = json.loads(r.pop("fields_json") or "[]")
            r["pdf"] = False
            out.append(r)
    return out


def main():
    cc = load_crosscheck()
    spans = cc.table_pages()
    records = read("bass2_draft.csv")
    stale = []
    for r in records:
        r["verified"] = is_verified(r)
        claimed = bool(r.get("auto_checked_by", "").strip()) and bool(r.get("auto_checked_date", "").strip())
        still_ok = claimed and not cc.check(r, spans)[0]
        if claimed and not still_ok and not r["verified"]:
            stale.append(r["id"])
        r["machine"] = still_ok and not r["verified"]
        r["level"] = "human" if r["verified"] else "machine" if r["machine"] else "none"
    pdf_live = None
    try:
        pc_spec = importlib.util.spec_from_file_location("pdfcheck_bass2", ROOT / "scripts" / "pdfcheck_bass2.py")
        pc = importlib.util.module_from_spec(pc_spec)
        pc_spec.loader.exec_module(pc)
        if pc.PDF.exists():
            pdf_live = pc.compare(records)
    except Exception as err:  # e.g. no pdftotext installed: fall back to the stored column
        print("note: PDF comparison not re-run here:", err)
    psi_live = load("psicheck_bass2").compare(records)
    for r in records:
        if pdf_live is not None:
            r["pdf_check"] = pdf_live[r["id"]]
        r["pdf"] = r.get("pdf_check", "").startswith("match")
        r["psi_check"] = psi_live[r["id"]]
        r["experiment"], r["source_id"] = "BASS-II", "20210011385"
        r["source_file"] = f"Appendix A, report page {r['source_page']}"
    records += psi_records()
    # Serve copies of NASA's PSI source files with the site, so every record can open its exact source file
    # (also offline). They are CC0; the copies are byte-identical to data/source/psi/.
    psi_dir = ROOT / "site" / "sources" / "psi"
    psi_dir.mkdir(parents=True, exist_ok=True)
    for f in (DATA / "source" / "psi").iterdir():
        if f.is_file():
            shutil.copyfile(f, psi_dir / f.name)
    for r in records:
        if r.get("source_file") and r.get("source_id", "").startswith("PSI"):
            r["source_href"] = "sources/psi/" + r["source_file"].split(",")[0]
        elif r.get("source_page", "").isdigit():  # report page -> PDF page (report page 103 is PDF page 111)
            r["source_href"] = ("https://ntrs.nasa.gov/api/citations/20210011385/downloads/TM-20210011385.pdf#page="
                                + str(int(r["source_page"]) + 8))
    sources = read("sources.csv")
    n_ver = sum(1 for r in records if r["level"] == "human")
    n_mach = sum(1 for r in records if r["level"] == "machine")
    payload = {
        "records": records,
        "sources": sources,
        "counts": {"records": len(records), "verified": n_ver, "machine": n_mach,
                   "unchecked": len(records) - n_ver - n_mach, "shown": n_ver + n_mach,
                   "sources": len(sources), "pdf_match": sum(1 for r in records if r["pdf"]),
                   "psi_agree": sum(1 for r in records if r.get("psi_check", "").startswith("agrees")),
                   "psi_differ": sum(1 for r in records if r.get("psi_check", "").startswith("DIFFERS")),
                   "experiments": {e: sum(1 for r in records if r["experiment"] == e)
                                   for e in sorted({r["experiment"] for r in records})}},
    }
    if stale:
        print("WARNING: edited after the automated check, downgraded to unchecked:", ", ".join(stale))
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "// GENERATED by scripts/build_site_data.py. Do not edit by hand.\n"
        "window.FLARE_DATA = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)}: {payload['counts']}")


if __name__ == "__main__":
    main()
