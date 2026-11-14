# Space Apps 2026 submission text: Flare AI

Paste each section into the matching field on the team's Project page (Project tab → Edit).
Replace every **[BRACKETED]** item first. Save often ("Save Progress"); submit with "Submit for Judging" before
**Sun 15 Nov, 11:59 p.m. local time**, after ticking both boxes.

---

## Project name

Flare AI

## High-level summary

Flare AI is a website that turns NASA's microgravity fire experiments into answers that mission planners, students and
engineers can check. It brings together all 24 combustion investigations in NASA's Physical Sciences Informatics (PSI)
system and 537 individual test records from BASS, BASS-II, FLEX and Saffire. Each record cites the NASA table, row
or report page it came from. Every record passed automated checks against NASA's own files, and our team checked all
537 by hand.

You can rank investigations for a spacecraft, a Moon base or a Mars base. You can compare experiments, or enter
conditions such as oxygen level and pressure and see the closest real NASA tests. You can also ask questions in plain
English. Flare AI never invents numbers, never pools experiments that measured oxygen differently, and says "the data
is insufficient" when NASA's tests don't cover a situation. That last point matters because the Moon-base atmosphere
in the challenge (30% oxygen or more at low pressure) lies outside every solid-material test in the data. Fire safety
for the Moon and Mars depends on knowing exactly what has and hasn't been tested, and Flare AI makes that visible.

## Project demo (link)

**[PUBLIC LINK TO THE 30-SECOND VIDEO OR THE SLIDE DECK]** (test it in a private browser window; no login required)

## Final project (link)

