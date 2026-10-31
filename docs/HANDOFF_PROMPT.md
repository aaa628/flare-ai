# HANDOFF PROMPT: Flare AI (paste this whole file into the new AI)

You are taking over an in-progress hackathon project. Read ALL of this before touching anything.
Where this file and the repo disagree, **the repo is the truth**; fix this file and tell the user.

---

## 1. Who you are working for

- A team of **three high-school students** (one lead who talks to you, two friends). Virtual participants.
  Lead's timezone: IST (UTC+05:30). They can recruit one outside specialist (e.g. UI designer) if you name the skill.
- They are **not experts**. Explain things plainly. They must be able to **explain every number, model and
  claim to judges without you**. Never build something they cannot defend.
- Stack: Python data scripts + a **static website** (plain HTML/CSS/JS, no build step, no framework, no backend, opens by
  double-clicking `site/index.html`). Streamlit was tried first and REMOVED (hard for the team to run/ship). Do not
  reintroduce Streamlit, and do not add React, FastAPI or Postgres.
- The lead's goal: **win** the NASA Space Apps Challenge 2026, challenge **"Flame in Freefall: AI-Powered
  Fire Safety Insights from Microgravity Combustion Data"**.
- Brand: product name **Flare AI**, shown under the **628 AEROSPACE** header (studio name "Studio 628").
  The lead's earlier mockup nav concept: Overview, Flame Explorer, Research Library, Comparative Analysis,
  Intelligence Lab, Safety Insights, Reports, Settings. We agreed to CUT it down (see section 4).

## 2. Hackathon facts (verify against official guides when they drop)

- Event: **Nov 14-15, 2026**. Project submission opens Nov 14, 9:00 a.m. local time; one source says it closes
  Nov 15, 11:59 PM local (**unconfirmed, check the official guide**).
- Official **Project Submission Guide** and **Judging & Awards Guide** are released **Nov 13**. READ THEM FIRST
  when available: they set the real judging criteria and the rules on AI use and pre-built code.
  **Do not assume either; tell the user to check.** The team keeps AI use disclosed (it is in README/About).
- Challenge brief (paraphrased): NASA has decades of microgravity flame experiments; the volume makes them
  hard to find, compare and understand; build an **interactive, AI-powered dashboard that summarizes, ranks
  and interprets findings to deliver fire-safety insights for human space exploration** (Moon/Mars).
- Official challenge page (could not be fetched by the previous AI; open it yourself):
  https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall-ai-powered-fire-safety-insights-from-microgravity-combustion-data/
- Many other teams are building near-identical "dashboard + cited chatbot" apps (public GitHub repos exist).
  **Our differentiator is trust**, not features: evidence grading, honest abstention, visible method.

## 3. The product idea (what Flare AI is)

> A dashboard that tells a mission planner what NASA's fire experiments actually prove about a given
> spacecraft situation, **and says "the available data is insufficient" when the data doesn't cover it.**

Non-negotiable principles (also in README.md):

1. **No invented numbers.** Every statistic is computed from records in `data/`. Nothing hardcoded.
2. **Every field is labelled** `measured`, `published_conclusion`, or `our_interpretation`. Keep them separate on screen.
3. **Never compare incompatible measurements** as if equivalent (different quantity/unit/method). The Compare
   screen must refuse and explain.
4. **Abstain outside tested conditions.** Show nearest real experiments instead of guessing.
5. **No fire probabilities. No safety certification.** It is a research-navigation tool.
6. **Every record cites its source** (NTRS id + page).
7. Unverified rows are **never shown as findings**.

## 4. Scope (Mark 1). KEEP vs CUT

KEEP, 5 screens + About:

