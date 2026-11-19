# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

Flare AI: a NASA Space Apps 2026 "Flame in Freefall" project by 628 Aerospace (three high-school students). It is a
static, evidence-graded dashboard of NASA microgravity combustion data (24 NASA PSI investigations, 537 test records
from BASS, BASS-II, FLEX, SAFFIRE I-III) plus one serverless function, the Intelligence Lab, that answers questions only
from retrieved Flare AI documents. Live: https://flare-ai-628-by-628aerospace.netlify.app. The submission is in; judging
runs to Jan 2027, so prefer small, safe changes.

## Commands

```bash
pip install openpyxl playwright             # pdftotext (poppler-utils) is also needed for the PDF comparison
python scripts/build_site_data.py           # regenerate site/data/data.js AND netlify/functions/ask/corpus.mjs
python3 -m http.server 8000 --directory site   # or just open site/index.html (must also work from file://)

python tests/site_smoke_test.py             # main browser suite (Playwright, file://); prints "N / N checks passed"
python tests/previewer_nav_test.py          # in-app links survive an injected <base> tag
python tests/lab_ui_test.py                 # Lab page with a mocked /api/ask (launches /opt/pw-browsers/chromium)
npm install && node tests/lab_function_test.mjs   # Lab server logic with fake model clients; no key, no network
python tests/crosscheck_mutation_test.py    # data-check mutation tests (also pdfcheck_mutation_test.py, psi_import_test.py)
```

There is no build, lint or bundler for the site. Tests are plain scripts; run a single suite by running its file (there
is no per-check selector). Rebuild data before the browser tests after any change to `data/` or the build script.

## Architecture

**Data pipeline (Python, `scripts/`).** NASA sources live in `data/source/` (BASS-II report text, PSI files, saved
challenge brief/resources text). Working CSVs in `data/` (`bass2_draft.csv`, `bass1_psi.csv`, `flex_psi.csv`,
`saffire_psi.csv`, `bass2_psi_extra.csv`, `investigations_curated.csv`, `resources_curated.json`) are turned by
`build_site_data.py` into two generated files that are committed and must never be hand-edited:
`site/data/data.js` (`window.FLARE_DATA`; a .js file, not JSON, because `fetch` fails on file://) and
`netlify/functions/ask/corpus.mjs` (the Lab's search corpus, incl. the "about-flare-ai" document). The build re-runs
the automated checks every time (report-vs-PDF, PSI file re-reads, word-for-word quote checks for Lessons resources and
`BRIEF_FACTS`), so an edited row silently drops to "unchecked". `extract_bass2.py` overwrites `bass2_draft.csv`; do not
re-run it on verified data.

**Site (`site/`).** One hand-written SPA: `index.html`, `css/style.css`, `js/app.js` (a single IIFE using `h()`/`svg()`
DOM helpers and a hash router in `render()`; routes like `#/explorer`, `#/compare/ID1,ID2`, `#/investigations/moon`,
`#/investigation/PSI-25`, `#/experiment/ID`, `#/scenario/...`, `#/lab`, `#/lessons`, `#/about`; unknown `#/...` shows
"Page not found"). Everything is local: fonts and media are bundled because the CSP in `netlify.toml` allows only
`'self'` (plus frames from `www.youtube-nocookie.com`); no inline scripts, no CDNs. Decode URL parts with `dec()`, not
`decodeURIComponent`. BASS-II report records cite the report (`source_id` 20210011385), not PSI-25, so map records to an
investigation with `recsOf()`. The investigation ranking (`relevance()`), its printed rule and `MAXPTS` must stay in sync.

**Intelligence Lab (`netlify/functions/ask/`).** `ask.mjs` is the Netlify entry (`/api/ask`); it uses Google Gemini when
`GEMINI_API_KEY` is set (`gemini.mjs` adapts Gemini to the same `client.beta.messages.create` shape) and Claude only if
`ANTHROPIC_API_KEY` is set instead. `core.mjs` holds all logic with injected dependencies: BM25 retrieval with synonym
expansion, the `SYSTEM` prompt and JSON `SCHEMA`, `validate()` (drops points whose citations are not retrieved
documents, never invents citations; computes the evidence grade by rule; keeps `instead`, `general` (no digits, no
citations) and an allow-listed `action` via `safeAction()`), per-IP/global limits and a long answer cache in Netlify
Blobs. Bump the cache-key prefix in `handle()` whenever the prompt or schema changes. Netlify's free plan kills functions
at ~10 s, so the Gemini adapter stops at 8.5 s; failures fall back to keyword search on the page.

## Rules that matter here

- Never fabricate data, citations or results. Never fill `verified_by` / `verified_date`: only a person who compared a
  row with NASA's source may (the current team sign-off is "Saad & Muqeet", "2026-11-13 to 2026-11-14"). "Machine-checked"
  is never called "verified".
- Never pool or compare experiments that measured oxygen differently; abstain outside tested conditions; no fire
  probabilities or safety certifications. NASA wording, NASA records and Flare AI interpretation are always labelled.
- 2026 Space Apps rules call AI "Super Intelligence (SI)": keep SI labels/disclosures (site About, README "SI use",
  `<meta name="ai-disclosure">`, "Edited with SI" on videos). No NASA logos; nothing showing anyone under 18.
- Append an entry to `docs/WORKLOG.md` (append-only) with each change; update the relevant README/docs in the same change.
- Work on a branch and open a PR; the user merges. Netlify builds are usually set to "Stopped" to save free-plan credits,
  so merging to `main` does not deploy until the user re-enables builds.
- Demo videos are built by `docs/demo/build*.py` (Playwright screenshots + ffmpeg); keep them under 30 s.
- `docs/HANDOFF_PROMPT.md` and `data/README.md` give the full background and the data-verification procedure (some
  counts there predate the team sign-off; `site/data/data.js` is the source of truth for counts).
