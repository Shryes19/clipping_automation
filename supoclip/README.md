# SupoClip clips (third quarter, 50-75% of each source)

This folder holds the SupoClip thread's clips. To avoid duplicates with the other tools, it only uses the **third quarter** of each source video.

| Source | Range used |
|---|---|
| Twitch: Lauren Hamden, "GTA 6 LAUNCH!!!!" (https://www.twitch.tv/videos/2934045907, 1:02:52) | 31:26 to 47:09 |
| YouTube: MrBeast Gaming, "I Survived 100 Hours In GTA 6" (https://youtu.be/ymCHX_Dcc-U, 30:21) | 15:10 to 22:46 |

Every clip is 1080x1920, 30 fps, H.264 + AAC at 48 kHz, loudness normalised to -14 LUFS, with metadata stripped. Each one opens with a bold hook title and has word-by-word burned-in captions (SupoClip's `hormozi` template: the current word is highlighted green). Dead air is trimmed with jump cuts. There are no watermarks or tool logos. Each `.mp4` has a matching `.txt` caption you can paste straight in.

## reels/ (Lauren Hamden campaign, Instagram Reels)

Layout: SupoClip gaming mode, with Lauren's facecam on top and gameplay below. The facecam stays on screen through cutscenes too. Every caption includes `@LaurenHamden` and `#LaurenHamden`.

| File | VOD timestamp | Length | Moment |
|---|---|---|---|
| lh01_reverse_truck | 32:16 to 33:17 | 28s | "How do you reverse a truck?" ... "we drove to the vault?" |
| lh02_keyless_car | 35:34 to 36:04 | 18s | "Can't start a keyless vehicle? What does that even mean?" + the Mandy story |
| lh03_boo_boo_jail | 36:44 to 37:30 | 21s | "Let's get our boo-boo girl out of jail" |
| lh04_so_close_home | 39:18 to 40:10 | 21s | Engine damaged, wrong lane, "We're so close to home" |
| lh05_cocaine_floor | 40:38 to 41:20 | 41s | Cal: "You ready to play?" Lauren: "Sure." "That is not a level of excitement" |
| lh06_crap_den | 43:52 to 44:42 | 39s | Roasting Cal's green room, "I'm being pranked", "this game is teaching men..." |

Campaign checklist before posting: post on a Lauren Hamden themed account, put `https://lozzahamden.click/` in the bio, and post as a Reel only.

## shorts/ (top streamer source, YouTube Shorts / Reels / TikTok)

Layout: SupoClip gaming mode (facecams on top, gameplay below), or a speaker-tracked crop where the source has no fixed facecam.

| File | Video timestamp | Length | Moment |
|---|---|---|---|
| yt01_first_bank_robbery | 18:46 to 19:21 | 34s | First bank robbery with Lucia, "$4,000?" |
| yt02_stole_jumbo_jet | 16:07 to 17:03 | 47s | Breaks into the Miami airport and steals a jet |
| yt03_cruise_ship | 17:09 to 17:37 | 19s | Crashes the plane, lands on a cruise ship |
| yt04_double_bank | 19:33 to 20:08 | 30s | Leading the cops from one bank to the next |
| yt05_left_lucia | 20:11 to 20:56 | 42s | Getaway goes wrong, "Sorry Lucia, have fun in jail" |
| yt06_cloud_physics | 21:06 to 22:02 | 49s | Flying through clouds, "GTA 6 has cloud physics" (subscribe plug cut out) |

## How it was made

- Download: yt-dlp (full video), then a local cut to the third quarter.
- Transcription: Whisper `medium` (faster-whisper, CPU, word timestamps), fed into SupoClip's transcript formatter and caption cache.
- Moment selection: SupoClip's AI analysis was run with local Ollama models (`gpt-oss:20b` ran out of memory on the 15 GB machine, and `qwen2.5:7b` failed SupoClip's structured-output checks). The moments were then picked by hand from the Whisper transcripts. See `pipeline/clips_*.json`.
- Rendering: SupoClip's own renderer (`create_optimized_clip`) with `GAMING_LAYOUT=auto`, the `hormozi` caption template, hook titles, and keep-ranges that trim silences. For Twitch, the gaming layout is locked to Lauren's facecam position (`batch_forced_gaming.py`).
- Finishing: `finalize.sh` (two-pass loudnorm to -14 LUFS, 1080x1920 at 30 fps, faststart).
