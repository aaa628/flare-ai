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

Currently 126 rows: **0 human-verified, 104 machine-checked, 22 unchecked.** The 22 are the ones the machine could not clear
(flags, hand-keyed values, missing readings): filter `auto_check_notes` for "NEEDS HUMAN CHECK" and do those FIRST.
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

- IDs `P7`, `P11` and `T8` do not appear in the report's text export, so they are not in the data.
  Check the PDF; if they are there, add them. Tests flown as pairs appear as `a`/`b` (e.g. `P3a`, `P3b`).
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

## Comparison rule

Two measurements are only comparable if they share the same quantity, unit, and measurement method.
The (planned) Compare screen refuses otherwise.
