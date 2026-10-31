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

## 2026-10-31 21:30 IST - Claude
Did:
- User allowed ntrs.nasa.gov + psi.nasa.gov in the network settings. Downloaded the official PDF (NTRS 20210011385, 144 pages,
  tables on PDF pages 111-121) to data/raw/ (git-ignored).
- scripts/pdfcheck_bass2.py: compares every row with the PDF text layer (pdftotext): page, row line, 8 readings, material, full note.
  126/126 match after fixing a text-export bug: byte 0x02 instead of a hyphen in 8 materials + 2 notes (see data/README.md).
- tests/pdfcheck_mutation_test.py: 5 corruptions x 126 rows, all caught.
- build_site_data.py re-runs the PDF comparison when the PDF is present; counts.pdf_match. Site: amber "Please read" box replaced by a
  one-line note ("126 of 126 records match NASA's original PDF ... team sign-off in progress"); detail pages say the row matches the PDF.
- Confirmed from the PDF: column order of the O2 columns; P7, P11, T8 absent from the tables.
- PSI (psi.nasa.gov) now redirects to science.nasa.gov, which is still blocked; the public AWS bucket nasa-psi has no combustion data
  (only DSI, OASIS, PK-4).
Verified by running: pdfcheck 126/126; pdfcheck_mutation ALL CAUGHT; crosscheck 126/126 + mutation ALL CAUGHT; smoke 34/34;
  previewer 14/14; screenshots of Overview and B14 reviewed; P1 compared by eye with the PDF page image.
Decisions + why: rows stay "machine-checked" (automated), never "verified"; that stays a person's signature.
Next step I recommend: allow science.nasa.gov for PSI data; pull Saffire reports from NTRS; build Compare.

## 2026-10-31 23:00 IST - Claude
Did:
- PSI reachable after the user allowed science.nasa.gov. Found the PSI JSON API; listed 24 combustion investigations; downloaded
  the small files (tables, docs) for BASS-II (PSI-25), BASS (PSI-26), SAFFIRE-I/II/III (PSI-98/99/100). Raw video/images (100s of GB) skipped.
- scripts/import_psi.py -> data/bass1_psi.csv (121), data/saffire_psi.csv (13), data/bass2_psi_extra.csv (O20-O22, PSI only).
- scripts/psicheck_bass2.py -> psi_check column: 123/126 agree with NASA's PSI spreadsheet; 3 real disagreements (F3, P22b, P3a) shown.
- build_site_data.py merges all; PSI rows machine-checked only if they still equal the source file. 5 sources added to sources.csv (DOIs).
- Site: Experiment column + filter, per-row source card with DOI, generic detail page for PSI rows, "NASA's two sources disagree"
  callout, overview chart by experiment, O2 chart restricted to BASS-II (one measurement method per chart), About lists all sources.
Verified by running: import 121/13/3; psicheck 123/126; pdfcheck 126/126; crosscheck + pdfcheck + psi_import tests ALL CAUGHT;
  smoke 38/38; previewer 14/14; screenshots of overview, explorer (SAFFIRE-II filter), BASS-I detail, P3a detail reviewed;
  P3a/P22b checked against the PDF page image.
Decisions + why: PSI rows labelled machine-checked (copied from NASA files, re-read every build), never verified. O2 never compared
  across experiments (different methods).
Open problems: 0 human-verified. BASS-I "Air display" and SAFFIRE airflow shown as logged; not yet used in any comparison.
Next step I recommend: merge PR; build Compare (same experiment + same column only); then Intelligence Lab.

