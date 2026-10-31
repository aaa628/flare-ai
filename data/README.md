# Flare AI data

`experiments.csv` is the single source of truth. Every number shown in the app
comes from here. It is empty until records are extracted AND verified.

## Workflow

1. **Extract** a record from a NASA source (NTRS report or PSI investigation).
2. Fill `source_id` and `source_page` so anyone can find the value.
3. **Verify**: a second person checks every value against the source and sets
   `verified_by` and `verified_date`. Unverified rows are never shown as findings.
4. Leave a field **blank** if the source does not state it. Never estimate.

## Columns of `experiments.csv`

| Column | Meaning |
|---|---|
| `id` | Short unique id, e.g. `BASSII-001` |
| `program` | BASS, BASS-II, Saffire, FLEX, ... |
| `title` | Experiment or test title |
| `fuel_material` | Fuel or sample material |
| `material_form` | e.g. thin sheet, cylinder, droplet |
| `gravity_env` | e.g. microgravity (ISS), drop tower, normal gravity |
| `oxygen_pct` | Oxygen concentration (% by volume), blank if unknown |
| `pressure_kpa` | Pressure in kPa, blank if unknown |
| `flow_cm_s` | Airflow velocity in cm/s, blank if unknown |
| `duration_s` | Duration in seconds, blank if unknown |
| `outcome` | `spread`, `extinguished`, `marginal`, or blank |
| `flame_observation` | Observation, quoted or closely paraphrased from source |
| `observation_label` | `measured`, `published_conclusion`, or `our_interpretation` |
| `source_id` | NTRS id (e.g. 20160000593) or PSI id |
| `source_page` | Page/table in the source |
| `source_url` | Link to the source |
| `verified_by` | Name of the person who checked it |
| `verified_date` | YYYY-MM-DD |

## `sources.csv`

One row per source document: `source_id`, `title`, `authors`, `date`, `url`, `type`.

## Comparison rule

Two measurements are only comparable if they share the same quantity, unit,
and measurement method. The Compare screen refuses otherwise.

---

## BASS-II draft data (`bass2_draft.csv`)

126 test records extracted from **Appendix A** (Tables A.1 to A.6) of NASA/TM-20210011385,
*Burning and Suppression of Solids-II (BASS-II) Summary Report*
(https://ntrs.nasa.gov/citations/20210011385). Produced by `scripts/extract_bass2.py`
from `data/source/TM-20210011385.txt`. **Every row is an unverified draft.**

### For the verifier

1. Open `bass2_draft.csv` next to the PDF. Each row's `source_page` is the report page number.
2. For each row compare, against the printed table: material, flow mode (opposed / concurrent /
   stagnation), the 8 gas values (O2 calibrated initial/final, O2 raw initial/final, CO2 initial/final,
   CO initial/final) and the observation text. `raw_text` shows exactly what the extractor saw.
3. If everything matches, fill `verified_by` (your name) and `verified_date` (YYYY-MM-DD).
   If something is wrong, fix the value and write what you changed in `verifier_notes`.
4. Look hardest at rows with a `qc_flag`:
   - `hand_keyed` (M5, O16, T3): irregular layout, values typed by hand.
   - `o2_final_reading_suspect`: final O2 differs from initial by more than 3 vol%. NASA's own
     table shows some glitch readings (for example 20.8 to 0.6). Keep them as printed; do not "fix".
   - `flow_mode_not_stated`: the table has no clear flow mode for that row. Leave blank.
5. Run `python scripts/promote_verified.py` to copy verified rows into `experiments.csv`
   (the only file the app reads).

### Known limits (be honest about these in the pitch)

- IDs `P7`, `P11` and `T8` do not appear in the report's text export, so they are not in the data.
  Check the PDF; if they are there, add them. Tests flown as pairs appear as `a`/`b` (e.g. `P3a`, `P3b`).
- Flow velocity (cm/s) is **not** a column. The report gives fan/potentiometer settings and, in some rows,
  velocities in parentheses, in formats that differ by PI. `setup_raw` keeps the original text. Any
  velocity-based comparison must be keyed carefully by hand and must not mix settings with true velocities.
- Pressure is not stated per test in these tables.
- `outcome` (spread / extinguished / marginal) is **not** extracted. Coding it is an interpretation and
  will be labelled `our_interpretation` in the app, with the supporting observation quoted.
- Values are strings kept as printed (e.g. `+OR`, `>500`, `failed`, `–1`).