**[LIVE SITE LINK, e.g. https://….netlify.app]**
Source code: https://github.com/aaa628/flare-ai

## Project details

**What it does**
- **Investigations:** all 24 NASA PSI combustion investigations, grouped by fire-safety need (prevention, detection,
  suppression). They can be ranked for three habitats, Spacecraft / ISS, Moon base / rover and Mars base, using a
  scoring rule printed on the page; every point names its evidence. Each investigation has its own page with NASA's
  objective, hardware, tested oxygen and pressure ranges, publications and DOI.
- **Flame Explorer and test pages:** 537 test records you can search and filter. Every value shows NASA's original
  field name and unit, the source (report page or PSI file and row), and how the record was checked.
- **Compare:** side-by-side charts that refuse to compare experiments that measured oxygen differently, and say why.
- **Scenario Check:** enter a fuel family, oxygen (%) and pressure (psi), or pick a preset such as ISS air or the
  challenge's Moon-base atmosphere. It shows the real NASA tests closest to those conditions and what NASA recorded,
  and abstains outside the tested range. It gives no probabilities.
- **Intelligence Lab:** questions in plain English, answered by an SI model only from Flare AI's NASA documents.
  Every point cites a document id. Citations that don't match a real document are removed. The evidence grade is
  computed by a fixed rule, not chosen by the AI. When the records can't answer, the Lab abstains, explains why and
  points to what the records do show.
- **Lessons:** the challenge's background resources (Apollo 1, Apollo 13, the Mir fire, NASA spinoffs), each with
  NASA quotes checked word for word on every build, plus our labelled interpretation linking it to the data.

**How it works**
- Python scripts download NASA's PSI files and the BASS-II report (NASA/TM-20210011385), extract the test tables and
  run automated cross-checks on every build. For example, all 126 BASS-II report records match the PDF value for value,
  and three disagreements with NASA's own spreadsheet are shown on those records rather than hidden.
- The website is plain HTML, CSS and JavaScript with no tracking. It also works offline from a single folder.
- The Intelligence Lab runs as one Netlify Function. The SI API key stays on the server and never reaches the
  browser. The function enforces per-visitor and daily limits and caches answers.

**Benefits**
Planners and students can see in seconds what NASA has actually tested, under which conditions, and with what
outcome, with a source for every number. They can also see clearly what has not been tested, such as partial gravity
and a Moon-base atmosphere, so research gaps are visible instead of being guessed over.

**What we hope to achieve**
To be a trustworthy starting point for spacecraft and habitat fire-safety questions: a tool that is honest about the
limits of the data, and that can grow as NASA publishes new results, such as the FM2 experiment on the Moon.

**Tools:** HTML, CSS, JavaScript; Python (openpyxl, pdftotext/poppler) for data extraction and checks; Netlify
(hosting and one serverless function, Netlify Blobs for limits and cache); Google Gemini API (Intelligence Lab
answers); Playwright (automated browser tests); GitHub.

## NASA data and resources used

- **NASA Physical Sciences Informatics (PSI)**, https://psi.nasa.gov: the catalogue of all 24 combustion investigations
  and these experimental tables (all CC0-1.0):
  - PSI-25 BASS-II experimental table, DOI 10.60555/4qc4-de67
  - PSI-26 BASS As Run Test Matrix, DOI 10.60555/58h4-dy80
  - PSI-69 FLEX experimental table, DOI 10.60555/mbq8-0451
  - PSI-68 FLEX-2 planned test matrix, DOI 10.60555/byp8-h018
  - PSI-98 / PSI-99 / PSI-100 Saffire-I / II / III experimental tables, DOIs 10.60555/0t15-1z43, 10.60555/2chp-m469,
    10.60555/040q-4h36
- **NASA Technical Reports Server:** Olson, S.L. et al., *Burning and Suppression of Solids-II (BASS-II) Summary
  Report*, NASA/TM-20210011385 (2021), https://ntrs.nasa.gov/citations/20210011385
- **The challenge's Resources tab:** Apollo 1 and Apollo 13 (NASA OSMA Lessons Learned); 25 Years Ago: Fire Aboard
  Space Station Mir (NASA); NASA Combustion Science (Glenn Research Center); A Researcher's Guide to ISS Combustion
  Science; NASA ScienceCasts: The Power of Studying Combustion on the ISS; NASA Spinoff: Fireman's Air Tanks, Fire
  Detector, New Technology for the Fire Attire.
- **NASA Scientific Visualization Studio:** "Spherical Flames" (ID 11640), https://svs.gsfc.nasa.gov/11640. Credit:
  Science@NASA and NASA's Goddard Space Flight Center. Edited background video on the home page (decoration only).

## Space Agency Partner data

We used NASA data only. Saffire was an international collaboration, but the tables we used are NASA PSI files.

## References

**Data and text**
- Everything under "NASA data and resources used" above.
- NASA Space Apps Challenge 2026, "Flame in Freefall" challenge brief and Resources tab,
  https://www.spaceappschallenge.org/2026/challenges/flame-in-freefall/

**Images and media**
- "Spherical Flames", NASA SVS ID 11640 (credit above), edited by the team: cropped, trimmed, looped, audio removed.
- "BASS-II Experiment" photo, NASA Image and Video Library ID iss040e088023 (ISS Expedition 40, 2014, astronaut Reid
  Wiseman), https://images.nasa.gov/details/iss040e088023. Credit: NASA. Used in the demo video's opening (cropped, slow zoom).
- Demo video: screen captures of Flare AI, assembled with SI (Claude) and marked "Edited with SI".
- 628 Aerospace emblem: original work by the team.
- Flame illustration on the home page: made with SI (Claude) and visibly watermarked "Illustration made with SI (Claude)".

**Fonts**
- IBM Plex Sans, SIL Open Font License 1.1, https://github.com/IBM/plex
- Space Grotesk, SIL Open Font License 1.1, https://github.com/floriankarsten/space-grotesk

**Code libraries and services**
- @netlify/blobs (Netlify), @anthropic-ai/sdk (Anthropic; optional Lab provider)
- Python: openpyxl; poppler-utils (pdftotext)
- Playwright (testing only)
- Netlify (hosting and functions); Google Gemini API (Lab answers); GitHub (code hosting)

**SI tools**
- Claude (Anthropic): coding assistant, see the SI section below.
- Google Gemini API: writes the Intelligence Lab's answers on the live site.

## SI question: "Did you use any SI tools? If yes, how?"

(This answer is not shown to judges.)

Yes.
- **Claude (Anthropic)** was our coding and writing assistant. It helped write the website code, the Python
  data-extraction and checking scripts, the automated tests and draft text (for example, plain-language summaries,
  which are labelled "Written with SI (Claude)" on the site). It also drew the flame illustration, which carries a
  visible "Illustration made with SI (Claude)" watermark.
- **Google Gemini** writes the answers in the site's Intelligence Lab. Every answer is labelled as an SI answer and
  names the model. It may use only the NASA documents Flare AI retrieves, and our code removes any citation that
  doesn't match a real document.
- **The idea, the design decisions and the checking were ours.** **[CONFIRM: the idea for Flare AI came from our team,
  not from an SI tool. The rules say SI must not be used to come up with the idea.]** NASA's data values are copied
  from NASA's files, not generated by SI, and the team compared all 537 records with NASA's sources by hand.
- The site uses no NASA logos or other NASA branding.

---

### Before you submit
- [ ] All [BRACKETED] items replaced.
- [ ] Demo link and live link open in a private browser window.
- [ ] No faces or voices of anyone under 18 in the demo; English subtitles if you speak another language.
- [ ] Both boxes ticked, then **Submit for Judging**, and the confirmation banner appears.
