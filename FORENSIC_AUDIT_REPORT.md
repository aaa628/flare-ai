# Flare AI: Forensic Audit Report

**Project:** Flare AI by 628 Aerospace. NASA Space Apps Challenge 2026, "Flame in Freefall".
**Audited build:** `main` at commit `3456ce7` (merge of PR #56). The live site, https://flare-ai-628.netlify.app, serves byte-identical `app.js`, `style.css`, `data.js` and assets; its `index.html` differs only by the two blocks Netlify injects (an HTML comment and its HUD script).
**Date:** 15 Nov 2026 (IST).
**Method:** everything below was measured. Nothing is estimated from reading alone, and every finding gives the command or test that shows it. The Intelligence Lab was **never sent a question**: every browser test intercepted `/api/*` and answered with a mock. The only live request to the function was one `GET`, which it refused with 405 before reading anything.

---

## How this audit was run (evidence base)

| Step | What was done | Result |
|---|---|---|
| Repository read | Inventory of every tracked file. Manual line-by-line reading of all logic paths in `site/js/app.js` (2,336 lines): router, Explorer, record pages, Compare, Investigations, Lab client, Scenario Check, Lessons, About. Also `netlify/functions/ask/{ask,core,gemini}.mjs`, `netlify.toml`, `site/index.html` and the design tokens in `site/css/style.css`. Automated scans of every line for DOM sinks, global listeners and secrets. | See Sections 3 to 5 |
| Live parity | SHA-1 of the live `index.html`, `js/app.js`, `css/style.css`, `data/data.js` and `img/628-emblem.svg` vs `main` | All identical except the Netlify-injected lines in `index.html` |
| Repo test suites | `site_smoke_test` (146 checks), `previewer_nav_test` (14), `lab_ui_test`, `lab_function_test.mjs` (33), three mutation tests | All pass on `main` |
| Data audit script | All 537 records and 24 investigations: schema, nulls, placeholders, encoding, duplicate IDs, foreign keys, counts, and every PSI value against NASA's original cell | Section 2 |
| Link audit | 79 unique external URLs fetched; 267 DOIs resolved through the doi.org handle API | Section 2.5 |
| Crawl | 577 live pages rendered (every route, investigation and record), visible text and ARIA text extracted | Spelling, NaN/undefined, wording |
| Torture test | 5 viewports × 13 routes, malformed URLs, 16 Scenario fuzz inputs, 10 Explorer search strings, filter combinations, 9 Compare edge cases, 7 mocked Lab failure modes, focus, keyboard, contrast, and 150-navigation listener and heap growth | Sections 3, 4 and 6 |
| Patch verification | All fixes applied in an isolated worktree. All repo suites re-run, every fix re-tested in the browser, and the new `verify-all.py` run against both versions | Sections 8 to 10 |

**Corrections to the audit brief's assumptions.** These matter, because a judge reading this report must not be misled.

- **Data format.** The data is one generated JavaScript file, `site/data/data.js` (`window.FLARE_DATA`, 1.31 MB), not a set of JSON files.
- **Routes.** There are 8 menu destinations but 12 route patterns: `#/`, `#/scenario/…`, `#/explorer`, `#/experiment/<id>`, `#/compare/…`, `#/investigations[/moon|/mars]`, `#/investigations/compare/…`, `#/investigation/<acc>`, `#/lab`, `#/lessons`, `#/about`, plus a not-found view.
- **Units.** The site uses no kPa. NASA's tables give pressure in atm (BASS-I) and mmHg (FLEX), which are converted to psi, and BASS-II has no per-test pressure.
- **Columns that don't exist.** There are no normalised "flame spread rate", "thickness" or "gravity" columns. Those appear only inside NASA's own verbatim columns.
- **UI features that don't exist.** There are no sliders (two number inputs), no modals or drawers, and no column sorting.
- **Investigations.** NASA PSI's combustion catalogue, downloaded 13 Nov 2026, lists 24 investigations. Saffire IV–VI, FLEX-2J and SOFIE are **not** among them, so their absence is correct.

---

## Section 1: Executive forensic summary and global-judge scorecard

**Bottom line:**
- **Blockers:** no P0 (crash, data loss or security hole) was found.
- **P1 (2):** one is a wrong number on the flagship investigation page, the other a navigation crash on malformed links.
- **P2 (6):** visible misprints, Lab robustness, focus handling and colour contrast.
- **P3 (15):** polish and hardening.

**Data integrity is the project's strongest asset:**
- Every one of 408 PSI-sourced records equals NASA's spreadsheet cell.
- Every BASS-II reading appears in its NASA report row.
- All 537 IDs are unique.
- Every count and chart number on the site matches the data.
- No hardcoded statistic disagrees with the arrays, and no API key appears anywhere in 142 commits.

**What's broken:**
1. The BASS-II investigation page says **"3 test records in Flare AI"** when there are **129**.
2. A malformed `%` sequence in a shared link freezes navigation.
3. Three record pages show NASA's words with a unit glued on ("+ORppm", "Overppm", "failedvol%").
4. 109 shortened texts end mid-word ("turne…", "understandin…").
5. A malformed Lab response can leave the Ask button stuck forever.
6. Focus stays on the old menu link after navigation.
7. The footer disclaimer and some small labels fall just below WCAG AA contrast.

Every one of these is fixed by the patches in Section 8, which are verified.

| Criterion | Score /10 | Exact deductions |
|---|---|---|
| **Impact** | 7 | −1: the audience (mission planners, researchers) is narrow and the site doesn't name a real user workflow such as an evidence brief for a design review (Upgrade U-02 adds one). −1: the key finding, that no solid cabin material has been tested in the Moon-base atmosphere, is stated but not made the headline. −1: no path from "gap found" to "what experiment would close it". |
| **Creativity** | 7 | −2: an evidence explorer over NASA tables is a familiar shape for data challenges. The novel parts (refusing to compare unlike data, abstention, the leave-one-out consistency check, the Moon-zone gap map) are present but under-sold. −1: no interactive regime map (oxygen × pressure × fuel family across all 24 investigations), which would be the signature visual. |
| **Validity** | 9 | −0.5: the P1 count error on the PSI-25 page contradicts the site's own 129-record figure, which is exactly what a sceptical judge clicks. −0.5: there's no single "verify" command a judge can run (Section 10 adds one). The data checks, refusal rules, unit conversions (1 atm = 14.6959 psi; 1 mmHg = 0.0193368 psi) and disclaimers are correct. |
| **Relevance** | 10 | All 24 PSI combustion investigations, 537 test records from 7 NASA files (PSI-25, 26, 69, 98, 99, 100 and NTRS TM-20210011385), and the challenge's Resources tab. NASA data is the core of the product, not decoration. |
| **Presentation** | 8 | −1: on phones the header takes 181–224 px (the 8-item menu wraps to 3 rows), pushing the headline below the fold. −1: the demo video (29.2 s) is clear but doesn't show the Moon-base gap as its climax. |
| **Total** | **41/50** | A strong local nominee, and a credible Global Finalist if the P1s are fixed and the Moon-base finding leads the story. Best-fit awards: **Best Use of Data** and **Best Use of Science**. |

---

## Section 2: Automated dataset and scientific integrity report

### 2.1 Counts (script vs the site's own `counts` block vs prose)

| Quantity | From the arrays | `FLARE_DATA.counts` | Where stated in prose | Verdict |
|---|---|---|---|---|
| Test records | 537 | 537 | Overview hero, Explorer "Showing 537 of 537", demo captions, `SUBMISSION.md` | ✅ |
| Investigations | 24 | 24 | Investigations header, Scenario table-level card ("None of the 24…") | ✅ |
| BASS-II / BASS-I / FLEX | 129 / 121 / 274 | 129 / 121 / 274 | Overview bar chart | ✅ |
| SAFFIRE-I / II / III | 2 / 9 / 2 | 2 / 9 / 2 | Overview bar chart | ✅ |
| Human-verified / machine-checked / unchecked | 537 / 537 / 0 | 537 / 537 / 0 | Dataset status panel | ✅ |
| BASS-II PDF matches / PSI agree / differ | 126 / 123 / 3 | 126 / 123 / 3 | Status panel; About ("126 records", "3 records") | ✅ |
| Sources with records | 7 (8 listed incl. FLEX-2 planned matrix with 0 records) | sources 8, with records 7 | Hero: "from 7 NASA sources" | ✅ |
| BASS-II starting-O2 bands | 5 / 24 / 46 / 22 / 27 (124 confirmed + 2 unconfirmed + 3 PSI-only = 129) | n/a | Overview chart and its included/left-out note | ✅ |
| FLEX endings | Extinction 186, Disruption 61, Completion 27 | n/a | Overview chart | ✅ |
| Highest solid-material O2 | 22.72 % (BASS-I); BASS-II max 22.2 % | n/a | Investigations: "at most 22.7% O2 (BASS-II, BASS)" | ✅ |
| FLEX max O2 and pressure there | 34 % at 10.33–10.50 psi | `p_min_psi_at_o2ge30` 10.33 | "FLEX tested up to 34% O2 but only down to 10.33 psi" | ✅ |
| Moon-zone tests (≥30 % O2, ≤10.2 psi) | ACME/Flame Design 18, ACME CFI-G 48 (across its two tables: normal and inverse flames) | `joint_tests` | Investigations, Scenario table-level card | ✅ |
| **BASS-II records shown on the PSI-25 page** | **129** | n/a | **"3 test records in Flare AI"** | ❌ **FA-01** |

### 2.2 Field-by-field schema scan (537 records, 24 investigations, recursive)

| Check | Result | Assessment |
|---|---|---|
| Duplicate record IDs / investigation accessions | 0 / 0 | ✅ |
| `null` in records | 0 | ✅ |
| `null` in investigations | 180, all in "no such column" fields (`p_min_psi`, `o2_max_pct`, `table_summaries[].p_col`…) for tables without that column | ✅ Rendered as "not in table", never as "null" (0 occurrences of "null" in 577 rendered pages) |
| Literal `"undefined"`, `"NaN"`, `"null"` strings | 0 in records; **1 in investigations**: PSI-10 publication author `"undefined undefined, FROLOV S. M."`, which is in **NASA's own catalogue JSON** | ⚠ **FA-09** (displayed verbatim) |
| Placeholders `N/A`, `TBD`, `#N/A`, `#VALUE!` | 83 × `"n/a"` in BASS-I `fields`, NASA's literal cell text (e.g. "GN2 display: n/a") | ✅ Verbatim, correct to keep |
| Untrimmed strings | 1 (`BASSII-O2.raw_text` trailing space) | ✅ Invisible |
| Broken encoding (`Ã`, `â€`, U+FFFD) | 0 | ✅ `µ`, `–`, `×`, `→`, `≥` all intact |
| NASA typos copied verbatim | "Samle" (SAFFIRE-II header), "Accidentaly", "degreees", "Comparitive", "Consistenly", "2st", "wass" | ✅ Correct for a source-faithful site |

### 2.3 Value-level verification against NASA's original files

| Source | Records | Method | Result |
|---|---|---|---|
| PSI-26 BASS-I xlsx (sheet "as run matrix") | 121 | Every shown field compared with its row's cells; values shown "(rounded)" compared within 5e-5 of the raw float | **121/121 exact** (e.g. 0.21887043… → "0.2189 (rounded)") |
| PSI-69 FLEX csv | 274 | Every field vs its row | **274/274** |
| PSI-98/99/100 SAFFIRE csv | 13 | Every field vs its row | **13/13** |
| PSI-25 BASS-II csv (PSI-only O20–O22) | 3 | Every field vs its row | **3/3** |
| NTRS TM-20210011385 Appendix A | 126 | 8 gas readings + material are tokens of the stored report row; row text present in `pdftotext` output | **126/126**. For 8 rows the stored text isn't one contiguous run in `pdftotext` output: 5 because the PDF breaks "200-µm-thick" across a line (extracted as "200-µmthick"), and 3 because of wrapped layout. Every token of those 3 is present |
| Conversions | 537 | O2 fraction × 100; atm × 14.6959; mmHg × 0.0193368 | ✅ No mixed-unit arithmetic anywhere. Compare refuses cross-experiment charts (CO2 vol% vs mm Hg) |

### 2.4 Relational integrity

| Link | Result |
|---|---|
| Record `source_id` → investigation | 411 records point at PSI accessions that exist. 126 BASS-II records point at NTRS `20210011385`, which is a **source**, not an investigation; they belong to PSI-25. The UI's `r.source_id === v.accession` therefore under-counts PSI-25. **FA-01** |
| Investigations with per-test records on the site | 6 of 24 (PSI-25, 26, 69, 98, 99, 100). 14 more have NASA tables summarised at table level; 4 are ground investigations with no experiment table (PSI-60, 62, 115, 117). This is by design and stated on the Investigations page |
| Lessons → investigations | `#/investigation/PSI-25` and `#/investigation/PSI-69` resolve; `#/investigations/moon`, `#/about` resolve |
| Compare examples, Scenario presets | All IDs exist; presets match the brief (30 % / 10.2 psi; 100 % / 4.3 psi; 21 % / 14.7 psi) |
| PSI-25 BASS-II units | Calibrated O2 is vol%; CO2 vol%; CO ppm. Non-numeric NASA entries: "+OR" (over range), "Over", "failed". The UI appends the unit to them. **FA-03** |
| FLEX headers | NASA prints "O / N / CO / He initial ambient composition" with subscripts lost. "O" is explained in the UI; "CO" is almost certainly CO₂ (FLEX used CO₂ as a diluent) and is not explained. **FA-15** |

### 2.5 External links and citations

| Category | Count | Result |
|---|---|---|
| Unique external URLs in data + UI | 79 (plus the SVG namespace) | **69 return 200**. 7 "failures" were extraction artefacts inside NASA's prose (URLs cut at `(` or `]`), which the site shows as text, not links. Re-tested cleaned: all resolve. `youtube.com` returned 429 (bot rate limit), `spaceappschallenge.org` has an incomplete TLS chain on the server side, and `issnationallab.org/...` (404) is in NASA's `experimentHardwareLink` field, which the UI doesn't render |
| DOIs | 267 | **267/267 registered** at doi.org; the 6 initial misses were the same extraction artefacts |
| `http://` links | 0 | ✅ |
| External `<a>` with `target="_blank"` | 11 in `app.js`, all `rel="noopener"` | ✅ Lessons: 11 external, 0 without `_blank`. `noreferrer` is not required: the policy is `strict-origin-when-cross-origin` |

### 2.6 Scientific boundary compliance

All wording on the 17 non-record pages that mentions probability, risk, safety, certification or prediction was extracted. Every instance is a **negation or limitation**:
- "It does not calculate fire probabilities or certify safety"
- "A screening tool, not a safety tool"
- "Counts, not a probability"
- "not a prediction for real missions"
- "They are not safety or risk scores"
- "Points never claim safety"

The Lab's system prompt (`core.mjs` `SYSTEM`) forbids "fire probabilities, risk scores, safety certifications or design recommendations". The UI example "What is the probability of a fire on a Mars rover? (should abstain)" demonstrates the abstention. **Compliant: no violations.**

---

## Section 3: Route-by-route forensic matrix

| Route | Renders | No NaN / undefined / Infinity | No overflow at 320–1440 px | Malformed input | Keyboard | Verdict |
|---|---|---|---|---|---|---|
| `#/` Overview | ✅ | ✅ | ✅ | n/a | ✅ skip link is the first Tab stop | Pass |
| `#/scenario` | ✅ | ✅ (16 fuzz inputs) | ✅ | ⚠ bad `%` in URL crashes (FA-02); `o2=NaN` written to URL (FA-11) | ✅ | Pass with fixes |
| `#/explorer` | ✅ | ✅ | ✅ | ✅ regex chars safe; ⚠ untrimmed search (FA-10) | ✅ rows focusable, Enter opens | Pass with fixes |
| `#/experiment/<id>` | ✅ 537/537 | ⚠ glued units on 3 records (FA-03) | ✅ | ⚠ bad `%` crashes (FA-02); unknown ID shows "Record not found" ✅ | ✅ | Pass with fixes |
| `#/compare` | ✅ | ✅ (9 edge cases) | ✅ | ⚠ bad `%` crashes; >4 IDs not normalised (FA-19) | ✅ | Pass with fixes |
| `#/investigations` | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠ FA-01 count |
| `#/investigation/<acc>` | ✅ 24/24 | ⚠ "undefined undefined" (FA-09); ⚠ "3 test records" (FA-01) | ✅ | ✅ unknown shows "Investigation not found" | ✅ | Fails until FA-01 fixed |
| `#/lab` | ✅ | ✅ | ✅ | ⚠ stuck button on malformed answer (FA-05); concurrent requests (FA-06) | ✅ | Pass with fixes |
| `#/lessons` | ✅ | ✅ | ✅ | ✅ | ✅ | Pass |
| `#/about` | ✅ | ✅ | ✅ | ✅ | ✅ | Pass |
| any unknown route | ✅ "Page not found" card | ✅ | ✅ | ✅ | ✅ | Pass |

### 3.1 `#/` Overview (`viewOverview`, app.js 217–319)
- **What's there:**
  - the hero with the background video, which is decorative and `aria-hidden`;
  - one primary call to action ("Open Flame Explorer") and one secondary ("Check a condition against NASA tests");
  - the "What this site answers" rows, the dataset-status panel with live counts, and the experiment and oxygen-band charts with "how to read" and "included / left out" notes.
- **Links:** every link is a plain `#/…` hash handled by the single delegated click handler (2324–2334). None carries filter state, because no target page reads any. U-01 adds Explorer state.
- **Load:** 771 ms to the load event and 496 ms to first contentful paint (desktop), with 301 KB transferred. The largest asset is `data.js` at 113 KB compressed.
- **Finding:** the headline doesn't state the project's most important result, the untested Moon-base atmosphere, which only appears deeper in Investigations (see Section 7).

### 3.2 `#/scenario` Scenario Check (`viewScenario` 1964–2153, `condOf` 1754, `dist` 1776)
- **Matching rule:**
  - Every test gets a normalised distance `d = √(((O2 − O2ₛ)/1.5)² + ((p − pₛ)/1.5)²)`. The pressure term is dropped where NASA recorded no pressure (BASS-II, and FLEX-114 whose pressure is printed as 0).
  - **Inside** means |ΔO2| ≤ 1.5 points **and** |Δp| ≤ 1.5 psi. **Oxygen only** applies when no pressure was recorded. **Omitted** means no usable O2: 2 BASS-II tests whose raw starting O2 doesn't confirm the calibrated value, and 13 SAFFIRE tests whose O2 is approximate or absent.
- **Fuel family is a hard partition**, so solids are never matched to droplets. There is no airflow, gravity or material weighting, and this is stated on the page.
- **Fuzz results:**
  - 0 % → "Insufficient data".
  - −50, 99999, empty or `abc` → "Enter oxygen between 0 and 100% and a pressure above 0 psi".
  - 21.55555 % → 95 inside.
  - 100 % / 4.3 psi → "Insufficient data".
  - `1e2` → treated as 100.
  - psi 0 or −3 → validation message. psi 99999 → "Partly covered: 43 oxygen-only matches" (FA-20: honest, but it should say the pressure is beyond every recorded test).
- **Input bounds:** `min=0 max=100 step=0.5` and `min=0 max=60 step=0.1`. The recorded ranges are O2 13.6–22.7 % (solids), 12–34 % (FLEX), and pressure 14.3–14.8 psi (BASS-I), 10.2–44.9 psi (FLEX).
- **Far outside the tested range:** the verdict is "✕ Insufficient data … will not describe what would happen", and nearest tests are labelled "for orientation only". ✅

### 3.3 `#/explorer` Flame Explorer (`viewExplorer` 389–504)
- **Search** uses `String.indexOf`, not a regex, so `(`, `[`, `*`, `\`, `%`, `.*` and `<script>` are literal and safe; no errors across 10 inputs. Leading and trailing spaces aren't trimmed: "␠␠pmma␠␠" returns 0 rows instead of 99 (**FA-10**).
- **Filters:** 4 filters plus search (0 rows), then remove "Investigator" (6 rows) and the select resets to "". "Reset all" returns all 537 rows, empties all 5 controls and removes every chip. **No desync.**
- **No sorting exists**, so the null-sort concern doesn't apply. Rows keep NASA's natural order.
- **No pagination:** all 537 rows render each time a filter changes. Measured fine (no typing lag; 7 MB heap).
- **URL sync:** none on `main`. A refresh or shared link loses the filters (**FA-13**). Fixed by U-01, verified: refresh keeps 6 of 537, and the record "Back to Flame Explorer" link restores them.

### 3.4 `#/compare` (`viewCompare` 976–1178)
- **State lives in the URL** (`#/compare/ID,ID`), de-duplicated (the same test counts once), capped at 4 (`MAX_PICK`), and unknown IDs are dropped. With 6 IDs, 4 are shown and the picker says "4 tests max", but the address keeps all 6 (**FA-19**, cosmetic).
- **Missing metrics** are listed under "Missing or suspect" and left out of the charts with the reason (e.g. "3 tests | 20 values charted | 4 left out" for P3b/O13b/O12).
- **Deltas** are plain differences (`changeBars`), never ratios, so `Infinity%` can't occur. No NaN, Infinity or undefined appeared in 9 edge cases.
- **Cross-experiment** (BASSII-B1 vs BASSI-1-1) gives "Flare AI won't compare these numbers", with 3 failed conditions listed. ✅

### 3.5 `#/investigations` and `#/investigation/<acc>` (1301–1595)
- **Lenses:** station / Moon / Mars. There are fuel and data filters, up to 3 checkboxes, and "Compare selected". Every score input is shown and tagged by source.
- **FA-01:** the card count, the detail-page link ("3 test records in Flare AI") and the "Has test records in Flare AI" filter all use `r.source_id === v.accession`, which misses the 126 report-sourced BASS-II rows.
- **FA-14:** that link goes to the unfiltered Explorer. U-01 links to `#/explorer/exp=<experiment>`; verified, PSI-69 gives 274 of 537.

### 3.6 `#/lab` Intelligence Lab (client 1657–1749; server `core.mjs`)
- **Retrieval:**
  - BM25 over a generated corpus of records, investigation texts and brief facts. An exact ID mentioned in the question gets +50, and investigation and brief documents get a ×1.15 boost.
  - The top 12 documents are kept, with **at most 6 test records**, so summaries aren't crowded out. That bounds the prompt size, so a broad query can't overflow the context.
  - Trade-off: a broad question ("all SAFFIRE tests") gets at most 6 records and relies on the investigation summaries. That's acceptable, and the retrieved list is shown to the user.
- **Mocked failure modes:**

  | Mode | Result |
  |---|---|
  | HTTP 429 JSON | keyword fallback with the server's message; button re-enabled ✅ |
  | HTTP 500 (HTML body) | fallback ✅ |
  | HTTP 504 | fallback ✅ |
  | network offline | "Could not reach the SI service", fallback ✅ |
  | answer with HTML / markdown / `javascript:` in text | rendered as inert text (no `<script>` or `<img>` in the DOM) ✅ |
  | answer citing `FAKE-999` | rendered as a link to `#/` (**FA-12**; the server's `validate()` normally strips it) |
  | answer whose key point lacks `citations` | **TypeError, button stuck on "Checking the records…" forever, no fallback** (**FA-05**) |
  | example chip clicked while a question is pending | **2 requests sent** (**FA-06**) |
  | double-click on Submit | 1 request ✅ |

- **Prompt injection:** the question is wrapped in `<visitor_question>`, and the system prompt says to ignore instructions inside it. Output is forced into a JSON schema and every citation is re-validated server-side against the documents actually sent. The UI renders text only via `textContent`. Residual risk is limited to wording inside a summary; it can't create links, markup or false citations.

### 3.7 `#/lessons` (2155–2229)
- 11 resources in 3 groups, with search and a group filter.
- The NASA quotes are checked word for word on every build (11 of 11).
- Internal links go to `#/investigation/PSI-25`, `#/investigation/PSI-69`, `#/investigations/moon`, `#/investigations` and `#/about`. Each resolves to the exact page.
- The video is a link, not an embed, but the CSP already allows `youtube-nocookie.com`.

### 3.8 `#/about` (2230–2280)
- Covers the method, the sources, the trust labels and the SI disclosure.
- The 628 Aerospace emblem sits beside the rules list (PR #55).
- The footer disclaimer is on every page. Its colour is just below AA contrast (**FA-08**).

---

## Section 4: Master bug and error registry

Line numbers refer to `main` @ `3456ce7`. "Verified" means the trigger was reproduced on the live site and the fix was re-tested in the browser.

| ID | Sev | Route / file:line | Trigger | Root cause | Fix (Section 8) |
|---|---|---|---|---|---|
| **FA-01** | **P1** | `#/investigation/PSI-25`, `#/investigations`; app.js 1315, 1321, 1519, 1551 | Open the BASS-II investigation page: it says "3 test records in Flare AI" | Record→investigation mapping uses `source_id`; 126 report rows have `source_id = "20210011385"` (the NTRS report), not `PSI-25` | `invAccOf(r)` maps report rows to PSI-25; the link text gives the split (126 report + 3 PSI-only). Verified: "129 test records in Flare AI (126 from NASA's BASS-II report, 3 only in this PSI table)" |
| **FA-02** | **P1** | router; app.js 2298, 2304, 979, 1968 | Open `#/experiment/%E0%A4%A` (any bad `%` sequence, e.g. a truncated shared link) | `decodeURIComponent` throws `URIError`, uncaught in `render()`. The previous page stays with a stale menu highlight; on first load `<main>` stays empty | `safeDecode()` wrapper. Verified: "Record not found", 0 errors |
| **FA-03** | P2 | record pages; app.js 505–510 | Open BASSII-O12 / O13b / P3b | `reading()` always appends the unit after the pair, even when NASA printed a word | Unit per numeric value; NASA words shown as printed. Verified: "+OR → +OR", "950 ppm → Over", "0.51 vol% → failed" |
| **FA-04** | P2 | Explorer 460, Investigation 1565, Scenario 2049 | Any long note: "turne…", "ignitio…", "understandin…" (109 places) | Character-count `slice()` | `clip(t, n)` ends on a whole word. Verified: 0 mid-word cuts in the verify crawl |
| **FA-05** | P2 | Lab; app.js 1700, 1703, 1729 | Server or cache returns a key point without `citations` | `p.citations.map` throws inside `.then`; the final `.then` that re-enables the button never runs | `(p.citations \|\| [])` and a `.catch` that shows the keyword fallback. Verified: button restored, no error |
| **FA-06** | P2 | Lab; app.js 1713 | Ask, then click an example while waiting | Example buttons call `ask()` directly; only Submit is disabled | `busy` guard. Verified: 1 request |
| **FA-07** | P2 (a11y, WCAG 2.4.3) | router; app.js 2316 | Click "Scenario Check" in the menu: focus stays on the menu link | `render()` scrolls but never moves focus | Focus `<main>` after in-app navigation (not on first load). Verified: `activeElement = main`; the skip link is still the first Tab stop on load |
| **FA-08** | P2 (a11y, WCAG 1.4.3) | style.css 16, 18 | Footer disclaimer, method tags, evidence note, accent links | `--dim:#757575` gives 3.89–4.35:1 on panels; `--accent-tx:#e2375a` gives 4.21–4.47:1 on panels | `#8c8c8c` (≥4.9:1 on every surface) and `#ea4d6c` (≥4.53:1) |
| FA-09 | P3 | `#/investigation/PSI-10`; app.js 1588 | Open the publications list | NASA's catalogue gives the author as "undefined undefined" | Shown as "[name missing in NASA PSI]" |
| FA-10 | P3 | Explorer; app.js 422 | Search "␠␠pmma␠␠" gives 0 rows | Untrimmed query | `.trim()` |
| FA-11 | P3 | Scenario; app.js 1989 | Empty a box: the URL shows `o2=NaN` | `NaN` concatenated into the hash | Empty value instead |
| FA-12 | P3 | Lab; app.js 1677 | Answer cites an ID not in `citations` | Falls back to a link to `#/` | Plain text with title "Not a retrieved document" |
| FA-13 | P3 | Explorer | Filter, then refresh or share: the filters are lost | No URL state | Upgrade U-01 |
| FA-14 | P3 | Investigation page | "N test records" link | Unfiltered `#/explorer` | Upgrade U-01 |
| FA-15 | P3 | FLEX record pages | Raw header "CO initial ambient composition" | NASA lost the subscript (CO₂) | Add a note like the existing "header reads 'O'" one (data-builder change) |
| FA-16 | P3 | header, all routes | 320 / 375 / 768 px | The 8-link menu wraps to 3 rows: header 224 / 181 / 221 px tall | Single scrollable row under 760 px (CSS in Section 6) |
| FA-17 | P3 (a11y) | chart tooltip; app.js 766 | Hover chart marks with a screen reader on | Tooltip `role="status"` may announce every hover | Make the tooltip `aria-hidden="true"`; marks already carry text alternatives |
| FA-18 | P3 | hosting | Every load: one console error | Netlify injects `/.netlify/scripts/hud` inline; the CSP (correctly) blocks it | Turn off the Netlify badge/HUD in site settings if the plan allows; harmless otherwise |
| FA-19 | P3 | Compare | `#/compare/A,B,C,D,E,F` | The address keeps IDs beyond the 4 shown | `history.replaceState` to the normalised list |
| FA-20 | P3 | Scenario | psi 99999 | Values above `max=60` accepted silently | Add "beyond every recorded pressure (max 44.9 psi, FLEX)" to the verdict |
| FA-21 | P3 | `core.mjs` 176–179 | Burst of parallel questions | Rate-limit counters are read-then-write (not atomic), so a burst can exceed the per-IP limits slightly | Accept it (the global cap still holds) or use blob ETags / conditional writes |
| FA-22 | P3 | `core.mjs` 163 | Very large POST body | `req.json()` reads the whole body before the 300-character check (Netlify caps at 6 MB) | Reject when `content-length > 4096` before parsing |
| FA-23 | P3 | data | `BASSII-O2.raw_text` trailing space | Extraction | `.strip()` in the builder (invisible) |

**Not bugs (claims from the earlier AI-generated audit that were re-tested and are false):**
- scenario NaN;
- column-sorting nulls (no sorting exists);
- typing lag;
- 320 px overflow (0 overflow on 13 routes × 5 widths);
- Lab double-submit (1 request);
- innerHTML / XSS (0 sinks);
- "Infinity%" (differences only);
- a broken skip link (it works: Tab → "Skip to content", Enter focuses `#main`);
- listener leaks (window 4→4, document 4→4 after 150 navigations; heap 7 MB).

---

## Section 5: Security, API hardening and XSS report

### 5.1 Secrets
- The full git history (142 commits, unshallowed), every tracked file and the client bundle were scanned for Google (`AIza…`), Anthropic (`sk-ant-…`) and GitHub (`ghp_…`) keys and for private-key blocks: **0 hits**.
- `.env` is in `.gitignore`.
- The key is read only from `process.env.GEMINI_API_KEY` / `ANTHROPIC_API_KEY` inside the function (`ask.mjs` 13–17), and is never logged: `core.mjs` logs the status code only.

### 5.2 DOM XSS
- **0 occurrences** of `innerHTML`, `outerHTML`, `insertAdjacentHTML`, `document.write`, `eval`, `new Function`, `on*` attributes set from strings, or `javascript:`.
- All DOM is built by `h()` (app.js 34–50), which uses `createTextNode` for strings and `addEventListener` for `on*` keys.
- URL parameters reach the DOM only as text or as `href` values constructed from known prefixes (`#/experiment/` + ID).
- LLM output is text-only (mock test: `<script>`, `<img onerror>` and `javascript:` were all inert).
- CSP: `script-src 'self'` with no `unsafe-inline` for scripts. A future injection still couldn't execute inline script.

### 5.3 Serverless function (`netlify/functions/ask`)

| Control | Status |
|---|---|
| Method | `POST` only, otherwise 405 with `Allow: POST` (verified live with a GET) |
| Origin | Must equal `URL` / `DEPLOY_PRIME_URL` / `ALLOWED_ORIGIN`, otherwise 403. No CORS headers are sent, so other sites' browsers can't read responses. (Origin can be forged by non-browser clients; rate limits cover that) |
| Content type | `application/json` required (415) |
| Input | trimmed; 8–300 characters; JSON parse errors give 400. Body size isn't pre-checked (FA-22) |
| Rate limits | 8/hour and 25/day per hashed IP (SHA-256, truncated), 200/day globally, 429 with `Retry-After`. Not atomic (FA-21) |
| Cache | 100 days, keyed by the normalised question; repeat questions cost no quota |
| Upstream timeout | `AbortController` deadline in `gemini.mjs`; 502 with a plain reason, never the key or the question |
| Fail closed | If the Blobs store is unavailable, it returns 503 instead of calling the model without limits |
| Output validation | JSON schema; citations filtered to documents actually sent; grade computed deterministically; text lengths capped |
| Headers | `X-Content-Type-Options: nosniff`; `Referrer-Policy`; strict CSP with `frame-ancestors 'self'`, `base-uri 'none'`; HSTS (Netlify, preload). Missing: `Permissions-Policy` (optional: `camera=(), microphone=(), geolocation=()`) |

### 5.4 Memory and listeners
- Global listeners: `hashchange` and one delegated `click` (registered once at startup), plus 3 tooltip listeners registered once through `ensureTip()`'s memo.
- Per-view listeners are attached to elements that are discarded with the view.
- Measured with Chrome DevTools Protocol `DOMDebugger.getEventListeners`: window 4 and document 4, before and after 150 route changes. **No leak.**

---

## Section 6: Responsive layout, CSS and WCAG 2.2 AA report

### 6.1 Breakpoints (13 routes each, live site)

| Width | Horizontal overflow | Menu items clipped | Header height | Note |
|---|---|---|---|---|
| 320 px | 0 routes | 0 | **224 px** (3 menu rows) | Content starts a quarter of the way down a 640 px screen |
| 375 px | 0 | 0 | 181 px | |
| 768 px | 0 | 0 | **221 px** | Tablet portrait wraps too |
| 1024 px | 0 | 0 | 157 px | |
| 1440 px | 0 | 0 | 72 px | |

Suggested CSS for FA-16, not applied because it's a visible design change for the team to approve:

```css
@media (max-width: 900px) {
  .top-inner { flex-wrap: wrap; }
  #nav { display: flex; flex-wrap: nowrap; overflow-x: auto; scrollbar-width: none; width: 100%;
         mask-image: linear-gradient(90deg, #000 85%, transparent); }
  #nav::-webkit-scrollbar { display: none; }
  #nav a { padding: 12px 10px; }
}
```

### 6.2 Keyboard and focus
- **Skip link:** the first Tab stop on load; Enter focuses `#main`. ✅
- **Explorer rows:** `tabindex=0`, Enter/Space opens. ✅ Scenario bubbles: Enter/Space. ✅
- **No modals or drawers,** so no Escape handling is needed.
- **Focus after navigation:** it stays on the old link (FA-07) on `main`; fixed.

### 6.3 Names, roles and states (all 8 menu destinations)
- Unlabelled form controls: **0**.
- Images without `alt`: **0**.
- Buttons without an accessible name: **0**.
- Exactly one `h1` per page.
- `aria-current="page"` on the correct menu item on every route.
- `aria-live="polite"` on the Explorer count, the Scenario output and the Lab output.
- `aria-pressed` on Scenario fuel tabs and zoom buttons; `role="tablist"`/`tab` with `aria-selected` on the Scenario result tabs.

### 6.4 Contrast (computed against the nearest opaque background, all pages)

| Element | Colour | Ratio | Required | Status |
|---|---|---|---|---|
| Footer disclaimer `p` (14 px) | #757575 | 4.35:1 | 4.5 | ❌, then 5.96:1 with #8c8c8c |
| Footer "Built for NASA Space Apps 2026" (13 px) | #757575 | 4.35:1 | 4.5 | ❌, then ✅ |
| Method tag `.mtag` (11.5 px, 567 instances) | #757575 | 4.13:1 | 4.5 | ❌, then 5.33:1 |
| Overview `.ev-note` (13 px) | #757575 | 4.13:1 | 4.5 | ❌, then ✅ |
| Accent links (record IDs, 600 instances) on panels | #e2375a | 4.47:1 | 4.5 | ❌ (by 0.03), then 4.93:1 with #ea4d6c |
| Body, `.note`, `.hint`, `th`, chips | various | 7.3–18.8:1 | 4.5 | ✅ |

---

## Section 7: Global-winner improvements (19)

**Scientific and analytical depth**

1. **U-03 Regime map (signature visual).** One chart: O2 % (x) vs pressure psi (y) for all 24 investigations as boxes (table ranges) and the 537 tests as dots, coloured by fuel family, with the brief's zones overlaid: ISS (21 %, 14.7 psi), Moon base (≥30 %, ≤10.2 psi) and spacesuit (100 %, 4.3 psi). The empty Moon-zone box for solids **is the story**. Data: `table_summaries[].o2_range_pct` / `p_range_psi` already exist.
2. **U-04 Gap ledger.** An auto-generated list of "never tested" combinations (fuel family × atmosphere zone × gravity), each with the nearest evidence and its distance. It turns the abstention logic into a research agenda: "The next experiment that would most reduce uncertainty for a Moon base".
3. **U-05 Moon-base headline on the Overview.** "No NASA test in PSI has burned a solid cabin material in the planned Moon-base atmosphere (≥30 % O2 at ≤10.2 psi); the highest solid-material test reached 22.7 % O2 (BASS)", linked to `#/investigations/moon`. This is the single biggest Impact and Creativity lever.
4. **U-06 Window sensitivity.** A slider for the match window (±0.5 to ±3 points / psi), showing how the verdict changes. It proves the result doesn't hinge on the arbitrary ±1.5.
5. **U-07 FLEX outcome map.** For droplets, small multiples of extinction / disruption / completion by O2 and diluent (N₂, CO₂, He), with counts only, extending the existing leave-one-out consistency note.

**UX and workflow**

6. **U-01 URL-shareable Explorer state (implemented, Section 9).**
7. **U-02 Evidence brief export from Scenario Check (implemented, Section 9).** A Markdown file with the verdict, counts, every matching test with its O2 method, pressure conversion and NASA source row, plus the disclaimer. It's the deliverable a design-review engineer actually needs.
8. **U-08 Compare and Investigation-compare export** with the same Markdown/CSV pattern.
9. **U-09 Global search (`/` or `Ctrl+K`).** One box over records, investigations and lessons, reusing `localSearch()` (already client-side), with results grouped by type.
10. **U-10 Print stylesheet** (`@media print`): white background, no video, links shown with URLs, so pages print as one-page evidence sheets.
11. **U-11 Mobile menu** (FA-16 CSS above) to reclaim 100–150 px of first-screen height on phones.

**Intelligence Lab**

12. **U-12 Citation verification badges.** Show "✓ in retrieved set" per citation and the retrieval score from `evidence[].score`, which is already returned.
13. **U-13 Mission-engineer templates.** Pre-built prompts ("Which materials have been tested near X % O2?", "What does NASA say about suppression with CO₂?") that fill a template with the current Scenario values.
14. **U-14 Deterministic offline synthesis.** When the model is unavailable, generate a templated answer from the top keyword matches ("3 records mention 'PMMA' and 'opposed'; their starting O2 is 16.4–21.7 %…") instead of a bare list.
15. **U-15 Field-weighted retrieval.** Boost matches in `material_raw` and NASA column names over free-text notes, and add synonyms (O2 ↔ oxygen, PMMA ↔ acrylic, rod ↔ cylinder).

**Visual polish and performance**

16. **U-16 Lazy data.** Split `data.js` (1.31 MB raw, 113 KB compressed): load investigation and record details on demand, keeping first paint under 400 ms on 3G.
17. **U-17 Skeleton states** for Lab answers (fixed-height placeholder) to avoid layout shift when the answer arrives.
18. **U-18 Contrast tokens** (done in FA-08) plus a visible focus ring audit on every interactive element.
19. **U-19 "Verify it yourself" panel on About.** One command (`python3 scripts/verify-all.py`) and its last result. Judges reward reproducibility.

---

## Section 8: Complete code patches for the P1 and P2 fixes (plus P3 fixes FA-09 to FA-12)

Apply with `git apply` on `main` @ `3456ce7`. Verified on the patched copy:
- `site_smoke_test` 146/146, `previewer_nav_test` 14/14, `lab_ui_test` all pass, `lab_function_test` 33/33;
- each fix re-tested in the browser.

```diff
diff --git a/site/css/style.css b/site/css/style.css
index 11738db..889c7b7 100644
--- a/site/css/style.css
+++ b/site/css/style.css
@@ -13,9 +13,9 @@
 :root {
   /* black, burgundy, white */
   --bg:#000000; --bg-2:#080808; --panel:#0e0e0e; --panel-2:#171717; --line:#333333; --line-2:#222222;
-  --text:#f2f2f2; --cream:#ffffff; --muted:#a8a8a8; --dim:#757575;
+  --text:#f2f2f2; --cream:#ffffff; --muted:#a8a8a8; --dim:#8c8c8c;
   /* burgundy: buttons and the brand use it exactly; text uses a brighter crimson so it stays readable on black */
-  --accent:#6d001a; --accent-hi:#8c0a28; --accent-tx:#e2375a; --accent-ink:#ffffff; --accent-soft:rgba(160,20,52,.18); --accent-line:rgba(226,55,90,.5);
+  --accent:#6d001a; --accent-hi:#8c0a28; --accent-tx:#ea4d6c; --accent-ink:#ffffff; --accent-soft:rgba(160,20,52,.18); --accent-line:rgba(226,55,90,.5);
   --sage:#6d001a;
   /* evidence vocabulary: one colour each, always with a glyph or word as well */
   --measured:#6ec6d6; --published:#8fb0ff; --interp:#c4a8d8; --caution:#e3a948; --warn:#ff7a45; --ok:#8db890; --mach:#b0b0b0;
@@ -769,3 +769,5 @@ body::after {
   .rules-emblem { padding:4px 0 8px; }
   .rules-emblem img { width:140px; }
 }
+
+main:focus { outline:none; } /* focus moves here after navigation; main itself is not interactive */
diff --git a/site/js/app.js b/site/js/app.js
index 88a41ea..f585fb4 100644
--- a/site/js/app.js
+++ b/site/js/app.js
@@ -16,6 +16,8 @@
   var SOURCE = SOURCES["20210011385"] || (D.sources || [])[0] || null;
   function sourceOf(r) { return SOURCES[r.source_id] || SOURCE; }
   function fromReport(r) { return r.experiment === "BASS-II" && !!r.raw_text; }
+  /* The PSI investigation a record belongs to. BASS-II rows copied from NASA's report (NTRS 20210011385) are PSI-25 tests. */
+  function invAccOf(r) { return fromReport(r) ? "PSI-25" : r.source_id; }
   /* Starting O2 as each source states it (BASS-II: calibrated chamber O2; BASS-I: logged O2 fraction x 100). */
   function o2Start(r) { return fromReport(r) ? r.o2_cal_initial : (r.o2_vol_pct || r.o2_raw || ""); }
   var TABLE = { B: "A.1", F: "A.2", P: "A.3", M: "A.4", O: "A.5", T: "A.6" };
@@ -55,6 +57,8 @@
       typeof arguments[i] === "string" || typeof arguments[i] === "number" ? document.createTextNode(String(arguments[i])) : arguments[i]);
     return el;
   }
+  /* decodeURIComponent throws URIError on a bad %-escape (e.g. "#/experiment/%E0%A4%A"); keep the raw text instead. */
+  function safeDecode(s) { try { return decodeURIComponent(s); } catch (e) { return s; } }
   function num(s) {
     if (s == null) return NaN;
     var t = String(s).replace(/[–−]/g, "-").trim();
@@ -84,6 +88,13 @@
   function flagsOf(r) {
     return (r.qc_flag || "").split(";").filter(Boolean);
   }
+  /* Shorten text to at most n characters, ending on a whole word, with one ellipsis. */
+  function clip(t, n) {
+    t = String(t || "").replace(/\s+/g, " ").trim();
+    if (t.length <= n) return t;
+    var cut = t.slice(0, n - 1), sp = cut.lastIndexOf(" ");
+    return (sp > n * 0.6 ? cut.slice(0, sp) : cut).replace(/[\s,;:.\-\u2013\u2014(]+$/, "") + "\u2026";
+  }
   function setTitle(t) { document.title = (t ? t + " | " : "") + "Flare AI"; }
 
   /* ---------- preview banner ---------- */
@@ -419,7 +430,7 @@
       return h("div", { class: "field" }, h("label", { for: id }, label), s);
     }
     var search = h("input", { type: "search", id: "q", placeholder: "Material, note text, test ID...",
-      oninput: function (e) { state.q = e.target.value.toLowerCase(); draw(); } });
+      oninput: function (e) { state.q = e.target.value.trim().toLowerCase(); draw(); } });
     controls.q = search;
     function o2match(r) {
       if (!state.o2) return true;
@@ -457,7 +468,7 @@
       tbody.textContent = "";
       list.forEach(function (r) {
         var note = r.observation || (r.fields || []).map(function (f) { return f[0] + ": " + f[1]; }).slice(0, 3).join("; ");
-        var obs = note.length > 140 ? note.slice(0, 137) + "..." : note;
+        var obs = clip(note, 140);
         var fl = flagsOf(r).map(function (f) { return chip("warn", FLAG_TEXT[f] || f); });
         /* data-check badges up front (details stay on the record page) */
         if ((r.psi_check || "").indexOf("DIFFERS") === 0) fl.push(chip("warn", "NASA PDF and PSI disagree"));
@@ -502,11 +513,16 @@
       h("p", { class: "note", style: "margin-top:10px" }, "O2 start tags: cal. = calibrated chamber sensor (BASS-II); logged = O2 logged as a fraction \u00d7 100 (BASS-I); mol% = ambient O2 mole fraction \u00d7 100 (FLEX); approx. = approximate value as printed (SAFFIRE). These methods differ, so the values are never compared with each other."));
   }
 
+  function isNumText(x) { return x != null && /^[-+]?(\d+\.?\d*|\.\d+)$/.test(String(x).trim()); }
   function reading(label, a, b, unit) {
+    /* Both numeric: one unit after the pair (13.6→13.4 vol%). Otherwise NASA printed a word in the column ("+OR" =
+     * over range, "Over", "failed"): each number keeps its own unit and the word is shown as printed, with no unit. */
+    var both = isNumText(a) && (b == null || isNumText(b));
+    function val(x) { return both || !isNumText(x) ? h("b", null, x || "—") : [h("b", null, x), h("span", { class: "u" }, unit)]; }
     return h("div", { class: "reading" }, h("span", null, label),
-      h("span", null, h("b", null, a || "—"),
-        b != null ? [h("span", { class: "arrow" }, "→"), h("b", null, b || "—")] : null,
-        h("span", { class: "u" }, unit)));
+      h("span", null, val(a),
+        b != null ? [h("span", { class: "arrow" }, "→"), val(b)] : null,
+        both ? h("span", { class: "u" }, unit) : null));
   }
 
   /* ---------- provenance: what NASA called each value, its unit, and anything we did to it ---------- */
@@ -976,7 +992,7 @@
   function viewCompare(arg) {
     setTitle("Compare");
     ensureTip();
-    var ids = (arg || "").split(",").map(decodeURIComponent).filter(Boolean)
+    var ids = (arg || "").split(",").map(safeDecode).filter(Boolean)
       .filter(function (id, i, a) { return a.indexOf(id) === i; }); /* the same test picked twice counts once */
     var picked = ids.map(function (id) { return ROWS.filter(function (r) { return r.id === id; })[0]; }).filter(Boolean).slice(0, MAX_PICK);
     function go2(list) { location.hash = "#/compare/" + list.map(function (r) { return encodeURIComponent(r.id); }).join(","); }
@@ -1312,13 +1328,13 @@
         if (state.fuel && fuelKey(x.v) !== state.fuel) return false;
         if (state.pillar && (c.pillar || "").indexOf(state.pillar) < 0) return false;
         if (state.data === "flight" && !(x.v.n_tests > 0 && /Microgravity/.test(x.v.projectType))) return false;
-        if (state.data === "ours" && !ALL.some(function (r) { return r.source_id === x.v.accession; })) return false;
+        if (state.data === "ours" && !ALL.some(function (r) { return invAccOf(r) === x.v.accession; })) return false;
         return true;
       }).sort(function (a, b) { return b.r.score - a.r.score || invName(a.v).localeCompare(invName(b.v)); });
       count.textContent = "Showing " + list.length + " of " + INV.length + " NASA PSI combustion investigations, ranked for: " + LENSES[lens].label;
       listBox.textContent = "";
       list.forEach(function (x, i) {
-        var v = x.v, c = v.curated || {}, ours = ALL.filter(function (r) { return r.source_id === v.accession; }).length;
+        var v = x.v, c = v.curated || {}, ours = ALL.filter(function (r) { return invAccOf(r) === v.accession; }).length;
         var cb = h("input", { type: "checkbox", id: "pick-" + v.accession, checked: picked.indexOf(v.accession) >= 0, onchange: function (e) {
           if (e.target.checked) { if (picked.length >= 3) { e.target.checked = false; return; } picked.push(v.accession); } else picked = picked.filter(function (a) { return a !== v.accession; });
           cmpBtn.textContent = "Compare selected (" + picked.length + ")"; cmpBtn.disabled = picked.length < 2; } });
@@ -1516,7 +1532,7 @@
     var v = invById(acc);
     if (!v) { setTitle("Not found"); return h("div", null, h("p", { class: "crumbs" }, h("a", { href: "#/investigations" }, "← Investigations")), h("h1", null, "Investigation not found")); }
     setTitle(invName(v));
-    var c = v.curated || {}, ours = ALL.filter(function (r) { return r.source_id === v.accession; });
+    var c = v.curated || {}, ours = ALL.filter(function (r) { return invAccOf(r) === v.accession; }), oursReport = ours.filter(fromReport).length;
     var rs = relevance(v, "station"), rm = relevance(v, "moon"), rM = relevance(v, "mars");
     function text(label, t) { return t ? h("div", { class: "card", style: "margin-top:14px" }, h("div", { class: "prov-head" }, h("h3", null, label), chip("published", "NASA PSI text")),
       h("p", { class: "pub-text" }, t)) : null; }
@@ -1548,7 +1564,8 @@
             h("div", { class: "rh-actions" },
               h("a", { class: "btn", href: v.landing_page, target: "_blank", rel: "noopener" }, "Open NASA’s PSI page ↗"),
               h("a", { class: "textlink", href: "https://doi.org/" + v.doi, target: "_blank", rel: "noopener" }, "DOI"),
-              ours.length ? h("a", { class: "textlink", href: "#/explorer" }, ours.length + " test records in Flare AI") : null),
+              ours.length ? h("a", { class: "textlink", href: "#/explorer" }, ours.length + " test records in Flare AI" +
+                (oursReport ? " (" + oursReport + " from NASA\u2019s BASS-II report, " + (ours.length - oursReport) + " only in this PSI table)" : "")) : null),
             (function () {
               var cite = "NASA Physical Sciences Informatics (PSI). " + v.title + " (" + v.accession + (v.investigationAcronym ? ", " + v.investigationAcronym : "") +
                 "), version " + v.version + ", released " + v.releaseDate + ". " + v.licenseIdentifier + ". https://doi.org/" + v.doi + ". Accessed " + v.retrieved + ".";
@@ -1562,7 +1579,7 @@
           h("div", null, h("p", { class: "mini-h" }, chip("interp", "Ours"), " Plain-language summary"), h("p", null, c.summary_ours || "\u2014"),
             h("p", { class: "note" }, "Written with SI (Claude) from NASA\u2019s objective text below. ", h("a", { href: v.landing_page, target: "_blank", rel: "noopener" }, "Check it on NASA\u2019s PSI page"))),
           h("div", null, h("p", { class: "mini-h" }, chip("published", "NASA"), " NASA\u2019s stated impact"),
-            h("p", null, (function (t) { t = (t || "").replace(/\s+/g, " ").trim(); return t ? (t.length > 420 ? t.slice(0, 417) + "\u2026" : t) : "NASA\u2019s PSI record gives no research-impact statement."; })(v.researchImpacts)),
+            h("p", null, (function (t) { t = clip(t, 420); return t ? t : "NASA\u2019s PSI record gives no research-impact statement."; })(v.researchImpacts)),
             h("p", { class: "note" }, "Quoted from NASA PSI (\u201cResearch impacts\u201d), full text below."))),
         h("p", { class: "note" }, h("b", null, "Variables and measurements: "), (v.table_summaries || []).length ? "NASA\u2019s table records " +
           v.table_summaries.map(function (t) { return (t.columns || []).length + " columns"; }).join(" + ") + " (listed below)." : "no experiment table in PSI.",
@@ -1585,7 +1602,8 @@
       text("Objective", v.objective), text("Approach", v.approach), text("Hypothesis", v.hypothesis), text("Research impacts", v.researchImpacts),
       (v.publications || []).length ? h("details", { class: "card tech" }, h("summary", null, h("b", null, "Publications listed by NASA PSI (" + v.publications.length + ")")),
         h("ul", { class: "fn", style: "margin-top:10px" }, v.publications.slice(0, 40).map(function (p) {
-          return h("li", null, p.title + (p.authors ? " — " + p.authors.split(",").slice(0, 3).join(",") + (p.authors.split(",").length > 3 ? " et al." : "") : "") + " ",
+          var au = (p.authors || "").replace(/\bundefined undefined\b/g, "[name missing in NASA PSI]");
+          return h("li", null, p.title + (au ? " — " + au.split(",").slice(0, 3).join(",") + (au.split(",").length > 3 ? " et al." : "") : "") + " ",
             p.doi ? h("a", { href: "https://doi.org/" + p.doi, target: "_blank", rel: "noopener" }, "DOI") : null); }))) : null,
       h("details", { class: "card tech" }, h("summary", null, h("b", null, "Why it scores " + rs.score + " / " + rm.score + " / " + rM.score)),
         h("p", { class: "mini-h" }, "Spacecraft & station"), h("ul", { class: "pts" }, rs.pts.map(function (p) { return h("li", null, h("b", null, "+" + p.n), " " + p.label); })),
@@ -1674,7 +1692,7 @@
     var btn = h("button", { type: "submit", class: "pill-btn" }, "Ask the Lab");
     function cite(id) {
       var c = (cur && cur.citations || []).filter(function (x) { return x.id === id; })[0];
-      return h("a", { class: "cite", href: c ? c.route : "#/", title: c ? c.source : id }, id);
+      return c ? h("a", { class: "cite", href: c.route, title: c.source }, id) : h("span", { class: "cite muted", title: "Not a retrieved document" }, id);
     }
     var cur = null;
     function renderLocal(q, why) {
@@ -1697,10 +1715,10 @@
           h("p", { class: "lab-sum" }, a.summary || (abst ? "The evidence does not support an answer." : "")),
           (a.key_points || []).length ? h("ul", { class: "kp" }, a.key_points.map(function (p) {
             var b = BASIS[p.basis] || BASIS.interpretation;
-            return h("li", null, chip(b[0], b[1]), " ", p.text, " ", h("span", { class: "cites" }, p.citations.map(cite)));
+            return h("li", null, chip(b[0], b[1]), " ", p.text, " ", h("span", { class: "cites" }, (p.citations || []).map(cite)));
           })) : null,
           abst && (a.instead || []).length ? h("div", { class: "lab-instead" }, h("b", null, "What the NASA records can tell you instead:"),
-            h("ul", { class: "kp" }, a.instead.map(function (p) { return h("li", null, p.text, " ", h("span", { class: "cites" }, p.citations.map(cite))); }))) : null,
+            h("ul", { class: "kp" }, a.instead.map(function (p) { return h("li", null, p.text, " ", h("span", { class: "cites" }, (p.citations || []).map(cite))); }))) : null,
           (a.gaps || []).length ? h("div", { class: "lab-gaps" }, h("b", null, "What the data does not cover: "), h("ul", null, a.gaps.map(function (t) { return h("li", null, t); }))) : null,
           h("p", { class: "note grade-rule" }, h("b", null, "Grade rule: "), g.text + " The grade is computed by Flare AI from the citations that survived checking, not chosen by the AI." +
             (a.dropped_points ? " " + a.dropped_points + " point(s) were removed because their citations did not match any retrieved document." : "")),
@@ -1710,14 +1728,16 @@
         (a.evidence || []).length ? h("details", { class: "card tech" }, h("summary", null, h("b", null, "All " + a.evidence.length + " documents retrieved for this question")),
           h("ul", { class: "fn", style: "margin-top:8px" }, a.evidence.map(function (c) { return h("li", null, h("a", { href: c.route }, c.id), " — " + c.title + " ", h("span", { class: "muted" }, "(" + c.kind + ", " + c.source + ")")); }))) : null);
     }
+    var busy = false;
     function ask(q) {
+      if (busy) return; /* one question at a time: the example buttons stay clickable while an answer is on its way */
       q = (q || "").trim();
       if (q.length < 8) { out.textContent = ""; out.appendChild(h("p", { class: "fwarn" }, "Please ask a full question.")); return; }
       ta.value = q; counter.textContent = q.length + " / 300";
       out.textContent = "";
       var ep = labEndpoint();
       if (!ep) { out.appendChild(renderLocal(q, "The AI answers need the online site (they run on a secure server). Offline, Flare AI shows the records that match your words instead.")); return; }
-      btn.disabled = true; btn.textContent = "Checking the records…";
+      busy = true; btn.disabled = true; btn.textContent = "Checking the records…";
       out.appendChild(h("p", { class: "muted" }, "Retrieving NASA records and asking the SI (Google Gemini) to answer only from them…"));
       fetch(ep, { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ question: q }) })
         .then(function (r) { return r.json().then(function (b) { return { ok: r.ok, status: r.status, b: b }; }, function () { return { ok: false, status: r.status, b: {} }; }); })
@@ -1726,7 +1746,8 @@
           if (res.ok) out.appendChild(renderAnswer(res.b, q));
           else out.appendChild(renderLocal(q, (res.b && res.b.error ? res.b.error + " " : "The SI service did not answer (" + res.status + "). ") + "Showing keyword matches instead."));
         }, function () { out.textContent = ""; out.appendChild(renderLocal(q, "Could not reach the SI service. Showing keyword matches instead.")); })
-        .then(function () { btn.disabled = false; btn.textContent = "Ask the Lab"; });
+        .catch(function () { out.textContent = ""; out.appendChild(renderLocal(q, "The SI answer could not be displayed. Showing keyword matches instead.")); })
+        .then(function () { busy = false; btn.disabled = false; btn.textContent = "Ask the Lab"; });
     }
     var form = h("form", { class: "lab-form", onsubmit: function (e) { e.preventDefault(); ask(ta.value); } },
       h("label", { for: "labq", class: "sr" }, "Your question"), ta, h("div", { class: "lab-row" }, counter, btn));
@@ -1965,7 +1986,7 @@
     setTitle("Scenario Check");
     ensureTip();
     var st = { family: "solid", o2: 21, psi: 14.7, fuel: "", diluent: "" };
-    (arg || "").split("&").forEach(function (kv) { var p = kv.split("="); if (p[0] in st) st[p[0]] = p[0] === "o2" || p[0] === "psi" ? parseFloat(p[1]) : decodeURIComponent(p[1] || ""); });
+    (arg || "").split("&").forEach(function (kv) { var p = kv.split("="); if (p[0] in st) st[p[0]] = p[0] === "o2" || p[0] === "psi" ? parseFloat(p[1]) : safeDecode(p[1] || ""); });
     var out = h("div", { class: "scen-out", "aria-live": "polite" });
     var o2In = h("input", { type: "number", id: "so2", min: 0, max: 100, step: 0.5, value: st.o2 });
     var pIn = h("input", { type: "number", id: "spsi", min: 0, max: 60, step: 0.1, value: st.psi });
@@ -1986,7 +2007,7 @@
     }
     function run() {
       st.o2 = parseFloat(o2In.value); st.psi = parseFloat(pIn.value); st.fuel = fuelSel.value; st.diluent = dilSel.value;
-      try { history.replaceState(null, "", "#/scenario/family=" + st.family + "&o2=" + st.o2 + "&psi=" + st.psi + (st.family === "liquid" ? "&fuel=" + st.fuel + "&diluent=" + st.diluent : "")); } catch (e) { /* sandboxed previewers */ }
+      try { history.replaceState(null, "", "#/scenario/family=" + st.family + "&o2=" + (isNaN(st.o2) ? "" : st.o2) + "&psi=" + (isNaN(st.psi) ? "" : st.psi) + (st.family === "liquid" ? "&fuel=" + st.fuel + "&diluent=" + st.diluent : "")); } catch (e) { /* sandboxed previewers */ }
       out.textContent = "";
       if (isNaN(st.o2) || isNaN(st.psi) || st.o2 < 0 || st.o2 > 100 || st.psi <= 0) { out.appendChild(h("p", { class: "fwarn" }, "Enter oxygen between 0 and 100% and a pressure above 0 psi.")); return; }
       out.appendChild(result());
@@ -2046,7 +2067,7 @@
       var TABS = [["inside", "Inside the window", inside], ["partial", "Oxygen only", partial], ["outside", "Outside, nearest first", outside], ["omitted", "Omitted", omitted]];
       var tab = inside.length ? "inside" : partial.length ? "partial" : "outside";
       function rowFor(t) {
-        var r = t.c.r, note = t.c.outcome ? "Test end: " + t.c.outcome : (r.observation || "").slice(0, 110) + ((r.observation || "").length > 110 ? "…" : "");
+        var r = t.c.r, note = t.c.outcome ? "Test end: " + t.c.outcome : clip(r.observation, 110);
         var catTxt = { inside: "inside", partial: "oxygen only", outside: "outside", omitted: "omitted" }[t.cat];
         return h("tr", null,
           h("th", { scope: "row", "data-label": "Test" }, h("a", { href: "#/experiment/" + r.id }, testLabel(r)), h("span", { class: "cat-tag ct-" + t.cat }, catTxt)),
@@ -2275,7 +2296,7 @@
   /* ---------- router ---------- */
   /* Record pages link back to the page the visitor came from (search results, a comparison, a scenario...),
    * falling back to Flame Explorer when they arrived directly. */
-  var prevHash = "", curHash = "";
+  var prevHash = "", curHash = "", rendered = false;
   var PAGE_NAMES = { explorer: "Flame Explorer", compare: "Compare", scenario: "Scenario Check", lab: "Intelligence Lab",
     investigation: "the investigation", investigations: "Investigations", lessons: "Lessons", about: "About", "": "Overview" };
   function backLink() {
@@ -2295,13 +2316,13 @@
     var seg = hash.replace(/^#\/?/, "").split("/");
     var route = seg[0] || "overview", view;
     if (route === "explorer") view = viewExplorer();
-    else if (route === "experiment") view = viewDetail(decodeURIComponent(seg[1] || ""));
+    else if (route === "experiment") view = viewDetail(safeDecode(seg[1] || ""));
     else if (route === "about") view = viewAbout();
     else if (route === "lessons") view = viewLessons();
     else if (route === "compare") view = viewCompare(seg.slice(1).join("/"));
     else if (route === "investigations" && seg[1] === "compare") view = viewInvCompare(seg[2] || "");
     else if (route === "investigations") view = viewInvestigations(seg[1] || "");
-    else if (route === "investigation") view = viewInvestigation(decodeURIComponent(seg[1] || ""));
+    else if (route === "investigation") view = viewInvestigation(safeDecode(seg[1] || ""));
     else if (route === "lab") view = viewLab();
     else if (route === "scenario") view = viewScenario(seg.slice(1).join("/"));
     else if (route === "overview" || !/^#\//.test(hash)) { route = "overview"; view = viewOverview(); }
@@ -2314,6 +2335,9 @@
       else a.removeAttribute("aria-current");
     });
     window.scrollTo(0, 0);
+    /* After in-app navigation, put keyboard and screen-reader focus on the new page, not on the old link. */
+    if (rendered && main.contains(document.activeElement) === false) main.focus({ preventScroll: true });
+    rendered = true;
   }
   window.addEventListener("hashchange", render);
 
```

---

## Section 9: Implementation code for the top upgrades (U-01 and U-02)

Apply after Section 8.
- **U-01:** Explorer filters live in the address (`#/explorer/q=pmma&exp=BASS-II&o2=16-18`). Refresh, back and shared links keep them; invalid values are dropped. The investigation page's record link opens Explorer filtered to that experiment.
- **U-02:** Scenario Check gets a "Download evidence brief (.md)" button.
- **Verified:**
  - filtered hash after selection;
  - refresh keeps "6 of 537";
  - the record back link restores the filters;
  - `#/explorer/exp=NOPE&o2=bogus&pi=Olson` normalises to `pi=Olson` (27 rows);
  - PSI-69 link gives `#/explorer/exp=FLEX` (274 rows);
  - the brief downloads as `flare-ai-scenario-solid-21pct-14.7psi.md` with 137 cited test rows;
  - all suites still pass.

```diff
diff --git a/site/js/app.js b/site/js/app.js
index f585fb4..75822d3 100644
--- a/site/js/app.js
+++ b/site/js/app.js
@@ -397,9 +397,11 @@
     } catch (err) { fallback(); }
   }
 
-  function viewExplorer() {
+  function viewExplorer(arg) {
     setTitle("Flame Explorer");
     var state = { q: "", exp: "", pi: "", flow: "", o2: "" };
+    (arg || "").split("&").forEach(function (kv) { var i = kv.indexOf("="); if (i > 0 && kv.slice(0, i) in state) state[kv.slice(0, i)] = safeDecode(kv.slice(i + 1)).trim(); });
+    if (state.q) state.q = state.q.toLowerCase();
     var exps = EXP_ORDER.filter(function (e) { return ROWS.some(function (r) { return r.experiment === e; }); });
     var pis = uniq(ROWS.map(function (r) { return r.pi; }).filter(Boolean));
     var flows = uniq(ROWS.map(function (r) { return r.flow_mode; }).filter(Boolean));
@@ -445,7 +447,13 @@
       return key === "q" ? "“" + state.q + "”" : state[key];
     }
     function open(r) { location.hash = "#/experiment/" + r.id; }
+    function syncUrl() {
+      var qs = Object.keys(state).filter(function (k) { return state[k]; }).map(function (k) { return k + "=" + encodeURIComponent(state[k]); }).join("&");
+      var want = "#/explorer" + (qs ? "/" + qs : "");
+      if (location.hash !== want) { curHash = want; try { history.replaceState(null, "", want); } catch (e) { /* sandboxed previewers */ } }
+    }
     function draw() {
+      syncUrl();
       var list = ROWS.filter(function (r) {
         if (state.exp && r.experiment !== state.exp) return false;
         if (state.pi && r.pi !== state.pi) return false;
@@ -496,6 +504,7 @@
       sel("fpi", "BASS-II investigator", pis.map(function (p) { return [p, p]; }), "pi"),
       sel("fflow", "Flow direction", flows.map(function (p) { return [p, p]; }), "flow"),
       sel("fo2", "Starting O2", o2opts, "o2"));
+    Object.keys(controls).forEach(function (k) { controls[k].value = state[k]; if (controls[k].value !== state[k]) state[k] = ""; });
     draw();
     return h("div", null,
       h("div", { class: "page-head" },
@@ -1564,7 +1573,7 @@
             h("div", { class: "rh-actions" },
               h("a", { class: "btn", href: v.landing_page, target: "_blank", rel: "noopener" }, "Open NASA’s PSI page ↗"),
               h("a", { class: "textlink", href: "https://doi.org/" + v.doi, target: "_blank", rel: "noopener" }, "DOI"),
-              ours.length ? h("a", { class: "textlink", href: "#/explorer" }, ours.length + " test records in Flare AI" +
+              ours.length ? h("a", { class: "textlink", href: "#/explorer/exp=" + encodeURIComponent(ours[0].experiment) }, ours.length + " test records in Flare AI" +
                 (oursReport ? " (" + oursReport + " from NASA\u2019s BASS-II report, " + (ours.length - oursReport) + " only in this PSI table)" : "")) : null),
             (function () {
               var cite = "NASA Physical Sciences Informatics (PSI). " + v.title + " (" + v.accession + (v.investigationAcronym ? ", " + v.investigationAcronym : "") +
@@ -2127,8 +2136,26 @@
       }
       drawPanels();
       var omittedWhy = {}; omitted.forEach(function (t) { omittedWhy[t.why] = (omittedWhy[t.why] || 0) + 1; });
+      function srcLine(r) { return fromReport(r) ? "NASA/TM-20210011385, Appendix A, report page " + r.source_page : "NASA PSI " + (r.source_id || "") + ", " + (r.source_file || "").split(",")[0] + ", row " + (r.source_row || ""); }
+      function mdRow(t) { var r = t.c.r; return "| " + [testLabel(r), r.material_raw, isNaN(t.c.o2) ? "—" : f1(t.c.o2) + "% (" + t.c.o2How + ")", isNaN(t.c.psi) ? "not recorded" : f1(t.c.psi) + " psi (" + t.c.pHow + ")",
+        isNaN(t.d) ? "—" : t.d.toFixed(2), t.c.outcome || clip(r.observation, 90) || "—", srcLine(r)].map(function (x) { return String(x).replace(/\|/g, "/"); }).join(" | ") + " |"; }
+      var briefBtn = h("button", { type: "button", class: "ghost small", onclick: function () {
+        var head2 = "| Test | Material | O2 (method) | Pressure | Distance (windows) | What NASA recorded | NASA source |\n|---|---|---|---|---|---|---|";
+        var md = ["# Flare AI evidence brief: Scenario Check", "",
+          "Scenario: " + { solid: "solid materials", liquid: "liquid droplets" }[st.family] + ", " + st.o2 + "% O2, " + st.psi + " psi" + (st.family === "liquid" ? ", fuel " + (st.fuel || "any") + ", diluent " + (st.diluent || "any") : "") + ".",
+          "Link: " + location.href, "Generated: " + new Date().toISOString().slice(0, 10), "",
+          "## Verdict", "", head.replace(/^[✓!✕] /, ""), "", body, "", env, "",
+          "Counts: " + inside.length + " inside the window; " + partial.length + " oxygen-only matches; " + outside.length + " outside; " + omitted.length + " omitted (no usable oxygen value).", "",
+          "## Tests inside the window", "", inside.length ? head2 + "\n" + inside.map(mdRow).join("\n") : "None.", "",
+          "## Oxygen-only matches (pressure not recorded)", "", partial.length ? head2 + "\n" + partial.map(mdRow).join("\n") : "None.", "",
+          "## Nearest tests outside the window (up to 10)", "", outside.length ? head2 + "\n" + outside.slice(0, 10).map(mdRow).join("\n") : "None.", "",
+          "## Rules", "", "- Window: ±" + MATCH.o2 + " points O2 and ±" + MATCH.psi + " psi. Each experiment keeps its own oxygen method; solids are never matched with droplets.",
+          "- Conversions: atm × 14.6959 and mmHg × 0.0193368 to psi; fractions × 100 to %.",
+          "- Flare AI helps people find NASA microgravity fire evidence. It does not calculate fire probabilities or certify safety. NASA does not endorse this project.", ""].join("\n");
+        saveFile("flare-ai-scenario-" + st.family + "-" + st.o2 + "pct-" + st.psi + "psi.md", md, "text/markdown;charset=utf-8");
+      } }, "Download evidence brief (.md)");
       return h("div", null,
-        h("section", { class: "card verdict " + cls }, h("p", { class: "v-h" }, head), h("p", null, body), counts, h("p", { class: "note" }, env)),
+        h("section", { class: "card verdict " + cls }, h("p", { class: "v-h" }, head), h("p", null, body), counts, h("p", { class: "note" }, env), briefBtn),
         h("figure", { class: "card qcard scen-fig" },
           h("figcaption", null, h("h3", null, "Did NASA test near your scenario?"), zBtns),
           h("div", { class: "cover-sum", role: "note" },
@@ -2315,7 +2342,7 @@
     if (hash !== curHash) { prevHash = curHash; curHash = hash; }
     var seg = hash.replace(/^#\/?/, "").split("/");
     var route = seg[0] || "overview", view;
-    if (route === "explorer") view = viewExplorer();
+    if (route === "explorer") view = viewExplorer(seg.slice(1).join("/"));
     else if (route === "experiment") view = viewDetail(safeDecode(seg[1] || ""));
     else if (route === "about") view = viewAbout();
     else if (route === "lessons") view = viewLessons();
```

---

## Section 10: Pre-submission verification checklist and automated test script

### 10.1 Checklist (run in this order before every push and before submitting)

1. `python3 scripts/build_site_data.py`. Only date stamps may change: `git diff --stat site/data/data.js`.
2. `python3 scripts/verify-all.py` (below). It must end with `0 failed`.
3. Open the live site in a private window. Check:
   - `#/`, `#/scenario` (Moon preset), `#/investigation/PSI-25` (says 129), `#/lab` (page loads; don't ask a question unless you intend to);
   - one record page.
4. Demo video: 30 s or less, English captions, "Edited with SI" watermark, link public with no login.
5. Submission form: all fields filled, NASA data listed, SI use declared, both boxes ticked, **Submit for Judging** clicked before 11:59 PM local time.

### 10.2 `scripts/verify-all.py`

Run against the current `main` it **fails with exactly the bugs above**:
- mid-word cuts on Scenario and investigation pages;
- `URI malformed` on `#/experiment/%E0%A4%A`;
- "undefined undefined" on PSI-10;
- "3 test records in Flare AI".

Against the patched copy: **18 passed, 0 failed**.

```python
#!/usr/bin/env python3
"""Flare AI pre-push verification: run before every `git push`. Exit code 0 = all checks passed.

  python3 scripts/verify-all.py              # data + every page of the local site (site/), plus the repo's own test suites
  python3 scripts/verify-all.py --url URL    # browser checks against a running copy instead (e.g. the live site)
  python3 scripts/verify-all.py --quick      # skip the repo's own test suites

It never sends a question to the Intelligence Lab: /api/* is intercepted in the browser.
Needs: python3, openpyxl, playwright (Chromium). CHROMIUM=/path/to/chrome overrides the browser.
"""
import argparse, asyncio, csv, functools, http.server, json, os, pathlib, re, shutil, subprocess, sys, threading, warnings

warnings.filterwarnings("ignore")
ROOT = pathlib.Path(__file__).resolve().parent.parent
SITE, PSI = ROOT / "site", ROOT / "data" / "source" / "psi"
FAILS, PASSES = [], 0


def check(name, ok, detail=""):
    global PASSES
    if ok:
        PASSES += 1
    else:
        FAILS.append(f"{name}: {detail}")
        print(f"FAIL {name}: {detail}")


def load_data():
    node = shutil.which("node")
    if not node:
        sys.exit("node is required to read site/data/data.js")
    out = subprocess.run([node, "-e", "global.window={};require(process.argv[1]);process.stdout.write(JSON.stringify(window.FLARE_DATA))",
                          str(SITE / "data" / "data.js")], capture_output=True, text=True, check=True)
    return json.loads(out.stdout)


# ---------------------------------------------------------------- 1. data
def data_checks(D):
    R, INV, C = D["records"], D["investigations"], D["counts"]
    ids = [r["id"] for r in R]
    check("record ids unique", len(ids) == len(set(ids)), [i for i in set(ids) if ids.count(i) > 1][:5])
    check("investigation ids unique", len({v["accession"] for v in INV}) == len(INV))
    check("records count == counts.records", len(R) == C["records"], (len(R), C["records"]))
    check("investigations count == counts.investigations", len(INV) == C["investigations"], (len(INV), C["investigations"]))
    per = {}
    for r in R:
        per[r["experiment"]] = per.get(r["experiment"], 0) + 1
    check("records per experiment == counts.experiments", per == C["experiments"], (per, C["experiments"]))
    check("verified count", sum(1 for r in R if r.get("verified")) == C["verified"])
    check("machine count", sum(1 for r in R if r.get("machine")) == C["machine"])
    moji = re.compile(r"Ã.|â€|�")
    bad = [(r["id"], k) for r in R for k, v in r.items() if isinstance(v, str) and (moji.search(v) or v in ("undefined", "NaN", "null"))]
    check("no broken encoding or literal undefined/NaN/null in records", not bad, bad[:5])
    # every BASS-I / FLEX / SAFFIRE / PSI-only BASS-II value equals NASA's cell
    cache = {}

    def rows(f):
        if f not in cache:
            if f.endswith(".xlsx"):
                import openpyxl
                ws = openpyxl.load_workbook(PSI / f, data_only=True)["as run matrix"]
                cache[f] = [list(x) for x in ws.iter_rows(values_only=True)]
            else:
                for enc in ("utf-8-sig", "cp1252"):
                    try:
                        cache[f] = list(csv.reader(open(PSI / f, encoding=enc, newline="")))
                        break
                    except UnicodeDecodeError:
                        pass
        return cache[f]

    def norm(x):
        if hasattr(x, "strftime"):
            x = x.strftime("%Y-%m-%d")
        return " ".join(str("" if x is None else x).replace(" ", " ").split())

    mism = []
    for r in R:
        if r["experiment"] == "BASS-II" and r.get("raw_text"):
            continue
        row = rows(r["source_file"].split(",")[0])[int(r["source_row"]) - 1]
        cells = [norm(c) for c in row]
        nums = [c for c in row if isinstance(c, (int, float))]
        for lab, val in r.get("fields", []):
            if lab.startswith("Note in NASA"):
                continue
            v = norm(val)
            if v.endswith("(rounded)"):
                x = float(v.split()[0])
                ok = any(abs(c - x) < 5e-5 for c in nums)
            else:
                ok = not v or v in cells or (re.fullmatch(r"-?[\d.]+", v) and any(re.fullmatch(r"-?[\d.]+(e-?\d+)?", c or "x") and abs(float(c) - float(v)) < 1e-9 for c in cells))
            if not ok:
                mism.append((r["id"], lab, v))
    check("every PSI record value equals NASA's cell", not mism, mism[:5])
    # BASS-II report rows: each parsed reading is a token of the report row text
    rep = [(r["id"], k) for r in R if r.get("raw_text") for k in ("o2_cal_initial", "o2_cal_final", "o2_raw_initial", "o2_raw_final", "co2_initial", "co2_final", "co_initial_ppm", "co_final_ppm")
           if r.get(k) and r[k] not in r["raw_text"].split()]
    check("BASS-II readings appear in their report row", not rep, rep[:5])


# ---------------------------------------------------------------- 2. secrets
def secret_checks():
    pat = re.compile(r"AIza[0-9A-Za-z_\-]{30,}|sk-ant-[A-Za-z0-9_\-]{20,}|ghp_[A-Za-z0-9]{30,}|-----BEGIN [A-Z ]*PRIVATE KEY")
    files = subprocess.run(["git", "-C", str(ROOT), "ls-files"], capture_output=True, text=True).stdout.split()
    hits = []
    for f in files:
        p = ROOT / f
        if p.suffix in (".mp4", ".webm", ".png", ".jpg", ".pdf", ".woff2", ".xlsx", ".ico") or not p.is_file():
            continue
        try:
            if pat.search(p.read_text(errors="ignore")):
                hits.append(f)
        except OSError:
            pass
    check("no API keys or private keys in tracked files", not hits, hits)


# ---------------------------------------------------------------- 3. browser
BAD = re.compile(r"\bNaN\b|\bundefined\b|Infinity|\[object |(?<=[A-Za-z+])(?:ppm\b|vol%)")
FRAG = re.compile(r"\b(?:turne|ignitio|becam|understandin|envel|prolon|smal|sligh|poin|chal|micr|extinc|allo)…")


async def browser_checks(base, D):
    from playwright.async_api import async_playwright
    exe = os.environ.get("CHROMIUM") or ("/opt/pw-browsers/chromium" if os.path.exists("/opt/pw-browsers/chromium") else None)
    async with async_playwright() as p:
        b = await p.chromium.launch(**({"executable_path": exe} if exe else {}))
        routes = ["", "scenario", "scenario/family=solid&o2=30&psi=10.2", "scenario/family=liquid&o2=21&psi=14.7", "scenario/family=gas&o2=30&psi=10.2",
                  "explorer", "compare", "compare/BASSII-P1,BASSII-P10,BASSII-P12", "compare/BASSII-B1,BASSI-1-1", "investigations", "investigations/moon",
                  "investigations/mars", "investigations/compare/PSI-25,PSI-69", "lab", "lessons", "about", "nonexistent", "experiment/%E0%A4%A"]
        routes += ["investigation/" + v["accession"] for v in D["investigations"]] + ["experiment/" + r["id"] for r in D["records"]]
        for w, sample in ((1280, routes), (375, routes[:18])):
            ctx = await b.new_context(viewport={"width": w, "height": 900})
            await ctx.route(re.compile(r".*/api/.*|.*/\.netlify/functions/.*"), lambda r: r.abort())
            pg = await ctx.new_page()
            errs = []
            pg.on("pageerror", lambda e: errs.append(str(e)[:120]))
            await pg.goto(base, wait_until="load")
            await pg.wait_for_timeout(300)
            probs = []
            for r in sample:
                n0 = len(errs)
                await pg.goto(base + "#/" + r)
                await pg.wait_for_timeout(60)
                await pg.evaluate("document.querySelectorAll('main details').forEach(d => d.open = true)")
                t = await pg.evaluate("document.querySelector('main').innerText + ' ' + [...document.querySelectorAll('main svg')].map(s => s.textContent + ' ' + (s.getAttribute('aria-label') || '')).join(' ')")
                if not t.strip():
                    probs.append((r, "empty page"))
                m = BAD.search(t)
                if m:
                    probs.append((r, "bad text: " + t[max(0, m.start() - 30):m.end() + 10].replace("\n", " ")))
                m = FRAG.search(t)
                if m:
                    probs.append((r, "word cut mid-way: " + m.group(0)))
                if await pg.evaluate("document.documentElement.scrollWidth > innerWidth + 1"):
                    probs.append((r, "horizontal overflow"))
                if len(errs) > n0:
                    probs.append((r, "page error: " + errs[-1]))
            check(f"all {len(sample)} pages clean at {w}px", not probs, probs[:8])
            await ctx.close()
        # record counts per investigation page agree with the data
        ctx = await b.new_context()
        await ctx.route(re.compile(r".*/api/.*"), lambda r: r.abort())
        pg = await ctx.new_page()
        await pg.goto(base + "#/investigation/PSI-25")
        await pg.wait_for_timeout(400)
        t = await pg.inner_text("main")
        n = sum(1 for r in D["records"] if r["experiment"] == "BASS-II")
        check("BASS-II investigation page shows all its records", f"{n} test records in Flare AI" in t, re.findall(r"\d+ test records in Flare AI", t))
        await b.close()


def serve(path, port=8799):
    class Quiet(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *a):
            pass
    handler = functools.partial(Quiet, directory=str(path))
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", port), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return f"http://127.0.0.1:{port}/"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--url")
    ap.add_argument("--quick", action="store_true")
    a = ap.parse_args()
    D = load_data()
    print("== data"); data_checks(D)
    print("== secrets"); secret_checks()
    print("== browser"); asyncio.run(browser_checks(a.url or serve(SITE), D))
    if not a.quick:
        print("== repo test suites")
        env = dict(os.environ)
        for t in ["crosscheck_mutation_test.py", "psi_import_test.py", "pdfcheck_mutation_test.py"]:
            r = subprocess.run([sys.executable, str(ROOT / "tests" / t)], capture_output=True, text=True, env=env)
            check(t, r.returncode == 0, r.stdout[-300:] + r.stderr[-300:])
        r = subprocess.run(["node", str(ROOT / "tests" / "lab_function_test.mjs")], capture_output=True, text=True)
        check("lab_function_test.mjs", r.returncode == 0, r.stdout[-300:])
    print(f"\n{PASSES} passed, {len(FAILS)} failed")
    sys.exit(1 if FAILS else 0)


if __name__ == "__main__":
    main()
```

---
*Prepared with SI (Claude) for 628 Aerospace. Every number in this report comes from a script run on 15 Nov 2026 against `main` @ `3456ce7` and the live deployment; the Intelligence Lab received no questions during the audit.*
