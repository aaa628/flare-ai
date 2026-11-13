"""Proves scripts/crosscheck_bass2.py can actually catch errors: corrupt a passing row in memory
in different ways and require that every corruption is rejected. Run: python tests/crosscheck_mutation_test.py"""
import csv, importlib.util, pathlib, sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("cc", ROOT / "scripts" / "crosscheck_bass2.py")
cc = importlib.util.module_from_spec(spec); spec.loader.exec_module(cc)

spans = cc.table_pages()
rows = list(csv.DictReader(open(ROOT / "data" / "bass2_draft.csv", encoding="utf-8")))
strict = [r for r in rows if not cc.check(r, spans, {})[0]]
good = strict
reviewed = [r for r in rows if r not in strict and not cc.check(r, spans)[0]]
print(f"{len(strict)} rows pass strictly, {len(reviewed)} more pass via row-by-row review, of {len(rows)}")
ok = True

def expect_fail(name, fn, sample):
    global ok
    bad = caught = 0
    for r in sample:
        m = dict(r); fn(m); bad += 1
        if cc.check(m, spans)[0]:
            caught += 1
    print(("PASS " if caught == bad else "FAIL ") + f"{name}: caught {caught}/{bad}")
    ok &= caught == bad

def swap(m):  m["o2_cal_final"], m["co2_initial"] = m["co2_initial"], m["o2_cal_final"]
def bump(m):  m["co2_final"] = str(float(m["co2_final"]) + 0.01)
def page(m):  m["source_page"] = "112" if m["id"][7] != "T" else "103"
def offset(m): m["o2_cal_initial"] = m["o2_raw_initial"]
def obs(m):   m["observation"] = m["observation"] + " extra"
def sample(m): m["sample_no"] = "99999"
def shift(m):  # classic column shift: every gas value moves one place left
    ks = ["o2_cal_initial","o2_cal_final","o2_raw_initial","o2_raw_final","co2_initial","co2_final","co_initial_ppm","co_final_ppm"]
    vals = [m[k] for k in ks]; vals = vals[1:] + vals[:1]
    for k, v in zip(ks, vals): m[k] = v
def blank(m): m["co_final_ppm"] = ""

for name, fn in [("REVIEWED wrong table page", page), ("REVIEWED observation edited", obs),
                 ("REVIEWED wrong sample number", sample), ("REVIEWED all readings shifted one column", shift)]:
    expect_fail(name, fn, reviewed)
expect_fail("two readings swapped", swap, good)
expect_fail("one reading changed by 0.01", bump, good)
expect_fail("wrong table page", page, good)
expect_fail("starting O2 replaced by raw value", offset, good)
expect_fail("observation edited", obs, good)
expect_fail("wrong sample number", sample, good)
expect_fail("all readings shifted one column", shift, good)
expect_fail("reading blanked", blank, good)
print("\nALL CORRUPTIONS CAUGHT" if ok else "\nSOME CORRUPTIONS MISSED")
sys.exit(0 if ok else 1)
