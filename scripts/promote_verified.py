"""Copy VERIFIED rows from data/bass2_draft.csv into data/experiments.csv.

A row is promoted only if verified_by and verified_date are filled in.
We do not interpret anything here: `outcome` stays blank until the team codes it
(and that coding is labelled our_interpretation in the app).
"""
import csv
from pathlib import Path

D = Path(__file__).resolve().parent.parent / "data"
COLS = ["id", "program", "title", "fuel_material", "material_form", "gravity_env",
        "oxygen_pct", "pressure_kpa", "flow_cm_s", "duration_s", "outcome",
        "flame_observation", "observation_label", "source_id", "source_page",
        "source_url", "verified_by", "verified_date"]

rows = []
for r in csv.DictReader((D / "bass2_draft.csv").open()):
    if r["verified_by"].strip() and r["verified_date"].strip():
        rows.append({
            "id": r["id"], "program": "BASS-II",
            "title": f"{r['pi']} test {r['id'].split('-')[1]}",
            "fuel_material": r["material_raw"], "material_form": "",
            "gravity_env": "microgravity (ISS, Microgravity Science Glovebox)",
            "oxygen_pct": r["o2_cal_initial"], "pressure_kpa": "", "flow_cm_s": "",
            "duration_s": "", "outcome": "",
            "flame_observation": r["observation"], "observation_label": "measured",
            "source_id": "20210011385", "source_page": r["source_page"],
            "source_url": "https://ntrs.nasa.gov/citations/20210011385",
            "verified_by": r["verified_by"], "verified_date": r["verified_date"],
        })
with (D / "experiments.csv").open("w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=COLS)
    w.writeheader()
    w.writerows(rows)
print(f"promoted {len(rows)} verified rows")
