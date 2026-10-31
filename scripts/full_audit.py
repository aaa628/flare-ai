import csv
import re
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parent.parent
CSV_PATH = ROOT / "data" / "bass2_draft.csv"
SOURCE_TXT_PATH = ROOT / "data" / "source" / "TM-20210011385.txt"

def load_txt(path):
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace").splitlines()
    return []

# Helper to normalize strings for comparison, stripping out spaces/newlines
def normalize(s):
    if not s: return ""
    return re.sub(r'\s+', ' ', s.strip())

def main():
    with CSV_PATH.open("r", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))

    src_lines = load_txt(SOURCE_TXT_PATH)

    # Missing checks
    missing_ids = ["P7", "P11", "T8"]
    missing_status = {}
    for mid in missing_ids:
        found = any(mid in line for line in src_lines)
        missing_status[mid] = found

    exact_matches = []
    discrepancies = []
    qc_flag_rows = []

    # A true audit means attempting to see if the values in the CSV exist in the raw_text source for that row.
    # The source text is basically the paragraph/line from the PDF.

    fields_to_check = [
        "material_raw", "flow_mode", "o2_cal_initial", "o2_cal_final",
        "o2_raw_initial", "o2_raw_final", "co2_initial", "co2_final",
        "co_initial_ppm", "co_final_ppm", "observation", "setup_raw"
    ]

    for row in rows:
        raw_text = normalize(row['raw_text'])
        mismatches = []
        flags = row['qc_flag'].split(';') if row['qc_flag'] else []
        if flags:
            qc_flag_rows.append(row)

        for field in fields_to_check:
            val = row[field]
            if val:
                val_norm = normalize(val)
                if val_norm not in raw_text:
                    mismatches.append(f"{field}: '{val}' not found in raw text.")

        # Check if the extracted values are consistent
        if not mismatches and not flags:
            exact_matches.append(row)
        elif mismatches:
            discrepancies.append({
                "row": row,
                "mismatches": mismatches
            })

    report_lines = []
    report_lines.append("# BASS-II Data Verification Audit Report")
    report_lines.append("")
    report_lines.append("This report audits `data/bass2_draft.csv` against the NASA TM-20210011385 report text.")
    report_lines.append("")
    report_lines.append("## Overview")
    report_lines.append(f"- Checked {len(rows)} rows from `data/bass2_draft.csv`.")
    report_lines.append("")

    report_lines.append("## Missing Tests (P7, P11, T8)")
    for mid in missing_ids:
        report_lines.append(f"- {mid}: {'Found' if missing_status[mid] else 'Not found'} in source text export.")

    report_lines.append("")
    report_lines.append("## Exact Matches")
    report_lines.append(f"{len(exact_matches)} rows were parsed perfectly with no QC flags, and all CSV fields were explicitly found in the source raw text.")

    report_lines.append("")
    report_lines.append("## QC Flag Rows Requiring Special Attention")
    for r in qc_flag_rows:
        report_lines.append(f"### {r['id']} (Page {r['source_page']})")
        report_lines.append(f"- **Flags:** {r['qc_flag']}")
        report_lines.append(f"- **Values:** O2: {r['o2_cal_initial']} -> {r['o2_cal_final']}, Mode: {r['flow_mode']}")
        report_lines.append(f"- **Observation:** {r['observation']}")
        report_lines.append(f"- **Raw Text:** `{r['raw_text']}`")
        report_lines.append("")

    report_lines.append("## Discrepancies and Mismatches")
    if not discrepancies:
        report_lines.append("No extracted field mismatch found against raw text blocks.")
    for d in discrepancies:
        r = d["row"]
        report_lines.append(f"### {r['id']} (Page {r['source_page']})")
        report_lines.append(f"- **Flags:** {r['qc_flag']}")
        for m in d["mismatches"]:
            report_lines.append(f"  - {m}")
        report_lines.append(f"- **Raw Text Extracted from Report:** `{r['raw_text']}`")
        report_lines.append("")

    report_path = ROOT / "docs" / "VERIFICATION_AUDIT.md"
    report_path.write_text("\n".join(report_lines))
    print(f"Report written to {report_path}")

if __name__ == "__main__":
    main()
