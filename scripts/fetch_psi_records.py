"""Download, fresh from NASA PSI, the files that Flare AI's test records are read from, and write a manifest.

Writes data/source/psi/<file> (the names scripts/import_psi.py reads) and data/source/psi/MANIFEST.csv with, for every
file: the NASA file name, the PSI investigation, the download request used, the retrieval date, the size and the SHA-256.
The experiment tables are NASA's served "Experimental table" files (the same bytes as data/source/psi/tables/);
BASS-I conditions come from NASA's "As Run Test Matrix" spreadsheet in PSI-26's Science Documents.

Run (needs network access to psi.nasa.gov):  python scripts/fetch_psi_records.py
"""
import csv
import hashlib
import urllib.parse
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "data" / "source" / "psi"
API = "https://psi.nasa.gov/geode-py/ws"
# local name (what import_psi.py reads) -> (PSI accession, NASA file name)
FILES = {
    "PSI-25_experimental_table_BASS-II.csv": ("PSI-25", "PSI-25_Experimental table_BASS-II.csv"),
    "PSI-26_as_run_test_matrix_BASS.xlsx": ("PSI-26", "PSI-26_Science Documents_As Run_Test Matrix.xlsx"),
    "PSI-68_planned_test_matrix_FLEX-2.csv": ("PSI-68", "PSI-68_Experimental table_Flex2.csv"),
    "PSI-69_experimental_table_FLEX.csv": ("PSI-69", "PSI-69_Experimental table_FLEX.csv"),
    "PSI-98_experimental_table_SAFFIRE-I.csv": ("PSI-98", "PSI-98_Experimental table_SAFFIRE-1.csv"),
    "PSI-99_experimental_table_SAFFIRE-II.csv": ("PSI-99", "PSI-99_Experimental table_SAFFIRE-2.csv"),
    "PSI-100_experimental_table_SAFFIRE-III.csv": ("PSI-100", "PSI-100_Experimental table_SAFFIRE-3.csv"),
}


def get(url):
    return urllib.request.urlopen(url, timeout=120).read()


def main():
    SRC.mkdir(parents=True, exist_ok=True)
    rows = []
    for local, (acc, name) in FILES.items():
        url = f"{API}/studies/{acc}/download?" + urllib.parse.urlencode({"file": name, "redirect": "false"})
        signed = get(url).decode().strip().strip('"')
        data = get(signed)
        (SRC / local).write_bytes(data)
        rows.append({"local_file": local, "investigation": acc, "nasa_file": name, "download_request": url,
                     "retrieved": date.today().isoformat(), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
        print(f"{local}: {len(data)} bytes from {acc} '{name}'")
    with (SRC / "MANIFEST.csv").open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"wrote {SRC.relative_to(ROOT)}/MANIFEST.csv ({len(rows)} files)")


if __name__ == "__main__":
    main()
