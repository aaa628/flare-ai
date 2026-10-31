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

## 2026-10-31 15:00 IST - Claude (Sonnet 5.5)
Did:
- Rewrote docs/HANDOFF_PROMPT.md from scratch as v2: operating contract, architecture, design tokens, exact data facts and traps,
  status, and concrete specs for the remaining features (Compare refusal rules, evidence-grade rule, outcome coding, Scenario Check
  abstention, retrieval-only Intelligence Lab, PDF brief), plus commands, do-not list, pitch story and a first-5-minutes checklist.
Verified by running:
- Cross-checked every concrete claim in the prompt against the repo (row counts per investigator, parse_ok counts, QC-flagged IDs,
  file tree via git ls-files, last commit hash). All matched. No site/data changes this entry.
Decisions + why:
- Evidence-grade thresholds, outcome categories and the +-1.5 vol% abstention range are written as PROPOSALS for the team to confirm.
Open problems / assumptions:
- Same as the previous entry (P7/P11/T8, calibrated vs raw O2, judging criteria unknown until Nov 13).
Next step I recommend:
- Hand this file to the next AI; verifier starts on data/bass2_draft.csv.

## 2026-10-31 16:40 IST - Claude (Sonnet 5.5)
Did:
- User reported "Open Flame Explorer" and "How we handle evidence" opened raw unstyled pages. Pulled the user's 4 commits (CSS restyle +
  index.html assets pointed at raw.githubusercontent.com for a hosted previewer).
- Root cause: previewers inject a <base href>; bare `href="#/explorer"` resolves against it and navigates to the raw file (text/plain).
  This broke ALL in-app links (nav, brand, test rows), not just the two buttons.
- Fix in site/js/app.js: one delegated click handler for `#/...` and `#main`; preview mode is now a runtime toggle (setPreview) instead of
  reload/hand-built URLs. User's CSS and asset URLs left untouched.
- Added tests/previewer_nav_test.py (simulated previewer); smoke test now serves raw.githubusercontent asset URLs from local files.
Verified by running:
- Reproduced first: 5 FAIL (click landed on http://raw.test/site/#/explorer). After fix: previewer test 14/14, smoke test 29/29,
  `node --check` OK, screenshot of the restyled page reviewed.
- NOT run: in the user's real previewer tool (unknown which one); on their devices.
Decisions + why:
- Handle links in JS rather than rewriting hrefs: works under any <base>, keeps hrefs meaningful for no-JS and right-click.
Open problems / assumptions:
- index.html now depends on absolute raw.githubusercontent URLs (works only in the user's previewer). Must go back to relative paths
  before real deployment or local double-click use. raw.githubusercontent caches ~5 min, so a pushed fix can take a few minutes to appear.
Next step I recommend:
- Deploy to a real static host (Netlify Drop is the quickest), revert asset URLs to relative, then continue with verification + Compare.

## 2026-10-31 18:00 IST - Claude (Sonnet 5.5)
Did:
- User asked me to "verify the data and add it to the website as verified". I cannot honestly do the human step (no PDF access; only a text
  export that the extractor also used), so I built the strongest legitimate check and an honest three-level label instead.
- scripts/crosscheck_bass2.py: table/page range from a fresh heading scan; token partition of the printed row tail; calibrated-minus-raw
  starting O2 offset invariant (0.2-2.5 vol%, ~1.0 typical); numeric ranges; no QC flags. Fills auto_checked_by/date/notes only.
  Result: 104 of 126 machine-checked; 22 left for a human with the reason in auto_check_notes.
- tests/crosscheck_mutation_test.py: 8 kinds of deliberate corruption x 104 rows, all caught (incl. a single reading changed by 0.01).
- build_site_data.py: levels human/machine/none; re-runs the cross-check at build so edited rows downgrade automatically.
- site/js/app.js: chips + wording for 3 levels, Overview tiles (human / machine / unchecked / sources), plain-words notice, detail page
  callout + source card, About rules, footer switch "Team preview: show unchecked rows". CSS: one added rule (.chip.mach).
- Relaxed two over-strict checks found while testing (small negative CO is instrument offset; last table page span).
Verified by running:
- crosscheck_mutation_test 8/8; site_smoke_test 34/34; previewer_nav_test 14/14; screenshots of Overview and a machine-checked detail reviewed.
- NOT done: any human comparison with the PDF. 0 rows are human-verified.
Decisions + why:
- "verified" stays human-only: the site tells judges a person checked the PDF; a machine pass must not be presented as that.
Open problems / assumptions:
- The cross-check shares its text source with the extractor. P7/P11/T8 still missing. "calibrated vs raw" O2 meaning unconfirmed.
Next step I recommend:
- Verifier: do the 22 NEEDS HUMAN CHECK rows first, then the 104 machine-checked ones against the PDF; stamp verified_by/date; rebuild.

## 2026-10-31 19:00 IST - Claude (Sonnet 5.5)
Did:
- Wrote docs/CONTINUATION_SUMMARY.md (whole-chat summary + exact latest state) for the user's move to a different account.
Verified by running:
- git fetch/status: in sync with origin, clean tree, last code commit c62b93d; data.js counts {records:126, verified:0, machine:104, unchecked:22}.
Decisions + why: none new.
Open problems / assumptions: unchanged (see CONTINUATION_SUMMARY section 7).
Next step I recommend: new session reads CONTINUATION_SUMMARY + HANDOFF_PROMPT, then asks the user the 3 check-in questions.

## 2026-10-31 20:00 IST - Claude
Did:
- User asked to put all rows in the machine-checked category. Read the 22 remaining rows one by one against their printed row text.
  All extracted fields match the print. Findings stored per row in data/ai_review_bass2.csv.
- Found that in paired a/b tests (B2, F3, P22a, P22b, T28a, T28b) "final calibrated O2" is a spreadsheet formula leftover
  (= starting calibrated O2 -/+ raw value; checked numerically for all 6). New qc flag o2_cal_final_formula_artifact + red callout on the site.
- scripts/crosscheck_bass2.py: hard (text-faithfulness) vs soft (flags, dashes, offset) problems; soft-only rows pass if reviewed.
- Overview O2 chart now counts only rows with both calibrated and raw starting readings (124).
Verified by running:
- crosscheck: 126/126 machine-checked; mutation test ALL CAUGHT (incl. 4 hard corruptions x 22 reviewed rows);
  site_smoke_test 34/34 (made unchecked-row check conditional, added P22b callout check); previewer_nav_test 14/14; screenshots reviewed.
- NOT done: any comparison with the PDF (NASA download blocked by network; no PDF attached). Still 0 human-verified.
Decisions + why:
- "Please read" notice kept: no person has compared rows with the PDF. It disappears automatically once rows are human-verified.
Next step I recommend:
- Get the PDF (pages 103-113) for a real PDF comparison; verifier signs rows; then build Compare.
