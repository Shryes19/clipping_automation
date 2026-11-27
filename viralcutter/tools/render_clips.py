"""Render ViralCutter-selected segments as stacked 9:16 shorts with word-timed captions.

Usage: python render_clips.py <project_dir> <out_dir> <layout> [offset_seconds]
layout: "facecam" (Lauren Twitch layout: facecam top-right stacked over gameplay) or "center" (center crop).
"""
import json, os, re, subprocess, sys

import torch
# Same compatibility patch ViralCutter applies: whisperx's bundled pyannote VAD checkpoint predates weights_only loading.
_orig_load = torch.load
def _load(*a, **k):
    k['weights_only'] = False
    return _orig_load(*a, **k)
torch.load = _load
import whisperx

proj, out_dir, layout = sys.argv[1], sys.argv[2], sys.argv[3]
offset = float(sys.argv[4]) if len(sys.argv) > 4 else 0.0
os.makedirs(out_dir, exist_ok=True)
work = os.path.join(proj, "render_tmp")
os.makedirs(work, exist_ok=True)
src = os.path.join(proj, "input.mp4")
segs = json.load(open(os.path.join(proj, "viral_segments.txt")))["segments"]
only = os.environ.get("ONLY")

CENSOR = {"fucking": "f***ing", "fuck": "f***", "shit": "sh*t", "bitch": "b*tch", "dick": "d*ck"}

def censor(w):
    core = re.sub(r"[^\w']", "", w).lower()
    return CENSOR.get(core, w) if core in CENSOR else w

def ts(t):
    t = max(t, 0)
    h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def slug(s):
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]

device = "cpu"
model = whisperx.load_model("large-v3-turbo", device, compute_type="int8", language="en")
align_model, meta = whisperx.load_align_model(language_code="en", device=device)

HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,92,&H00FFFFFF,&H00FFFFFF,&H00000000,&H96000000,-1,0,0,0,100,100,0,0,1,7,3,2,110,110,{capv},1
Style: Hook,Inter Black,64,&H00000000,&H00000000,&H00FFFFFF,&H00FFFFFF,-1,0,0,0,100,100,0,0,3,18,0,8,70,70,{hookv},1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""

