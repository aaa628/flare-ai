"""Proves the PSI records are checked against NASA's files: unmodified rows are machine-checked, and a row with any
data value changed drops to unchecked. Run: python tests/psi_import_test.py   (needs openpyxl)"""
import importlib.util, pathlib, sys, warnings
warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
spec = importlib.util.spec_from_file_location("b", ROOT / "scripts" / "build_site_data.py")
b = importlib.util.module_from_spec(spec); spec.loader.exec_module(b)
ok = True
recs = b.psi_records()
n = sum(r["level"] == "machine" for r in recs)
print(("PASS " if n == len(recs) else "FAIL ") + f"unmodified: {n}/{len(recs)} machine-checked"); ok &= n == len(recs)
real_read = b.read
for col in ["material_raw", "o2_raw", "airflow_raw", "observation", "source_row"]:
    def bad_read(name, col=col):
        rows = real_read(name)
        if name.endswith("_psi.csv") or name.endswith("_psi_extra.csv"):
            for r in rows: r[col] = (r[col] or "") + "x"
        return rows
    b.read = bad_read
    recs = b.psi_records()
    caught = sum(r["level"] == "none" for r in recs)
    print(("PASS " if caught == len(recs) else "FAIL ") + f"{col} changed: caught {caught}/{len(recs)}"); ok &= caught == len(recs)
b.read = real_read
print("\nALL CORRUPTIONS CAUGHT" if ok else "\nSOME CORRUPTIONS MISSED")
sys.exit(0 if ok else 1)
