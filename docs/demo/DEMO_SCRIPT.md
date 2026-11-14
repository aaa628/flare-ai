# Flare AI: 30-second demo video script

**Final file:** `flare-ai-demo.mp4` (29.2 s, 1920×1080, narrator's voice + English captions burned in).
**Without voice:** `flare-ai-demo-silent.mp4` (same video, no sound). `mix_voice.py` puts the recording on it.
**Subtitles:** `flare-ai-demo.srt` (the same lines, if YouTube asks for a caption file).

## Rules this video follows (Space Apps 2026)
- 30 seconds or less: it runs 29.5 s. **Don't add an intro or outro that makes it longer.**
- **No image, video or voice of anyone under 18.** The narrator must be **18 or older**. The video shows only screen
  captures of the site and NASA footage.
- English captions are on screen, so the voice can be in English or another language.
- The video was assembled with SI (Claude), so it carries a small "Edited with SI" mark. **Leave it in.**
- The opening photo is credited on screen (NASA, ISS Expedition 40, image iss040e088023). No NASA logos are used.

## Script (what's on screen, and what to say)

| Time | On screen | Narrator says (≈80 words in total) |
|---|---|---|
| 0:00–0:04 | 4K NASA photo of a BASS-II flame on the ISS (slow push-in), title **Flare AI · 628 Aerospace · NASA Space Apps 2026 · Flame in Freefall** | "We're 628 Aerospace, and this is Flare AI." |
| 0:04–0:08 | Flare AI home page: "What NASA's fire experiments prove, and where the data stops" | "NASA's space-fire experiments: 24 investigations, 537 tests, in one place." |
| 0:08–0:11.5 | Investigations page with the Spacecraft / Moon base / Mars base choice and the Moon-base answer | "Rank them for a spacecraft, a Moon base or Mars." |
| 0:11.5–0:15.5 | Compare: three BASS-II rods, oxygen at the start vs the end of each test (bar charts) | "Compare tests like with like, or it refuses and explains why." |
| 0:15.5–0:19.5 | A real test record (FLEX-114) with its NASA source, "Human-verified" and "Machine-checked" | "Every number cites NASA, and we checked all 537 by hand." |
| 0:19.5–0:24 | The Intelligence Lab abstaining on "What is the probability of a fire on a Mars rover?", with cited related facts | "Our SI answers only from NASA's records, or says the data isn't there." |
| 0:24–0:28 | Scenario Check with the Moon-base atmosphere (30% O2, 10.2 psi): "Insufficient data: no NASA test near these conditions" | "On the Moon and Mars, knowing what's never been tested could save a crew." |
| 0:28–0:29.5 | End card: **Flare AI**, "What NASA's fire experiments prove, and where the data stops.", github.com/aaa628/flare-ai | *(silence)* |

## Recording tips for the narrator
1. Use a quiet room. Hold the phone about a hand's width from your mouth, slightly to the side.
2. Read along while the silent video plays, so each line fits its scene. Each line has about 4 seconds, so keep a brisk, steady pace.
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
`build.py`, `cap.py` and `capc.py` in this folder are the exact scripts used (Playwright screenshots of the site, the 4K NASA photo from `site/media` history, then ffmpeg).
Change a caption in `build.py` and run it again to rebuild.