for i, seg in enumerate(segs):
    title = seg["title"]
    if only and slug(title) not in only.split(","):
        continue
    st, en = seg["start_time"] - 0.15, seg["end_time"] + 0.6
    dur = en - st
    name = f"{i+1:02d}_{slug(title)}"
    wav = os.path.join(work, name + ".wav")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{st:.3f}", "-t", f"{dur:.3f}", "-i", src,
                    "-vn", "-ac", "1", "-ar", "16000", wav], check=True)
    audio = whisperx.load_audio(wav)
    res = model.transcribe(audio, batch_size=8, language="en")
    al = whisperx.align(res["segments"], align_model, meta, audio, device, return_char_alignments=False)
    words = [w for s in al["segments"] for w in s.get("words", []) if "start" in w]

    # Dead-air removal: keep speech, squeeze gaps > 1.2s down to ~0.5s
    def build(gap, pre, post):
        rs = []
        for w in words:
            a, b = max(w["start"] - pre, 0), min(w["end"] + post, dur)
            if rs and a - rs[-1][1] < gap:
                rs[-1][1] = max(rs[-1][1], b)
            else:
                rs.append([a, b])
        if not rs:
            rs = [[0, dur]]
        rs[0][0] = max(rs[0][0], 0)
        rs[-1][1] = min(rs[-1][1] + 0.4, dur)
        return rs
    for gap, pre, post in [(1.5, 0.3, 0.6), (3.0, 0.5, 1.0), (1e9, 0.3, 0.6)]:
        ranges = build(gap, pre, post)
        if sum(b - a for a, b in ranges) >= 15:
            break
    def remap(t):
        acc = 0.0
        for a, b in ranges:
            if t < a:
                return acc
            if t <= b:
                return acc + t - a
            acc += b - a
        return acc
    for w in words:
        w["start"], w["end"] = remap(w["start"]), remap(w["end"])
    new_dur = sum(b - a for a, b in ranges)

    # group into 1-3 word chunks, break on punctuation or gaps
    chunks, cur = [], []
    for w in words:
        if cur and (len(cur) >= 3 or w["start"] - cur[-1]["end"] > 0.6 or re.search(r"[.?!,]$", cur[-1]["word"])):
            chunks.append(cur); cur = []
        cur.append(w)
    if cur:
        chunks.append(cur)

    capv = {"facecam": 600, "camleft": 560}.get(layout, 470)
    hookv = {"facecam": 880, "camleft": 690}.get(layout, 520)
    lines = [HEADER.format(capv=capv, hookv=hookv)]
    hook = title.upper()
    lines.append(f"Dialogue: 1,{ts(0)},{ts(2.8)},Hook,,0,0,0,,{{\\fad(0,200)}}{hook}")
    for ci, c in enumerate(chunks):
        c_end = c[-1]["end"] + 0.12
        if ci + 1 < len(chunks):
            c_end = min(c_end, chunks[ci + 1][0]["start"])
        for k, w in enumerate(c):
            w_end = c[k + 1]["start"] if k + 1 < len(c) else c_end
            w_end = min(max(w_end, w["start"] + 0.05), c_end) if k + 1 == len(c) else w_end
            txt = []
            for j, x in enumerate(c):
                word = censor(x["word"]).upper()
                if j == k:
                    txt.append("{\\c&H00E5FF&\\fscx108\\fscy108}" + word + "{\\c&HFFFFFF&\\fscx100\\fscy100}")
                else:
                    txt.append(word)
            pop = "{\\t(0,80,\\fscx104\\fscy104)}" if k == 0 else ""
            lines.append(f"Dialogue: 0,{ts(w['start'])},{ts(w_end)},Cap,,0,0,0,,{pop}{' '.join(txt)}")
    ass = os.path.join(work, name + ".ass")
    open(ass, "w").write("\n".join(lines) + "\n")

    n = len(ranges)
    cut = "".join(f"[0:v]trim={a:.3f}:{b:.3f},setpts=PTS-STARTPTS[v{k}];[0:a]atrim={a:.3f}:{b:.3f},asetpts=PTS-STARTPTS[a{k}];" for k, (a, b) in enumerate(ranges))
    cut += "".join(f"[v{k}][a{k}]" for k in range(n)) + f"concat=n={n}:v=1:a=1[cv][ca];[ca]loudnorm=I=-14:TP=-1.5:LRA=11[aout];"
    if layout == "facecam":
        vf = ("[cv]split=2[a][b];"
              "[a]crop=540:420:1346:8,scale=1080:840[top];"
              "[b]crop=1000:1000:335:60,scale=1080:1080[bot];"
              "[top][bot]vstack=2,fps=30,format=yuv420p,"
              f"ass={ass}:fontsdir=/usr/share/fonts[v]")
    elif layout == "camleft":
        vf = ("[cv]split=2[a][b];"
              "[a]crop=780:468:0:612,scale=1080:648[top];"
              "[b]crop=917:1080:760:0,scale=1080:1272[bot];"
              "[top][bot]vstack=2,fps=30,format=yuv420p,"
              f"ass={ass}:fontsdir=/usr/share/fonts[v]")
    else:
        vf = ("[cv]split=2[a][b];"
              "[a]scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,boxblur=30:5,eq=brightness=-0.08[bg];"
              "[b]scale=1080:-2[fg];"
              "[bg][fg]overlay=0:(H-h)/2,fps=30,format=yuv420p,"
              f"ass={ass}:fontsdir=/usr/share/fonts[v]")
    vf = cut + vf
    out = os.path.join(out_dir, name + ".mp4")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{st:.3f}", "-t", f"{dur:.3f}", "-i", src,
                    "-filter_complex", vf, "-map", "[v]", "-map", "[aout]",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
                    "-c:a", "aac", "-b:a", "160k", "-ar", "48000",
                    "-movflags", "+faststart", out], check=True)
    meta_out = {"title": title, "source_start": round(seg["start_time"] + offset, 2),
                "source_end": round(seg["end_time"] + offset, 2), "duration": round(new_dur, 1),
                "transcript": " ".join(w["word"] for w in words)}
    json.dump(meta_out, open(os.path.join(out_dir, name + ".json"), "w"), indent=2)
    print("DONE", name, f"{new_dur:.1f}s", flush=True)
