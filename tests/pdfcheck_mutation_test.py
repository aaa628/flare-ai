"""Proves scripts/pdfcheck_bass2.py catches errors: corrupt every row in memory and require the PDF
comparison to reject each one. Needs the PDF in data/raw/ (the script downloads it) and pdftotext.
Run: python tests/pdfcheck_mutation_test.py"""
import csv, importlib.util, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("pc", ROOT / "scripts" / "pdfcheck_bass2.py")
pc = importlib.util.module_from_spec(spec); spec.loader.exec_module(pc)
pc.ensure_pdf()
rows = list(csv.DictReader(open(ROOT / "data" / "bass2_draft.csv", encoding="utf-8")))
base = pc.compare(rows)
n_ok = sum(v.startswith("match") for v in base.values())
print(f"{n_ok} of {len(rows)} rows match unmodified")
ok = n_ok == len(rows)

def first_numeric(r):
    return next(k for k in pc.GAS if r[k] and r[k][-1].isdigit())
MUT = {
    "one reading gets an extra digit": lambda r: r.__setitem__(first_numeric(r), r[first_numeric(r)] + "1"),
    "two readings swapped": lambda r: (r.__setitem__("o2_cal_initial", r["co2_initial"]), r.__setitem__("co2_initial", r["o2_cal_initial"])),
    "wrong page": lambda r: r.__setitem__("source_page", "999"),
    "material word changed": lambda r: r.__setitem__("material_raw", r["material_raw"].replace("PMMA", "Nomex") if "PMMA" in r["material_raw"] else r["material_raw"] + " X"),
    "observation word added at end": lambda r: r.__setitem__("observation", r["observation"] + " quickly"),
}
for name, fn in MUT.items():
    bad = [dict(r) for r in rows]
    for r in bad: fn(r)
    res = pc.compare(bad)
    caught = sum(not v.startswith("match") for v in res.values())
    print(("PASS " if caught == len(rows) else "FAIL ") + f"{name}: caught {caught}/{len(rows)}")
    ok &= caught == len(rows)
print("\nALL CORRUPTIONS CAUGHT" if ok else "\nSOME CORRUPTIONS MISSED")
sys.exit(0 if ok else 1)
