# Flare AI data

**Status: 537 records from NASA PSI; 537 machine-checked, 537 human-verified (team sign-off), 0 unchecked; 24 investigations.**
All files in `source/psi/` were downloaded fresh from NASA PSI on 2026-11-13 (`scripts/fetch_psi_records.py` writes
`source/psi/MANIFEST.csv` with each file's PSI investigation, NASA file name, size and SHA-256; `scripts/fetch_psi_catalog.py`
writes the catalog and tables). Every file was compared byte for byte with the copies used earlier: all identical.

**Sign-off.** The user stated that the 628 Aerospace team verified all records; each record carries `verified_by` =
"628 Aerospace team", `verified_date` = 2026-11-13 and a `verifier_notes` line saying so. A record is shown as verified only
while its automated re-read from NASA's file also passes: changing any value drops it to unchecked and voids the sign-off.

**Flags** (our reading of NASA's own values; nothing is changed): BASS-II final calibrated O2 more than 3 vol% from the start
(`o2_final_reading_suspect`, 6 tests) or not a plain number (`o2_final_not_numeric`, 2 tests); FLEX pressure printed as 0 (1)
and an identifier used twice (2). Flagged readings are left out of charts, with the reason.

## Adding data

1. Put the source files under `data/source/` (report text, `data/source/psi/` data files, `data/source/psi/catalog/*.json`).
2. Fill the CSVs below (header row = the column format). Keep the CSV as UTF-8; spreadsheet programs may rewrite characters such as the en dash and µ.
3. Run `python scripts/build_site_data.py` (needs `pip install openpyxl`; the PDF comparison also needs `pdftotext`).
   It re-runs every automated check, writes `site/data/data.js` and `netlify/functions/ask/corpus.mjs`, and copies the
   PSI files into `site/sources/psi/`. With empty templates it still runs and writes an all-zero data file.
4. Run the tests in `tests/` and commit the generated files.

A person verifies a record by comparing it with its source and filling `verified_by` and `verified_date`.
Never fill these from an automated check: "machine-checked" is never "verified".

## Files and columns

### `bass2_draft.csv`
Report-table test records (one row per test, values kept exactly as printed). Checked at build time by `scripts/crosscheck_bass2.py`, `pdfcheck_bass2.py` and `psicheck_bass2.py` against the source text, PDF and spreadsheet in `data/source/`.

Columns: `id, pi, as_run_no, sample_no, material_raw, flow_mode, o2_cal_initial, o2_cal_final, o2_raw_initial, o2_raw_final, co2_initial, co2_final, co_initial_ppm, co_final_ppm, observation, setup_raw, source_page, qc_flag, parse_ok, verified_by, verified_date, verifier_notes, auto_checked_by, auto_checked_date, auto_check_notes, pdf_check, psi_check, raw_text`

### `bass1_psi.csv`
Test records copied from a PSI data file (one row per test; `fields_json` keeps every original column). Re-read from the file in `data/source/psi/` on every build.

Columns: `id, experiment, pi, source_id, source_file, source_row, material_raw, flow_mode, airflow_raw, o2_raw, o2_note, o2_vol_pct, outcome_raw, qc_flag, observation, fields_json, verified_by, verified_date, verifier_notes`

### `bass2_psi_extra.csv`
Extra test records that appear only in a PSI data file (same columns as the other `*_psi.csv` files).

Columns: `id, experiment, pi, source_id, source_file, source_row, material_raw, flow_mode, airflow_raw, o2_raw, o2_note, o2_vol_pct, outcome_raw, qc_flag, observation, fields_json, verified_by, verified_date, verifier_notes`

### `flex_psi.csv`
Droplet-combustion test records from a PSI data file (same columns; `outcome_raw` holds the recorded end of test).

Columns: `id, experiment, pi, source_id, source_file, source_row, material_raw, flow_mode, airflow_raw, o2_raw, o2_note, o2_vol_pct, outcome_raw, qc_flag, observation, fields_json, verified_by, verified_date, verifier_notes`

### `saffire_psi.csv`
Large-scale test records from PSI data files (same columns).

Columns: `id, experiment, pi, source_id, source_file, source_row, material_raw, flow_mode, airflow_raw, o2_raw, o2_note, o2_vol_pct, outcome_raw, qc_flag, observation, fields_json, verified_by, verified_date, verifier_notes`

### `investigations_curated.csv`
Our labels for each investigation in the catalogue (`data/source/psi/catalog/*.json`), each with its basis.

Columns: `accession, short_name, fuel_class, fuel_examples, pillar, brief_mention, scale, basis, evidence_type, summary_ours`

### `ai_review_bass2.csv`
Written row-by-row reviews for flagged report rows (`id`, reviewer, date, finding).

Columns: `id, reviewed_by, reviewed_date, finding`

### `sources.csv`
One row per source document or data file, listed on the About page.

Columns: `source_id, title, authors, date, url, type`

## Comparison rule

Two measurements are only comparable if they share the same quantity, unit, and measurement method.
The Compare screen refuses otherwise: it never charts tests from different experiments, and it leaves out flagged, non-numeric or approximate values, saying why next to each chart.
