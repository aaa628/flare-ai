# Flare AI data

`bass2_draft.csv` is the working sheet. The website reads it (through `scripts/build_site_data.py`).
Every row has a **check level**:
- **verified**: `verified_by` and `verified_date` filled in by a person who compared the row with NASA's PDF.
- **machine-checked**: passed `scripts/crosscheck_bass2.py` (automated; no person has looked). Shown on the site with that label.
- **unchecked**: neither. Hidden by default; `auto_check_notes` says why it needs a human.

## Pipeline

1. `python scripts/extract_bass2.py` parses Appendix A (Tables A.1 to A.6) of NASA/TM-20210011385,
   *Burning and Suppression of Solids-II (BASS-II) Summary Report*
   (https://ntrs.nasa.gov/citations/20210011385), from `data/source/TM-20210011385.txt`. It **overwrites**
   `bass2_draft.csv`, so do not re-run it after verification has started unless you port your edits.
2. `python scripts/crosscheck_bass2.py` re-checks every row and fills `auto_checked_*` (it never touches `verified_*`; safe to re-run).
3. A person verifies rows (below).
4. `python scripts/build_site_data.py` writes `site/data/data.js`. Reload the site. It re-runs the cross-check, so a row edited after its check drops back to unchecked.

`sources.csv` has one row per source document (`source_id,title,authors,date,url,type`).

## For the verifier

Currently 126 rows: **0 human-verified, 126 machine-checked (104 strictly + 22 via the row-by-row review in
`ai_review_bass2.csv`), 0 unchecked.** Do the 22 reviewed rows FIRST (their `auto_check_notes` contain "row-by-row review"):
they carry flags, hand-keyed values, NASA dashes or `+OR`/`Over`/`failed` entries.
Then work through the machine-checked rows; the machine check does not replace your comparison with the PDF.

1. Open `bass2_draft.csv` next to the PDF. `source_page` is the report page number; the Appendix A table is
   A.1 Bhattacharjee (B), A.2 Ferkul (F), A.3 Fernandez-Pello (P), A.4 Miller (M), A.5 Olson (O), A.6 T'ien (T).
2. For each row compare with the printed table: material, flow mode (opposed / concurrent / stagnation),
   the 8 gas values (O2 calibrated initial/final, O2 raw initial/final, CO2 initial/final, CO initial/final)
   and the observation text. `raw_text` is exactly what the extractor saw; `setup_raw` is the setup columns as printed.
3. If everything matches **in the PDF**, fill `verified_by` (your name) and `verified_date` (YYYY-MM-DD). Never fill these from the machine check.
   If something is wrong, fix the value and note what you changed in `verifier_notes`.
4. Look hardest at rows with a `qc_flag`:
   - `hand_keyed` (M5, O16, T3): irregular layout, values typed by hand.
   - `o2_final_reading_suspect`: final O2 differs from initial by more than 3 vol%. NASA's own table shows
     some glitch readings (for example 20.8 to 0.6). Keep them as printed; do not "fix".
   - `flow_mode_not_stated`: the table has no clear flow mode for that row. Leave blank.
   - `material_check`: the material name could not be split cleanly from the setup columns. Fix by hand.
5. Run `python scripts/build_site_data.py`, reload `site/index.html`, and confirm your rows appear.

Tip: keep the file as CSV (UTF-8). Spreadsheet programs may rewrite characters such as the en dash (`–1`) and
the micro sign (`µm`); check those survive a save.

## Columns of `bass2_draft.csv`

`id, pi, as_run_no, sample_no, material_raw, flow_mode, o2_cal_initial, o2_cal_final, o2_raw_initial,
o2_raw_final, co2_initial, co2_final, co_initial_ppm, co_final_ppm, observation, setup_raw, source_page,
qc_flag, parse_ok, verified_by, verified_date, verifier_notes, auto_checked_by, auto_checked_date, auto_check_notes, raw_text`

Units: O2 and CO2 in vol%, CO in ppm. Values are strings kept exactly as printed.

## Known limits (be honest about these in the pitch)

- IDs `P7`, `P11` and `T8` do not appear in the report's tables (checked in the PDF), so they are not in the data. Tests flown as pairs appear as `a`/`b` (e.g. `P3a`, `P3b`).
- Flow velocity (cm/s) is **not** a column. The report gives fan/potentiometer settings and, in some rows,
  velocities in parentheses, in formats that differ by investigator. Any velocity-based comparison must be keyed
  carefully by hand and must not mix settings with true velocities.
- Pressure is not stated per test in these tables.
- `outcome` (spread / extinguished / marginal) is **not** extracted. Coding it is an interpretation and will be
  labelled `our_interpretation` on the site, with the supporting observation quoted.
- The meaning of "calibrated" vs "raw" O2 is shown as labelled in NASA's table; confirm against the report text
  (Section 1.3 and Appendix B) before making claims about it.
- Values such as `+OR`, `>500`, `failed`, `Over` are NASA's own entries.

## What the automated cross-check does and does not do

It checks (all must pass): the row's page lies in the page range of its investigator's table (from a fresh scan of the table headings);
the 8 gas fields are exactly the 8 printed tokens before the observation and the observation is the rest of the row;
calibrated minus raw starting O2 is 0.2 to 2.5 vol% (about 1.0 for nearly every row, so a shifted column breaks it);
readings are numeric and in plausible ranges; no QC flag. `tests/crosscheck_mutation_test.py` corrupts rows 8 ways and requires all to be caught.

It does **not** compare anything with the PDF. The text it reads is a text export of the PDF, so an error introduced by that export
itself would pass. Only a person with the PDF can verify.

## Data from NASA PSI (`scripts/import_psi.py`)

NASA Physical Sciences Informatics (psi.nasa.gov, all CC0-1.0) holds the experiments' own data tables. Files used are
committed in `source/psi/`: PSI-25 BASS-II experimental table, PSI-26 BASS "As Run Test Matrix" (xlsx), PSI-98/99/100
SAFFIRE-I/II/III experimental tables. `import_psi.py` writes `bass1_psi.csv` (121 rows), `saffire_psi.csv` (13 rows) and
`bass2_psi_extra.csv` (O20, O21, O22: in PSI-25 but not in the report). Each row stores its file and row number; all other
recorded values are kept in `fields_json`, as written in NASA's file. Long computed decimals in the BASS-I spreadsheet are
rounded to 4 places and marked "(rounded)". BASS-I O2 is logged as a fraction (0.221); the site shows it as printed and as
vol% (x 100). SAFFIRE-II rows 2-6 and 2-9 have a blank material cell in NASA's file; shown as "not stated (row above: ...)".
On every build `build_site_data.py` re-imports the source files; a row whose data no longer equals the file drops to
unchecked (`tests/psi_import_test.py`). Verify by comparing a row with the file in `source/psi/`, then fill `verified_by`/`verified_date`.

`scripts/psicheck_bass2.py` compares the 126 report rows with the PSI-25 table (column `psi_check`): 123 agree.
Disagreements between NASA's two sources (shown on the site, never "fixed"): F3 final calibrated O2 (report 0.9 =
formula leftover, PSI none), P22b final CO (report 236, PSI 239), P3a CO (report 33 then blank, PSI 2 then 33; the PDF
image confirms the report's print).

**Never compare O2 across experiments**: BASS-II = calibrated chamber sensor, BASS-I = logged O2 under "ISS environment",
SAFFIRE = approximate values (SAFFIRE-II derived from CO2).

## Comparison with NASA's PDF (`scripts/pdfcheck_bass2.py`)

Downloads the official PDF to `data/raw/` (git-ignored, 49 MB) and reads its text layer with `pdftotext` (a separate
extraction from `source/TM-20210011385.txt`). For every row: printed on the stated page; exactly one table line starts
with the test ID + sample number; the 8 readings are consecutive on that line; the material name and the FULL log note
match word for word. Result per row in column `pdf_check`. **Result: 126 of 126 match.**
`tests/pdfcheck_mutation_test.py` corrupts every row 5 ways; all caught. It is still automated, so rows stay
"machine-checked" until a team member signs `verified_by`.
Corrections made from the PDF (2026-10-31): the old text export had a control character (byte 0x02) instead of a hyphen
in 8 material names (B14, B17, B18, B21, B22: "200-µm-thick"; M2, M14: "one-sided"; M19: "two-sided") and in 2 notes
(M2 "self-extinguished", T1 "CSA-CP"). Fixed in `bass2_draft.csv` (re-running `extract_bass2.py` would bring the bug back).
The PDF's column headings confirm the order: calibrated initial/final O2, then sensor initial/final O2, CO2, CO.
P7, P11 and T8 are not in the PDF's tables either.

## Row-by-row review (`ai_review_bass2.csv`)

The 22 rows that fail only the soft checks (flags, dashes or non-numeric NASA entries, unusual offset) were read one by one
against the report text by Claude; the finding is stored per row. They still must pass every strict text check, so an edit
to such a row drops it back to unchecked. Main finding: in paired a/b tests (B2, F3, P22a, P22b, T28a, T28b) the printed
"final calibrated O2" is a spreadsheet formula leftover (it equals starting calibrated O2 minus or plus the raw value, e.g.
P22a 0.6 = 20.8 - 20.2, P22b 39.1 = 20.0 + 19.1). Those rows carry the flag `o2_cal_final_formula_artifact`; never use
that value. The site's oxygen chart counts only rows that have both a calibrated and a raw starting reading.

## Comparison rule

Two measurements are only comparable if they share the same quantity, unit, and measurement method.
The (planned) Compare screen refuses otherwise.