## 2026-11-01 00:30 IST - Claude
Did:
- PR #3 was merged; continued on branch claude/stoic-pasteur-c8vrts from main (fast-forward of the old branch).
- Built the Compare screen (site/js/app.js viewCompare, CSS block at end of style.css, nav link enabled; "Compare with other
  tests" link on every test page). Pick 2-4 tests; presets incl. "A comparison Flare AI refuses".
- Charts: grouped start/end bars per measure (BASS-II: calibrated O2, raw O2, CO2, CO; BASS-I: O2, pressure, CO2;
  SAFFIRE: air flow, ignition power/time, burn time), diverging "change during the test" bars, flow-direction donut for the
  experiment, shared hover tooltip, side-by-side table.
- Rules: refuses across experiments; excludes flagged O2 and non-numeric/approximate values with reasons; caution on differing
  flow direction/material; no averages. User asked for pie charts: used one donut for the only true part-to-whole view
  (flow-direction mix); comparisons use bars (pies mislead for close values).
Verified by running: dataviz validator (dark, surface #191a1d) PASS for 4 categorical slots and the fell/rose pair;
  smoke 44/44 (6 new Compare checks); previewer 14/14; screenshots of 4 compare states reviewed; 390px: no horizontal scroll.
Next step I recommend: Intelligence Lab (in-browser retrieval with evidence grade), then Scenario Check + PDF brief.

## 2026-11-01 01:30 IST - Claude
Did:
- PR #4 merged; branch fast-forwarded to main. Restyled the Compare screen after the user's dashboard reference images:
  toolbar with pill selects, test chips + dashed preset chips, summary pills (experiment, tests, values charted, left out),
  stat tiles per test (first tile highlighted in the accent colour; tiny glyph drawn from that test's own values), card headers
  with icon badges and unit pills, bars with gradient + soft glow (start) and hatched texture (end), dashed gridlines with y
  ticks, pill-track change chart, thicker donut with hub and value legend, "How this comparison works" checklist card,
  refusal card. CSS block at the end of site/css/style.css replaced; colours unchanged (validated palette).
- Fixed: y-axis ticks could stop below the tallest bar (raw O2 at 16.6 clipped at 15).
Verified by running: smoke 46/46 (new: axis not clipped, no horizontal scroll at 390px); previewer 14/14; screenshots of
  4 states + 390px reviewed.
Next step I recommend: Intelligence Lab (user still to choose: Claude-backed function vs search only).

## 2026-11-01 03:00 IST - Claude
Did:
- Hosting conflict resolved: site/index.html back to relative asset links (offline + any static host); netlify.toml (publish site/,
  no build, CSP + nosniff headers); docs/DEPLOY.md (offline, local server, Netlify Drop / Git, alternatives, why not raw GitHub).
- Evidence status: shared LEVEL vocabulary; chips carry glyphs (✓ verified, ◇ machine-checked dashed, ! unchecked); compact legend
  with counts at the top of Overview and Explorer; test pages get one Evidence card (how it was checked + source evidence).
- Overview: hero groups headline, explanation, "what this site can answer", one primary action, dataset status + legend; table of the
  three experiment families and how each was measured; question-led charts with units and how-to-read lines.
- Explorer: active-filter chips with remove + "Reset all", count beside them, warning when the O2 filter spans experiments, sticky
  headings (scrolling table), rows focusable and open on Enter, arrow column, hint line, O2 method tag, stacked cards under 700px.
- Compare: "Before charting" panel (source, oxygen method, other values/units, check level, missing/suspect per test); each chart says
  what it left out right under it; refusal shows the differing methods; how-to-read on every chart; SVG title + aria-label summaries.
- Docs synced to the generated data (README rewritten, data/README status table, HANDOFF).
Verified by running: smoke 59/59 (new checks for legend counts, primary action, families table, filter chips, sticky header, Enter
  opens a row, evidence card, before-charting panel, per-chart limits, text alternatives); previewer 14/14; crosscheck, pdfcheck,
  psi_import tests ALL CAUGHT; CSP from netlify.toml served locally: no errors; screenshots at 1280px and 390px reviewed, no overflow.
Not done: actual Netlify deployment (needs the user's Netlify account).

## 2026-11-01 04:00 IST - Claude
Did (whole-repo review after PR #6 merged):
- Fixed: crosscheck_bass2.py and extract_bass2.py read the NASA text without encoding="utf-8" (on Windows the em dash in
  "Appendix A.—Test Matrices" would not match and the build would crash); extract_bass2.py also wrote the CSV without utf-8.
- extract_bass2.py now refuses to overwrite data/bass2_draft.csv without --force, and maps byte 0x02 to "-" itself. Verified: a
  fresh --force extraction reproduces the committed data fields exactly (sheet restored afterwards).
- Phone nav wraps instead of hiding links off-screen; "soon" placeholders hidden under 700px.
- Removed dead code (unused go(), tbl, src). Stale doc lines fixed (data/README Compare line, HANDOFF test counts/tree/limits);
  CONTINUATION_SUMMARY marked as a historical snapshot.
Verified by running: all 263 record pages + 10 Compare combinations + 4 main pages opened: no JS errors, no undefined/NaN in text;
  full pipeline re-run reproduces committed data; smoke 59/59; previewer 14/14; 3 tamper tests ALL CAUGHT.
Not checked: the live Netlify site (netlify.app is not in this session's allowed network domains; URL not known yet).
Open: no LICENSE file (team decision).

## 2026-11-01 05:30 IST - Claude
Did:
- Overview dataset status: separate, prominent "Human sign-off: 0 of 263" box, then each automated check with exact counts (126/126
  PDF match, 123/126 PSI agree + the 3 disagreements named, 22 row-by-row reviewed, 137 re-read from NASA files). Same on About.
- Source attribution: build copies NASA PSI files to site/sources/psi/; every record links to its source (report: NASA PDF at the
  page; PSI: dataset page on psi.nasa.gov, the exact file, DOI) with file/sheet/row shown.
- Provenance table on every test page: value, NASA's field name, unit as recorded, method/conversion (BASS-I O2 header says "%" but
  stores fractions -> x100; SAFFIRE-II O2 from CO2 per NASA's Note 1; BASS airflow = fan settings, not converted).
- Test page hierarchy: one record header (identity + check status + sign-off state + source reference + actions); readings and log
  note next; provenance; labels; technical setup and raw text collapsed at the bottom.
- Compare: worked / limited / refusal example cards (empty state + drawer); refusal lists failed conditions; each chart's left-out
  list tags the reason (suspect reading, missing value, unconfirmed, approximate, not a number).
- Overview charts: "included / left out" notes with exact counts. Favicon (data URI) added.
Verified by running: smoke 69/69; previewer 14/14; all 263 record pages + Compare combos + main pages: no errors; tamper tests ALL
  CAUGHT; netlify.toml CSP served locally: no errors; 1280px and 390px screenshots, no overflow.
Not checked: the hosted Netlify site (URL unknown; netlify.app not in this session's allowed domains).

## 2026-11-01 07:00 IST - Claude
Did:
- Challenge page and its mirrors are blocked here; public repos of other teams consistently cite NASA PSI with BASS-II (PSI-25) and
  FLEX (PSI-69) as the challenge datasets. Added FLEX from PSI-69 (274 tests; Windows-1252 CSV) via import_psi.flex_rows(); added
  PSI-68 FLEX-2 as a listed source (planned matrix only, no records). sources.csv now 8 rows; 537 records.
- Site: FLEX in Explorer (mol% tag), Overview families table + "How did FLEX droplet fires end?" chart (NASA's labels), Compare
  measures (O2 mole fraction, pressure, droplet/extinction diameter, burn time), donut shows NASA's test end for FLEX, worked example,
  provenance rows (lost-subscript reading labelled as our interpretation), flag callouts (pressure printed as 0, duplicate identifier).
Verified by running: import 274 rows; build 537/537 machine-checked; smoke 72/72; previewer 14/14; tamper tests ALL CAUGHT; all 537
  record pages + Compare + main pages: no errors; CSP served locally: no errors; 1280/390 px screenshots, no overflow.
Not verified: the official challenge resource list itself (spaceappschallenge.org not reachable from this session).

## 2026-11-01 09:00 IST - Claude
Did:
- Found that PR #7 had been merged before the FLEX commit was pushed; opened PR #8 for FLEX (I had wrongly said #7 included it).
- Challenge Details text (pasted by the user) drives the next build. Resources tab: "available Friday, November 13".
- scripts/fetch_psi_catalog.py: PSI metadata (verbatim fields) + experiment tables for all 24 Combustion Science investigations
  -> data/source/psi/catalog/, data/source/psi/tables/. data/investigations_curated.csv: our labels with basis.
- scripts/build_catalog.py: per-table O2 / pressure ranges from named columns, psi conversion, Moon-base-zone test counts,
  lowest pressure among >=30% O2 tests, unparsed cells listed. build_site_data.py adds D.investigations and serves the tables.
- Site: Investigations page (lens Spacecraft/ISS vs Moon base/rover, ranking with printed rule + per-point evidence, filters,
  O2-range and O2-vs-pressure charts with the brief's zone, computed insight), investigation detail pages, investigation compare.
  Test pages link to their investigation; Overview lists the new question.
- Fixed: svg() helper now accepts numbers; class "top" clashed with the header (renamed "podium").
Verified by running: build_catalog (24); smoke 79/79 (incl. all 24 investigation pages); previewer 14/14; tamper tests ALL CAUGHT;
  all record pages: no errors; investigations pages at 1280/390 px: no errors, no overflow.

## 2026-11-01 11:30 IST - Claude
Did:
- Intelligence Lab (user chose Claude, asked for strong key security): Netlify Function netlify/functions/ask (core.mjs logic,
  ask.mjs entry). Key only in Netlify env var ANTHROPIC_API_KEY (Functions scope, secret). POST-only, origin check, 300-char cap,
  per-IP 8/h 25/day + global 400/day via Netlify Blobs, 24 h answer cache, fails closed if the store is down. BM25 retrieval over a
  generated corpus (691 docs) server-side; claude-opus-5-5, effort low, structured JSON output, fallbacks "default"; citations
  validated against retrieved ids (invalid points dropped); evidence grade by a fixed rule; abstains; refusal -> abstained.
- Lab page #/lab: examples incl. one that must abstain, basis labels, citation chips to records/investigations, grade rule, gaps,
  retrieved documents, keyword-search fallback offline / on errors / at limits.
- Investigations: need tabs (prevention/detection/suppression, labelled Flare AI classification) + inline habitat switch; coverage
  levels and known gaps (no partial gravity, no prediction claim); audit table of every study the brief names; score inputs
  inline with source tags (NASA data / Flare AI label / brief) and "relevance, not safety"; evidence type badges; plain-language
  summaries (ours) + NASA's stated impact on detail pages; compare adds summary, coverage, geometry, airflow column, measurements.
Verified by running: lab_function_test 18/18 (fake client); SDK request shape checked with a stub fetch (header + body);
  lab_ui_test 11/11 (simulated server); smoke 85/85; previewer 14/14; tamper tests ALL CAUGHT; all record pages OK; CSP OK.
Not verified: a real Claude call (no key in this session) and the deployed function on Netlify.
