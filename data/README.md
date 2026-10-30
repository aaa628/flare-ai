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