| Screen | Purpose |
|---|---|
| Overview | Intro + real counts computed from verified records, featured experiment, 3 key findings, quick links |
| Flame Explorer | Search/filter (fuel/material, gravity env, program), experiment detail page with conditions, observations, source link. Each field tagged measured / published_conclusion / our_interpretation |
| Compare | Pick 2-3 experiments, side-by-side table + one chart, missing-data flags; refuse incompatible comparisons |
| Intelligence Lab | Q&A answering ONLY from verified records + cited NASA papers. Each answer: evidence grade (strong / thin / none), documents used, "insufficient data" when appropriate. Retrieval (keyword/TF-IDF in JavaScript) over verified records. A static site has no backend, so **no LLM calls from the browser** (an API key would leak); an optional serverless function could be added later. Must work with no API key |
| Scenario Check + Brief | User picks environment + material; an explainable model (nearest-neighbour in JavaScript, or a small tree trained offline in Python and exported as JSON) predicts spread vs extinction **or abstains** when outside tested range; one button exports a PDF brief with citations. Never claims probabilities or safety |
| About | Sources, credits, limitations, AI-use disclosure |

CUT (do not rebuild unless the user insists): React/TypeScript/FastAPI/PostgreSQL; a Settings page; bookmarks;
research-activity feed; a separate Research Library page (merged into per-experiment source links);
Safety Insights as its own page (merged into Scenario Check); many chart types.

Visual identity: dark "mission control" look (reference screenshots were dark dashboards: navy/black, orange/coral
accent, teal secondary). Theme tokens are CSS variables at the top of `site/css/style.css`: accent `#ff6a2b`, bg `#0a0e17`,
panel `#121826`, text `#e6ebf5`; label colours measured teal, published blue, interpretation amber. Header strip: "628 AEROSPACE · SYSTEM ONLINE". Charts are plain
inline SVG (no chart library). A designer polishes in the last week.

## 5. Repo: `https://github.com/aaa628/flare-ai` (branch `main`, private for now)

```
flare-ai/
├── README.md                    principles, how to open the site, data flow, tests
├── site/                        THE WEBSITE (static; double-click index.html)
│   ├── index.html               shell: header (628 AEROSPACE · SYSTEM ONLINE), nav, footer
│   ├── css/style.css            dark theme, all design tokens as CSS variables
│   ├── js/app.js                hash router + views: Overview, Flame Explorer, test detail, About
│   └── data/data.js             GENERATED by scripts/build_site_data.py (window.FLARE_DATA). Never hand-edit
├── data/
│   ├── README.md                pipeline, verifier checklist, columns, known limits  <- READ IT
│   ├── bass2_draft.csv          126 BASS-II test rows; THE working sheet; all UNVERIFIED so far
│   ├── sources.csv              1 row (BASS-II report)
│   └── source/TM-20210011385.txt  plain-text export of the NASA report (extraction input)
├── scripts/
│   ├── extract_bass2.py         parses Appendix A -> bass2_draft.csv (OVERWRITES it; deterministic)
│   └── build_site_data.py       bass2_draft.csv + sources.csv -> site/data/data.js
├── tests/site_smoke_test.py     Playwright headless-browser checks (29 pass at last run)
└── docs/  HANDOFF_PROMPT.md (this file), WORKLOG.md (append-only log)
```

**Verified-only rule:** `scripts/build_site_data.py` sets `verified = true` only when `verified_by` AND `verified_date`
are non-empty; `site/js/app.js` shows only verified rows unless the URL has `?preview=draft`, which shows everything under
a loud red "UNVERIFIED" banner on every page. Do not weaken this. Pairs (`P3a`/`P3b`) are sorted naturally.

Blank/"—" in the UI = the source doesn't state it. **Never estimate.** The detail page shows three labelled sections
(Measured readings and log note; Published conclusion; Our interpretation) plus a Source card (report, Appendix A table,
page, verification status).

## 6. The data (be precise)

