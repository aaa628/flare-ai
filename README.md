# Flare AI

Evidence-graded fire safety insights from NASA microgravity combustion data.
Built for the **NASA Space Apps Challenge 2026: Flame in Freefall**.

> Flare AI tells a mission planner what NASA's fire experiments actually prove
> about a situation, and says "the available data is insufficient" when the
> data does not cover it.

## Open it

- **Offline:** double-click `site/index.html`. Plain HTML, CSS and JavaScript with relative links; works from disk with no internet.
- **Local server:** `python3 -m http.server 8000 --directory site`, then open http://localhost:8000.
- **Demo host:** Netlify (publish directory `site`, no build; config in `netlify.toml`). Steps in [`docs/DEPLOY.md`](docs/DEPLOY.md).

`raw.githubusercontent.com` is not a website host (it serves files as plain text), so `index.html` no longer points at it.

## Current data status (generated `site/data/data.js`)

| | Count |
|---|---|
| Test records | **263** from **6** NASA sources |
| Human-verified (a person compared the record with NASA's source and signed it) | **0** |
| Machine-checked (automated checks against NASA's PDF or data file; not "verified") | **263** |
| Unchecked (hidden unless the team preview is on) | **0** |

| Experiment family | Records | Source | How it was checked |
|---|---|---|---|
| BASS-II | 126 | NASA/TM-20210011385 report, Appendix A (NTRS) | matches the PDF value for value (126/126); 123 also agree with NASA's PSI spreadsheet, 3 disagreements (F3, P22b, P3a) shown on those records; 22 flagged rows passed via a written row-by-row review |
| BASS-II | 3 (O20-O22) | NASA PSI-25 experimental table (DOI 10.60555/4qc4-de67) | copied from NASA's file, re-read on every build; not in the report |
| BASS-I | 121 | NASA PSI-26 As Run Test Matrix (DOI 10.60555/58h4-dy80) | copied from NASA's file, re-read on every build |
| SAFFIRE-I / II / III | 2 / 9 / 2 | NASA PSI-98/99/100 experimental tables | copied from NASA's file, re-read on every build |

The three families recorded oxygen differently (calibrated chamber sensor / logged station O2 as a fraction / approximate values),
so they are **never pooled into one chart or comparison**. Details: [`data/README.md`](data/README.md).

## Principles (non-negotiable)

1. **No invented numbers.** Every statistic is computed from records in `data/`.
2. **Every fact is labelled** as Measured, Published conclusion, or Our interpretation.
3. **Never compare incompatible measurements.** Compare refuses across experiments and says why.
4. **Abstain outside tested conditions.** Show the closest real experiments instead of guessing.
5. **No fire probabilities, no safety certification.** This is a research-navigation tool.
6. **Every record cites its source** (report table and page, or NASA data file and row, with DOI).
7. **"Machine-checked" is never presented as "verified".** Verified = a person compared the record with NASA's source and signed `verified_by`/`verified_date`. Every record shows its level with a glyph and a label (✓ verified, ◇ machine-checked, ! unchecked), never colour alone.

## Screens

| Screen | Status | What it does |
|---|---|---|
| Overview | built | What the site can answer, one primary action; dataset status that separates **human sign-off (0 of 263)** from each automated check with exact counts; the three experiment families and how each was measured; two question-led charts with "how to read" and "included / left out" notes |
| Flame Explorer | built | Search and filters with active-filter chips and one-click reset, record count next to the filters, sticky headings, rows open with click or Enter, stacked cards on phones; O2 start tagged with its method |
| Test pages | built | One header with identity, check status, sign-off state, source reference and actions (open NASA's PDF at the page, or NASA's dataset page + the exact NASA file served by this site + DOI); flags; a provenance table (value, NASA's field name, unit as recorded, conversion); technical setup and raw text lower down |
| Compare | built | Worked, limited and refusal examples for first-time users; "before charting" panel (source, method, units, missing/suspect fields); start/end bars, change chart, flow-direction donut; each chart lists what it left out, tagged by reason; refusals list which conditions failed (experiment, oxygen method, units) |
| About | built | Rules, all sources, known limits, AI disclosure |
| Intelligence Lab | planned | Question answering over the records with an evidence grade |
| Scenario Check + PDF brief | planned | Explainable nearest-test screening that abstains |

## How the data flows

```
NASA report PDF/text --extract_bass2.py--> data/bass2_draft.csv --crosscheck_bass2.py, pdfcheck_bass2.py, psicheck_bass2.py--+
NASA PSI files (data/source/psi/) --import_psi.py--> data/bass1_psi.csv, saffire_psi.csv, bass2_psi_extra.csv -----------+
                                                         build_site_data.py (re-runs the checks) --> site/data/data.js --> site/
```

Run the smoke and previewer tests after any UI or routing change, and check the hosted site on desktop and phone.
After any data change run `python scripts/build_site_data.py` (needs `pip install openpyxl`; the PDF comparison also
needs `pdftotext` from poppler-utils) and commit `site/data/data.js`. A person verifies a record by comparing it with
NASA's source and filling `verified_by` and `verified_date`; the checklist is in [`data/README.md`](data/README.md).

## Repo layout

```
site/            the website: index.html, css/style.css, js/app.js, data/data.js (generated),
                 sources/psi/ (byte-identical copies of NASA's PSI files, copied by build_site_data.py)
data/            working CSVs, sources.csv, source/ (report text + NASA PSI files), README.md
scripts/         extract_bass2.py, crosscheck_bass2.py, pdfcheck_bass2.py, psicheck_bass2.py, import_psi.py, build_site_data.py
tests/           site_smoke_test.py, previewer_nav_test.py, crosscheck_mutation_test.py, pdfcheck_mutation_test.py, psi_import_test.py
docs/            DEPLOY.md, HANDOFF_PROMPT.md (full brief for any AI), WORKLOG.md (append-only log)
netlify.toml     static hosting config (publish site/, security headers)
```

## Tests

```bash
pip install playwright openpyxl
python scripts/build_site_data.py
python tests/site_smoke_test.py            # 69 browser checks: sign-off vs automated checks, provenance, source links, filters, Compare examples and refusals, text alternatives, 390px
python tests/previewer_nav_test.py         # in-app links survive an injected <base> tag
python tests/crosscheck_mutation_test.py   # the cross-check catches corrupted rows
python tests/pdfcheck_mutation_test.py     # the PDF comparison catches corrupted rows
python tests/psi_import_test.py            # edited PSI records drop to unchecked
```

## Team

Studio 628 / 628 Aerospace. NASA Space Apps 2026 (virtual). NASA does not endorse this project.

## AI-use disclosure

Developed with AI assistance (Claude). The team reviews, verifies and can explain all data, code and claims.
Check the official Participant Guides (released Nov 13) for current rules on AI use and pre-built code.
