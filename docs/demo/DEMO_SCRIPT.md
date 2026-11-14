# Flare AI: 30-second demo video script

**File:** `flare-ai-demo-silent.mp4` (29.5 s, 1920×1080, English captions burned in, no sound yet).
**Subtitles:** `flare-ai-demo.srt` (the same lines, if YouTube asks for a caption file).

## Rules this video follows (Space Apps 2026)
- 30 seconds or less: it runs 29.5 s. **Don't add an intro or outro that makes it longer.**
- **No image, video or voice of anyone under 18.** The narrator must be **18 or older**. The video shows only screen
  captures of the site and NASA footage.
- English captions are on screen, so the voice can be in English or another language.
- The video was assembled with SI (Claude), so it carries a small "Edited with SI (Claude)" mark. **Leave it in.**
- The NASA footage is credited on screen (Science@NASA / NASA Goddard, SVS 11640). No NASA logos are used.

## Script (what's on screen, and what to say)

| Time | On screen | Narrator says (≈75 words in total) |
|---|---|---|
| 0:00–0:04 | NASA footage of a burning fuel droplet on the ISS (the "jellyfish" flame), title **Flare AI · 628 Aerospace · NASA Space Apps 2026 · Flame in Freefall** | "We're 628 Aerospace, and this is Flare AI." |
| 0:04–0:08.5 | Flare AI home page: "What NASA's fire experiments prove, and where the data stops" | "NASA's space-fire experiments: 24 investigations, 537 tests, in one place." |
| 0:08.5–0:12.5 | Investigations page with the Spacecraft / Moon base / Mars base choice and the Moon-base answer | "Rank them for a spacecraft, a Moon base or Mars." |
| 0:12.5–0:17 | A real test record (FLEX-114) with its NASA source, "Human-verified" and "Machine-checked" | "Every number links to its NASA source, and we checked every one by hand." |
| 0:17–0:22.5 | The Intelligence Lab abstaining on "What is the probability of a fire on a Mars rover?", with cited related facts | "Ask a question: our SI answers only from NASA's records, or tells you the data isn't there." |
| 0:22.5–0:26.5 | Scenario Check with the Moon-base atmosphere (30% O2, 10.2 psi): "Insufficient data: no NASA test near these conditions" | "Because on the Moon and Mars, knowing what's never been tested could save a crew." |
| 0:26.5–0:29.5 | End card: **Flare AI**, "What NASA's fire experiments prove, and where the data stops.", github.com/aaa628/flare-ai | *(silence, or just:)* "Flare AI." |

## Recording tips for the narrator
1. Use a quiet room. Hold the phone about a hand's width from your mouth, slightly to the side.
2. Read along while the silent video plays, so each line fits its scene. Line 5 is the longest, so say it briskly.
3. Record the whole thing in one take of about 30 seconds. Do 3–4 takes and keep the best one.
4. Save it as `.m4a`, `.mp3` or `.wav`, without background music unless it's royalty-free and listed in References.

## Putting the voice on the video
- **Easiest:** send the audio file back to Claude, and it will be mixed onto the video, trimmed to 30 s and normalised.
- **Or yourselves:** in CapCut, iMovie or Clipchamp, import `flare-ai-demo-silent.mp4`, add the audio track, line it
  up with the start, and export at 1080p. Keep it at 30 seconds or less.

## Uploading
1. YouTube: upload as **Unlisted** or **Public**. Not Private, because judges can't open private videos.
2. Optionally add `flare-ai-demo.srt` as English subtitles.
3. Test the link in a private browser window, then paste it into the "Project demo" field.

## Rebuilding the video
`build.py` and `cap.py` in this folder are the exact scripts used (Playwright screenshots of the site, then ffmpeg).
Change a caption in `build.py` and run it again to rebuild.