Source: **NASA/TM-20210011385**, *Burning and Suppression of Solids-II (BASS-II) Summary Report*
(Olson, Ferkul, Bhattacharjee, Miller, Fernandez-Pello, Link, T'ien, Wichman; Oct 2021).
https://ntrs.nasa.gov/citations/20210011385 . ISS Microgravity Science Glovebox small flow duct; samples burned
under varied O2 level, ventilation, fuel type/thickness/geometry. Report abstract (paraphrased): heat release
mostly < 100 W, global equivalence ratio about 1.3 (fuel-rich).

`data/bass2_draft.csv`: **126 rows** from Appendix A, Tables A.1-A.6 (one table per investigator:
B=Bhattacharjee 22 rows, F=Ferkul 4, P=Fernandez-Pello 27, M=Miller 20, O=Olson 24, T=T'ien 29).
IDs like `BASSII-B1`; pairs appear as `a`/`b` (`P3a`, `P3b`). Columns: id, pi, as_run_no, sample_no,
material_raw, flow_mode, o2_cal_initial/final, o2_raw_initial/final, co2_initial/final, co_initial_ppm/final_ppm,
observation, setup_raw, source_page, qc_flag, parse_ok, verified_by, verified_date, verifier_notes, raw_text.
qc_flag values: hand_keyed, o2_final_reading_suspect, flow_mode_not_stated, o2_final_not_numeric, material_check.
`material_raw` was once polluted with igniter/flow text for 62 rows; fixed (regex splits material | igniter | flow-restrictor+mode).
Re-running extract_bass2.py overwrites verifier edits, so only re-run it before verification starts.

**Everything in it is an unverified draft.** Known facts and traps:

- **Missing IDs:** P7, P11, T8 do not appear in the text export. They may exist in the PDF. Do not invent them.
- **Hand-keyed rows** (`qc_flag=hand_keyed`, `parse_ok=manual`): M5, O16, T3. Irregular PDF layout.
- **Suspect O2 readings** (`o2_final_reading_suspect`): B2, F3, P22a, P22b, M5, T28a, T28b. NASA's own table has
  glitch values (e.g. 20.8 -> 0.6, ~40). **Keep as printed; do not "fix".** Exclude from numeric analysis, or flag.
- **Values are strings as printed** (e.g. `+OR`, `>500`, `failed`, `Over`, en-dash minus `–1`). Parse carefully.
- **No usable flow-velocity (cm/s) column.** Report gives fan/potentiometer settings; some rows have velocities in
  parentheses; formats differ by investigator. Raw text is in `setup_raw`. **Do not treat fan settings as velocities.**
- **No pressure** per test in these tables. **No `outcome`** (spread / extinguished / marginal) yet: coding it is
  *interpretation*, must be labelled `our_interpretation`, and must quote the supporting observation.
- Observation text is NASA's test-log notes. The site labels it **Measured** ("as recorded in the log").
- O2 columns: "calibrated" = calibrated against the station's gas analyzer; the site shows both calibrated and raw columns and the Overview chart uses `o2_cal_initial`.
  Confirm the meaning of calibrated vs raw in the report text (Section 1.3 / Appendix B) before making claims.
- Other sources (NOT yet pulled): NASA PSI psi.nasa.gov (CC0; BASS, BASS-II, Saffire, FLEX investigations),
  NTRS 20160000593 (2014 conference summary; **has no per-test table**, only experiment-level summaries and the
  finding that at airflow below ~1 cm/s flames can persist as dim steady blue flames but can flare up if flow
  rises). Saffire (unmanned spacecraft-scale fires) is a strong cabin-fire-relevance source worth adding.

## 7. Current status

DONE (repo `aaa628/flare-ai`, branch `main`):
- Static site built and browser-tested (Overview with computed counts + SVG charts, Flame Explorer with search/filters,
  per-test detail pages with evidence labels and source card, About; mobile-safe; zero console errors; 29/29 smoke checks).
  Tested via file:// in headless Chromium. Not yet seen by the team on their own machines.
- 126 BASS-II rows extracted with page citations and QC flags; none verified.
- Streamlit prototype deleted.

NOT DONE (priority order):
1. **Human verification** of `data/bass2_draft.csv` (the user's data-verifier friend). Gates everything. An AI must NOT stamp `verified_by`.
   Helpful AI work: a verification helper UI/printable checklist.
2. Team opens `site/index.html` (and `?preview=draft`) on their own machines and reports problems.
3. Add `sources.csv` rows as sources are used (e.g. NTRS 20160000593 conference summary, Saffire reports, PSI investigations).
4. **Compare** page: pick 2-3 tests, side-by-side table + one chart, missing-data flags, REFUSE incompatible comparisons
   (e.g. different quantity/unit/method; fan settings vs true velocities). Add to nav (currently a "soon" placeholder).
5. **Outcome coding** (team-reviewed) so Scenario Check has labels; store a `coding_rationale` quote; label `our_interpretation`.
6. **Scenario Check**: explainable nearest-neighbour screening over (O2 level, flow mode, material class), with abstention and
   the tested range stated. ~126 rows, no clean velocity, no pressure: do not claim predictive accuracy you cannot cross-validate.
7. **Intelligence Lab**: in-browser keyword/TF-IDF retrieval over verified records + paper text; visible evidence-grade rule
   (strong/thin/none); "insufficient data" answers; pre-test the ~10 pitch questions. No browser-side LLM calls.
8. **PDF brief**: simplest robust route is a print stylesheet + `window.print()`, or jsPDF vendored locally.
9. Polish, deploy (static host: Netlify/Vercel/Cloudflare Pages deploy a private repo free; GitHub Pages needs a public repo),
   2-minute demo video, pitch script, slides, submission.

## 8. Planned timeline (from Oct 31)

- Oct 31 to Nov 6: data extraction + verification, model, retrieval.
- Nov 7 to Nov 13: app screens, brief generator, polish. **Nov 13: read the official guides.**
- Nov 14 to 15: finish, record demo, **submit well before the deadline**.

## 9. How you must work

- **Never fabricate** data, sources, citations, statistics, quotes or results. If you can't find it, say so.
- If you quote NASA text, keep it short; prefer paraphrase plus page citation.
- Small, reviewable commits with clear messages. Do not rewrite history. Do not commit secrets or API keys.
- Keep to the stack. Prefer boring and robust over clever: this must not break on stage.
- Anything the app asserts must be traceable to a verified row. Add unit-style sanity checks for data code.
- When you change schema, scripts, structure or decisions, **update `data/README.md` and this file in the same commit**.
- Before saying something works, **run it**. If you couldn't run it, say "not run".
- Don't make the user dependent on you: explain what you build in plain language.

### Worklog protocol (important: the previous AI, "Claude", will be re-reading this repo)

Maintain `docs/WORKLOG.md`. After every working session **append** an entry:

```
## YYYY-MM-DD HH:MM IST - <AI name/model>
Did: <bullets, concrete, with file paths>
Verified by running: <what you actually ran and the result, or "not run">
Decisions + why: <bullets>
Open problems / assumptions: <bullets>
Next step I recommend: <1-3 bullets>
```

Be factual. Do not delete old entries. This is how work stays continuous across AIs.

## 10. Environment notes from the previous AI (may not apply to you)

- Its sandbox blocked PyPI (so Streamlit could never be run there, one reason for the move to a static site); `gh repo create` (GraphQL) was blocked; pushing needed the
  Claude GitHub App installed on the user's repo. NASA PDF hosts were blocked from the sandbox, so the PDF was
  supplied by the user as a compressed text export (kept in `data/source/`).
- If you have the same limits, ask the user to attach files or run commands locally and paste results.
- The text export flattens PDF tables; always keep `raw_text` and page numbers so humans can verify against the PDF.

## 11. Pitch story (so the product serves it)

1. Hook: fire behaves differently without gravity (no buoyancy: flames can be dim, blue, spherical, persist at very low
   airflow, and flare up if airflow rises).
2. Problem: decades of NASA results are scattered and hard to compare for mission planners.
3. Solution: Flare AI organizes verified NASA test records, grades the evidence, and refuses to guess beyond it.
4. Demo (2 min): Overview real counts -> Explorer record with source and labels -> Compare (including a refusal) ->
   Intelligence Lab answer with evidence grade and an "insufficient data" case -> Scenario Check + PDF brief.
5. Honesty slide: what we verified, how, and exactly what the data cannot tell you.

## 12. First thing to do when you start

1. Read `README.md`, `data/README.md`, this file, and `docs/WORKLOG.md` if it exists.
2. Ask the user: "Has anyone run the app? Has verification started (how many rows)? What are the exact errors?"
3. Do the highest-priority NOT DONE item that is unblocked. Log it in `docs/WORKLOG.md`.
