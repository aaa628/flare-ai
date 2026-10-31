# Flare AI

Evidence-graded fire safety insights from NASA microgravity combustion data.
Built for the **NASA Space Apps Challenge 2026: Flame in Freefall**.

> Flare AI tells a mission planner what NASA's fire experiments actually prove
> about a situation, and says "the available data is insufficient" when the
> data does not cover it.

## Open it (no install, no server)

Double-click **`site/index.html`**. It is a static website (plain HTML, CSS, JavaScript) and works straight from disk.

- Default view shows **human-verified** and **machine-checked** rows (currently all 126 machine-checked, 0 human-verified), each labelled with how it was checked. Right now none is human-verified.
- Rows with no check are hidden. The team can reveal them with the footer link "Team preview: show unchecked rows" (or `?preview=draft`); a red banner appears on every page.

## Principles (non-negotiable)

1. **No invented numbers.** Every statistic is computed from records in `data/`.
2. **Every field is labelled** as `measured`, `published_conclusion`, or `our_interpretation`.
3. **Never compare incompatible measurements** as if they were equivalent.
4. **Abstain outside tested conditions.** Show the closest real experiments instead of guessing.
5. **No fire probabilities, no safety certification.** This is a research-navigation tool.
6. **Every record cites its source** (NTRS id, table and page).
7. **Unchecked rows are never shown as findings, and "machine-checked" is never presented as "verified".** Verified = a person compared the row with NASA's PDF. Machine-checked = an automated cross-check passed; no person has looked yet.

## Screens

| Screen | Status |
|---|---|
| Overview (real counts, charts, evidence labels) | built |
| Flame Explorer (search, filters, test detail pages) | built |
| About (rules, source, limits, AI disclosure) | built |
| Compare | planned |
| Intelligence Lab (retrieval over verified records, evidence grade) | planned |
| Scenario Check + PDF brief (explainable model that abstains) | planned |

## How the data flows

```
NASA report text ──extract_bass2.py──▶ data/bass2_draft.csv ──crosscheck_bass2.py (machine level)──▶
   (a person verifies against the PDF) ──▶ build_site_data.py ──▶ site/data/data.js ──▶ site/index.html
```

After verifying rows in the CSV, run `python scripts/build_site_data.py` and reload the site.
Details and the verifier's checklist: [`data/README.md`](data/README.md).

## Repo layout

```
site/            the website (index.html, css/style.css, js/app.js, data/data.js [generated])
data/            bass2_draft.csv (working sheet), sources.csv, source/ (report text), README.md
scripts/         extract_bass2.py, crosscheck_bass2.py, build_site_data.py
tests/           site_smoke_test.py, previewer_nav_test.py, crosscheck_mutation_test.py
docs/            HANDOFF_PROMPT.md (full project brief for any AI), WORKLOG.md (append-only log)
```

## Tests

```bash
pip install playwright && playwright install chromium
python scripts/build_site_data.py
python tests/site_smoke_test.py
python tests/previewer_nav_test.py
python tests/crosscheck_mutation_test.py   # proves the cross-check catches corrupted rows
```

## Data

Source so far: NASA/TM-20210011385, BASS-II Summary Report (NTRS). NASA does not endorse this project.

## Team

Studio 628 / 628 Aerospace. NASA Space Apps 2026 (virtual).

## AI-use disclosure

Developed with AI assistance (Claude). The team reviews, verifies and can explain all data, code and claims.
Check the official Participant Guides (released Nov 13) for current rules on AI use and pre-built code.
