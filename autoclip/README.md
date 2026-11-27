# AutoClip clips (first 25% of each source)

This folder holds the AutoClip thread's clips. To avoid duplicates with the other tools, it only uses the **first quarter** of each source video.

| Source | Range used |
|---|---|
| Twitch: Lauren Hamden, "GTA 6 LAUNCH!!!!" (https://www.twitch.tv/videos/2934045907, 1:02:52) | 0:00 to 15:43 |
| YouTube: MrBeast Gaming, "I Survived 100 Hours In GTA 6" (https://youtu.be/ymCHX_Dcc-U, 30:21) | 0:00 to 7:35 |

Every clip is 1080x1920, 30 fps, H.264 + AAC at 48 kHz, loudness normalised to about -14 LUFS. Each one has a bold hook title for the first 3 seconds and word-by-word burned-in captions (the current word is highlighted). Swear words are masked in the captions only. There are no watermarks or tool logos. Each `.mp4` has a matching `.txt` with a caption you can paste straight in.

## reels/ (Lauren Hamden campaign, Instagram Reels)

Layout: facecam on top, gameplay below. Every caption includes `@LaurenHamden` and `#LaurenHamden`.

| File | VOD timestamp | Length | Moment |
|---|---|---|---|
| lauren_01_boxer_shorts | 3:39 to 3:59 | 20s | "Why am I in here? ...I'm in boxer shorts" |
| lauren_02_dating_standards | 4:44 to 5:03 | 18s | Dating a shorter guy, "What would my kids think?" |
| lauren_03_croc_water | 6:42 to 6:57 | 15s | Falls into croc-infested water |
| lauren_04_only_australian | 8:16 to 8:35 | 19s | "I can't speak any other language other than Australian" |
| lauren_05_the_spade_saga | 10:27 to 11:00 | 33s | "I obviously need the spade" ... "I don't need the spade" |
| lauren_06_boat_stuck | 12:45 to 13:18 | 33s | Boat stuck, "I'm done for", then an alligator shows up |

Campaign checklist before posting: post on a Lauren Hamden themed account, put `https://lozzahamden.click/` in the bio, and post as a Reel only.

## shorts/ (top streamer source, YouTube Shorts / Reels / TikTok)

Layout: blurred fill with the gameplay and facecams enlarged in the middle.

| File | Video timestamp | Length | Moment |
|---|---|---|---|
| gta6_01_100_hours | 0:00 to 0:30 | 30s | Intro: "after 13 years", NPCs look real |
| gta6_02_girlfriend | 1:28 to 1:45 | 17s | "Playing GTA 6 before anyone got a girlfriend" |
| gta6_03_panic_attack_robbery | 1:57 to 2:26 | 29s | Clerk has a panic attack mid robbery |
| gta6_04_selfies | 3:17 to 3:40 | 23s | Discovering selfies in GTA 6 |
| gta6_05_she_has_a_family | 4:15 to 4:34 | 19s | "Jimmy, she has a family!" pawn shop robbery |
| gta6_06_cops_mid_heist | 4:54 to 5:25 | 31s | "They're here Jimmy!" cops arrive mid heist |
| gta6_07_helicopter_chase | 5:59 to 6:28 | 29s | Helicopter chase, "I give up bro" |

## How these were made

1. `yt-dlp` downloaded both sources, then the first quarter was cut out.
2. `faster-whisper` (small.en) transcribed it with word timestamps (`pipeline/transcribe.py`).
3. [AutoClip](https://github.com/zhouxiaoka/autoclip) v1.6.2 (`autoclip run --category entertainment`) segmented the transcript into topics and candidate segments, running on a local Qwen2.5-7B model. Those segments are 1 to 3 minutes long, so the final 15 to 35 second moments were picked inside them by hand. Picks favour funny moments, quotes and reactions, and skip anything that could show Lauren negatively.
4. `pipeline/render.py` did the 9:16 layout, hook title, captions and loudness. The exact ranges and caption corrections are in `pipeline/clips_*.json`.
