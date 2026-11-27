# OpenShorts clips (second 25% of each source)

This folder holds the OpenShorts thread's clips. To avoid duplicates with the other tools, it only uses the **second quarter** of each source video.

| Source | Range used |
|---|---|
| Twitch: Lauren Hamden, "GTA 6 LAUNCH!!!!" (https://www.twitch.tv/videos/2934045907, 1:02:52) | 15:43 to 31:26 |
| YouTube: "I Survived 100 Hours In GTA 6" (https://youtu.be/ymCHX_Dcc-U, 30:21) | 7:35 to 15:10 |

Every clip is 1080x1920 (9:16), 30 fps H.264 with AAC audio loudness-normalized to about -14 LUFS. Each one opens with a 3-second hook title and has burned-in word-by-word captions with the active word highlighted. Next to every `.mp4` is a `.txt` with the title, the source timestamps and a caption ready to paste.

## reels/ : Lauren Hamden campaign (Instagram Reels)

| File | Source time | Length | Title | On-screen hook |
|---|---|---|---|---|
| `reels/lauren_01_first_plane_flight.mp4` | 18:28 to 19:15 | 47s | Lauren's First GTA 6 Plane Flight Is Pure Chaos | POV: your first time flying in GTA 6 ✈️😭 |
| `reels/lauren_02_lost_all_the_cocaine.mp4` | 19:25 to 20:22 | 56s | She Crashed The Plane With All The Cocaine On It | She lost ALL the cocaine in one landing 💀 |
| `reels/lauren_03_massive_explosion.mp4` | 22:58 to 23:41 | 43s | She Died, Respawned, Then Saw A Plane Explode | What was that MASSIVE explosion?! 💥 |
| `reels/lauren_04_swamp_sightseeing.mp4` | 24:04 to 24:51 | 47s | She Bogged Her Car In The GTA 6 Swamps | Never seen a plane crash... drives into a swamp 🐊 |
| `reels/lauren_05_is_it_a_bear.mp4` | 24:57 to 25:55 | 58s | Something Was Growling At Her In GTA 6... | Something is growling at her... is it a BEAR? 🐻 |
| `reels/lauren_06_we_have_cocaine.mp4` | 25:54 to 26:51 | 57s | She Found The Cocaine But Lost Her Car | We have cocaine. We have cocaine. We have... 😂 |
| `reels/lauren_07_longest_getaway_car.mp4` | 27:20 to 28:15 | 55s | She Stole The Longest Getaway Car In GTA 6 | The longest getaway car in GTA history 🚛😂 |
| `reels/lauren_08_police_wont_suspect_truck.mp4` | 28:15 to 28:55 | 40s | Her Genius Plan To Hide From The GTA 6 Cops | Police will never suspect the truck. Trust. 🤫 |
| `reels/lauren_09_truck_road_rage.mp4` | 30:36 to 31:18 | 42s | Lauren's GTA 6 Road Rage In A Giant Truck | These cars have SOME nerve beeping at my truck 😤 |

Campaign rules these clips follow:
- Layout: her facecam on top, the gameplay below. The stream's "UNHOOK" overlay logo is cropped out, and there are no tool watermarks.
- Every caption has `#LaurenHamden` and tags `@LaurenHamden`. Swear words in the burned captions are censored (f\*ck, b\*tch).
- Moments were picked to be funny or memorable and to show her in a good light.
- Before posting: use a Lauren Hamden-themed account with https://lozzahamden.click/ in the bio.

## shorts/ : GTA 6 top-streamer clips (YouTube Shorts, Reels, TikTok)

| File | Source time | Length | Title | On-screen hook |
|---|---|---|---|---|
| `shorts/gta6_01_wynwood_1to1_miami.mp4` | 9:02 to 9:34 | 32s | GTA 6 Recreated Miami's Wynwood 1:1 | GTA 6 copied this real Miami street 1:1 🤯 |
| `shorts/gta6_02_fly_this_low.mp4` | 9:54 to 10:49 | 55s | GTA 6 Makes You Fly THIS Low To Drop The Package | You have to fly THIS low in GTA 6 ✈️😳 |
| `shorts/gta6_03_aviation_major_landing.mp4` | 11:11 to 11:55 | 44s | He Said He Majored In Aviation... Then Landed This | 'I majored in aviation' ...watch him land this 🛬 |
| `shorts/gta6_04_first_time_thats_a_cliff.mp4` | 12:07 to 12:31 | 23s | His First 20 Seconds In GTA 6 | First time playing GTA 6... THAT'S A CLIFF 😱 |
| `shorts/gta6_05_switch_to_lucia_mid_heist.mp4` | 12:44 to 13:16 | 32s | GTA 6 Lets You Switch Characters Mid-Heist | You can switch to Lucia MID-HEIST 👀 |
| `shorts/gta6_06_biker_saloon_went_quiet.mp4` | 13:37 to 14:27 | 50s | They Walked Into A GTA 6 Biker Saloon To Rob It | The entire saloon went quiet... 🤫 |
| `shorts/gta6_07_blew_the_safe_16k.mp4` | 14:27 to 15:10 | 43s | They Blew Open A Safe In GTA 6 For $16,000 | They blew the safe open... $16,000 💥 |

Layout: the gameplay on top, the creators' facecams below.

## How these were made

1. Downloaded both sources with yt-dlp (1080p60) and cut out the second quarter.
2. Ran **OpenShorts** (`mutonby/openshorts`, `main.py`) on each segment. It transcribed with faster-whisper (word timestamps), built its scoring windows, and ran its two LLM passes (score every window, then pick 15-60s clips with a hook, a title and descriptions). OpenShorts normally sends those passes to Gemini or another OpenAI-compatible LLM. Here `pipeline/llm_bridge.py` stood in as that endpoint, and Claude answered OpenShorts' own prompts. The picks are in `pipeline/clips_*.json`.
3. OpenShorts' default reframe didn't work for these sources. Without a Gemini key its layout picker can't run, so it fell back to a plain crop that cut off most of the gameplay and kept the stream logo. So `pipeline/polish.py` builds a stacked facecam/gameplay layout with ffmpeg, then calls OpenShorts' own `auto_caption_clip` and `auto_hook_clip` to burn the captions and hook. `pipeline/fixes.json` fixes transcription typos (mangroves, Wynwood, side missions...) and censors swear words.
4. Final pass: 30 fps, -14 LUFS loudnorm, faststart.
