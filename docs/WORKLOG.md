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

## 2026-10-31 14:00 IST - Claude (Sonnet 5.5)
Did:
- Replaced the Streamlit prototype with a static website: site/index.html, site/css/style.css, site/js/app.js.
  Pages: Overview (computed counts, two SVG charts, evidence-label legend), Flame Explorer (search + investigator /
  flow mode / starting O2 filters, natural sort), per-test detail (Measured readings, log note, Published conclusion,
  Our interpretation, Source card with Appendix A table + page), About. Compare / Intelligence Lab / Scenario Check
  are greyed "soon" placeholders in the nav.
- scripts/build_site_data.py turns bass2_draft.csv + sources.csv into site/data/data.js (a .js file so the site works
  from file://). Removed data/experiments.csv and scripts/promote_verified.py (one working sheet now).
- Fixed an extraction bug found by looking at a screenshot: material_raw was polluted with igniter/flow text for 62 of
  126 rows. extract_bass2.py now splits material | igniter | restrictor+mode with a regex. Regenerated bass2_draft.csv
  (still 126 rows; 123 auto + 3 hand-keyed). No rows had been verified, and origin had no new commits, so nothing was lost.
- Deleted app/, .streamlit/, requirements.txt. Rewrote README.md and data/README.md; patched docs/HANDOFF_PROMPT.md.
- Added tests/site_smoke_test.py (Playwright).
Verified by running:
- tests/site_smoke_test.py: 29/29 checks pass in headless Chromium via file://, zero console/page errors. Covers empty
  state, preview banner, 126 rows, filters (Olson=24), search, natural sort, detail callouts, unknown-id refusal, About,
  and no horizontal scroll at 390px wide. Screenshots reviewed by eye (desktop + mobile).
- NOT run: on the team's own machines/browsers (Safari, Firefox); with any verified rows (none exist yet).
Decisions + why:
- Static site over Streamlit: team can double-click it, judges just open a URL, and it can be tested in this sandbox.
- Preview mode (?preview=draft) exists so the team can see the UI before verification; red banner on every page.
- No browser-side LLM (key would leak). Intelligence Lab will be retrieval + rules.
Open problems / assumptions:
- P7, P11, T8 missing; "calibrated" vs "raw" O2 meaning unconfirmed; judging criteria + AI-use rules unknown until Nov 13.
- The smoke test hard-codes the 0-verified state; update its first checks once rows are verified.
Next step I recommend:
- Verifier starts on data/bass2_draft.csv; team opens the site and reports problems; then build Compare + outcome coding.
