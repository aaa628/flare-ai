# Flare AI

Evidence-graded fire safety insights from NASA microgravity combustion data.
Built for the **NASA Space Apps Challenge 2026: Flame in Freefall**.

> Flare AI tells a mission planner what NASA's fire experiments actually prove
> about a situation, and says "the available data is insufficient" when the
> data does not cover it.

## Principles (non-negotiable)

1. **No invented numbers.** Every statistic is computed from records in `data/`.
2. **Every field is labelled** as `measured`, `published_conclusion`, or `our_interpretation`.
3. **Never compare incompatible measurements** as if they were equivalent.
4. **Abstain outside tested conditions.** Show the closest real experiments instead of guessing.
5. **No fire probabilities, no safety certification.** This is a research-navigation tool.
6. **Every record cites its source** (NTRS / PSI identifier and page).

## Screens (Mark 1)

| Screen | Purpose |
|---|---|
| Overview | Real counts from indexed records, featured experiment, key findings |
| Flame Explorer | Search/filter experiments, detail pages with source links |
| Compare | Side-by-side comparison with missing-data flags and incompatibility refusal |
| Intelligence Lab | Source-grounded Q&A with evidence grade and citations |
| Scenario Check | Spread/extinction prediction that abstains outside tested range, exports a PDF brief |
| About | Data sources, credits, limitations |

## Run locally

```bash
pip install -r requirements.txt
streamlit run app/Home.py
```

## Data

See [`data/README.md`](data/README.md) for the schema and verification workflow.
Sources: NASA Physical Sciences Informatics (psi.nasa.gov, CC0) and the NASA
Technical Reports Server (ntrs.nasa.gov). NASA does not endorse this project.

## Team

Studio 628 / 628 Aerospace — NASA Space Apps 2026 (virtual).

## AI-use disclosure

This project is developed with AI assistance (Claude). The team reviews,
verifies and can explain all data, code and claims. Check the official
Participant Guides (released Nov 13) for current rules on AI use and pre-built code.
