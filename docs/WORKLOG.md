# Flare AI worklog

Append-only. Newest entries at the bottom. Format is described in docs/HANDOFF_PROMPT.md section 9.

## 2026-10-31 11:00 IST - Claude (Sonnet 5.5)
Did:
- Created repo scaffold: README.md, requirements.txt, .streamlit/config.toml, app/Home.py, app/data.py,
  app/pages/1_Flame_Explorer.py, app/pages/5_About.py, data/ schema files.
- Wrote scripts/extract_bass2.py and extracted 126 BASS-II test rows (NASA/TM-20210011385, Appendix A) into
  data/bass2_draft.csv with page numbers, raw text and QC flags. Wrote scripts/promote_verified.py.
- Documented verification workflow and known data limits in data/README.md.
- Wrote docs/HANDOFF_PROMPT.md for switching to another AI.
Verified by running:
- extract_bass2.py runs and produces 126 rows (123 auto-parsed, 3 hand-keyed); every row contains the camera-setting
  marker used as an independent presence check; plausibility check on O2 values; random spot-check vs raw text.
- promote_verified.py runs (promotes 0 rows, correct because nothing is verified yet).
- App files pass `python -m py_compile`. **The Streamlit app has NOT been run** (sandbox could not install packages).
Decisions + why:
- Streamlit + CSV instead of React/FastAPI/Postgres: two-week hackathon, three students.
- Verified-only rule enforced in app/data.py so unchecked data never appears as a finding.
- No outcome coding or flow velocity extracted: both need human judgement; see data/README.md.
Open problems / assumptions:
- P7, P11, T8 missing from the text export; may exist in the PDF.
- Meaning of "calibrated" vs "raw" O2 columns not yet confirmed from the report text.
- Official judging criteria and AI-use rules unknown until the Nov 13 guides.
Next step I recommend:
- A human verifies bass2_draft.csv; someone runs the app locally and reports errors; then build Compare + detail pages.
