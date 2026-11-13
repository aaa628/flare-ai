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


BRIEF_FACTS = [
    ("brief-moon", "Challenge brief: Moon base and rover atmosphere",
     "The intermediate oxygen concentration used on the Moon will likely be 30% or greater, with a corresponding pressure of 10.2 psi or less. "
     "Spacesuits are filled with 100% oxygen to 4.3 psi; Earth's sea-level pressure is 14.7 psi."),
    ("brief-partial-g", "Challenge brief: partial gravity",
     "There is currently no partial-gravity combustion data available in PSI. Partial gravity was mimicked in ACME E-FIELD Flames through an electric field. "
     "Microgravity and normal-gravity results could bound what occurs at intermediate gravity levels."),
    ("brief-pillars", "Challenge brief: prevention, detection, suppression",
     "NASA's spacecraft fire safety work is focused on prevention, detection, and suppression. Flammability studies of solid materials: BASS, BASS-II, "
     "Saffire-I, -II, -III. Detection: SAME and SAME-R. Suppression: FLEX, by diluting the chamber atmosphere with carbon dioxide and helium."),
    ("brief-scope", "Challenge brief: scope",
     "Fire safety involving rockets and propellants is generally beyond the scope of the research available in the PSI database."),
]


def write_corpus(records, investigations):
    """Search corpus for the Intelligence Lab server function (netlify/functions/ask/corpus.mjs). Generated; never hand-edit.
    Each document carries the site route and source label it is cited with. Only shown (checked) records are included."""
    docs = []
    for r in records:
        if r["level"] == "none":
            continue
        fields = r.get("fields") or []
        vals = "; ".join(f"{k}: {v}" for k, v in fields[:18]) if fields else (
            f"calibrated O2 {r.get('o2_cal_initial','')} -> {r.get('o2_cal_final','')} vol%; raw O2 {r.get('o2_raw_initial','')} -> {r.get('o2_raw_final','')}; "
            f"CO2 {r.get('co2_initial','')} -> {r.get('co2_final','')} vol%; CO {r.get('co_initial_ppm','')} -> {r.get('co_final_ppm','')} ppm")
        text = (f"{r['experiment']} test {r['id']}. Material: {r.get('material_raw','')}. Flow direction: {r.get('flow_mode') or 'not stated'}. "
                f"Values as recorded: {vals}. " + (f"NASA test end: {r['outcome_raw']}. " if r.get("outcome_raw") else "") +
                (f"Test-log note: {r['observation']} " if r.get("observation") else "") +
                (f"Flags: {r['qc_flag']}. " if r.get("qc_flag") else "") + f"Check level: {r['level']} (no person has signed it)." * (r["level"] == "machine"))
        src = (f"NASA/TM-20210011385, Appendix A, report page {r.get('source_page')}" if r.get("raw_text")
               else f"NASA PSI {r.get('source_id')}: {r.get('source_file','').split(',')[0]}, row {r.get('source_row')}")
        docs.append({"id": r["id"], "kind": "record", "title": f"{r['experiment']} {r['id']}: {r.get('material_raw','')}",
                     "route": "#/experiment/" + r["id"], "source": src, "text": text[:1600]})
    for v in investigations:
        name = v.get("investigationAcronym") or v["title"]
        c = v.get("curated", {})
        conds = []
        for t in v.get("table_summaries", []):
            if t.get("o2_range_pct"):
                conds.append(f"O2 {t['o2_range_pct'][0]}-{t['o2_range_pct'][1]}% ({t.get('o2_meaning')})")
            if t.get("p_range_psi"):
                conds.append(f"pressure {t['p_range_orig'][0]}-{t['p_range_orig'][1]} {t['p_unit']} = {t['p_range_psi'][0]}-{t['p_range_psi'][1]} psi")
            if t.get("joint"):
                conds.append(f"{t['joint']} tests with O2 >= 30% at <= 10.2 psi")
        summary = (f"{name} ({v['accession']}): {v['title']}. NASA PSI sub-area: {v.get('subResearchArea')}. Type: {v.get('projectType')}; platform: "
                   f"{v.get('flightProgram')}; hardware: {v.get('experimentHardware')}. Tests in NASA table: {v.get('n_tests')}. "
                   f"Conditions read from NASA's table: {'; '.join(conds) or 'none recorded'}. Flare AI labels (interpretation): fuel {c.get('fuel_class')} "
                   f"({c.get('fuel_examples')}); fire-safety area {c.get('pillar') or 'none'}; brief mention {c.get('brief_mention')}.")
        docs.append({"id": v["accession"], "kind": "investigation", "title": f"{name} ({v['accession']}) overview", "route": "#/investigation/" + v["accession"],
                     "source": f"NASA PSI {v['accession']} (DOI {v.get('doi')}) + Flare AI table summary", "text": summary[:1800]})
        for key, label in (("objective", "objective"), ("approach", "approach"), ("hypothesis", "hypothesis"), ("researchImpacts", "research impacts")):
            t = " ".join((v.get(key) or "").split())
            for i in range(0, min(len(t), 3000), 1000):
                docs.append({"id": f"{v['accession']}#{key}{i // 1000 or ''}", "kind": "nasa_text", "title": f"{name}: NASA's stated {label}",
                             "route": "#/investigation/" + v["accession"], "source": f"NASA PSI {v['accession']} description ({label})", "text": t[i:i + 1100]})
    for i, title, text in BRIEF_FACTS:
        docs.append({"id": i, "kind": "brief", "title": title, "route": "#/investigations", "source": "NASA Space Apps 2026 challenge brief (Details tab)", "text": text})
    out = ROOT / "netlify" / "functions" / "ask" / "corpus.mjs"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text("// GENERATED by scripts/build_site_data.py. Do not edit by hand.\nexport default " +
                   json.dumps(docs, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    print(f"wrote {out.relative_to(ROOT)}: {len(docs)} documents")


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
    # Investigation catalogue: all NASA PSI combustion investigations (metadata + table summaries), tables served too.
    tab_dir = ROOT / "site" / "sources" / "psi" / "tables"
    tab_dir.mkdir(parents=True, exist_ok=True)
    for f in (DATA / "source" / "psi" / "tables").iterdir():
        if f.is_file():
            shutil.copyfile(f, tab_dir / f.name)
    investigations = load("build_catalog").catalog()
    sources = read("sources.csv")
    n_ver = sum(1 for r in records if r["level"] == "human")
    n_mach = sum(1 for r in records if r["level"] == "machine")
    payload = {
        "records": records,
        "sources": sources,
        "investigations": investigations,
        "counts": {"records": len(records), "verified": n_ver, "machine": n_mach,
                   "unchecked": len(records) - n_ver - n_mach, "shown": n_ver + n_mach,
                   "sources": len(sources), "pdf_match": sum(1 for r in records if r["pdf"]),
                   "psi_agree": sum(1 for r in records if r.get("psi_check", "").startswith("agrees")),
                   "psi_differ": sum(1 for r in records if r.get("psi_check", "").startswith("DIFFERS")),
                   "investigations": len(investigations),
                   "experiments": {e: sum(1 for r in records if r["experiment"] == e)
                                   for e in sorted({r["experiment"] for r in records})}},
    }
    if stale:
        print("WARNING: edited after the automated check, downgraded to unchecked:", ", ".join(stale))
    write_corpus(records, investigations)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(
        "// GENERATED by scripts/build_site_data.py. Do not edit by hand.\n"
        "window.FLARE_DATA = " + json.dumps(payload, ensure_ascii=False, indent=1) + ";\n",
        encoding="utf-8",
    )
    print(f"wrote {OUT.relative_to(ROOT)}: {payload['counts']}")


if __name__ == "__main__":
    main()
