"""Finish a clip: 9:16 layout, word-by-word captions, hook title, loudness-normalised audio."""
import json, sys, subprocess, re, os

CENSOR = {r"\bfuck": "f*ck", r"\bshit": "sh*t", r"\bbitch": "b*tch"}

def censor(w):
    for k, v in CENSOR.items():
        w = re.sub(k, v, w, flags=re.I)
    return w

def ts(t):
    t = max(0, t); h = int(t // 3600); m = int(t % 3600 // 60); s = t % 60
    return f"{h}:{m:02d}:{s:05.2f}"

def build_ass(words, start, end, hook, out, cap_y, hook_y, W=1080, H=1920):
    hdr = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 0

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,Inter Black,84,&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,7,3,5,60,60,0
Style: Hook,Inter Black,70,&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,3,18,0,5,110,110,0

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    ev = []
    # hook title box for first 3s
    if hook:
        ev.append(f"Dialogue: 2,{ts(0)},{ts(3.0)},Hook,,0,0,0,,{{\\pos({W//2},{hook_y})\\3c&H000000&\\1c&HFFFFFF&\\fad(0,250)}}{hook.upper()}")
    # word-by-word: group words into chunks of <=3 words, highlight active word
    ws = [w for w in words if w["e"] > start and w["s"] < end]
    chunks, cur = [], []
    for w in ws:
        if cur and w["s"] - cur[-1]["e"] > 0.6:
            chunks.append(cur); cur = []
        cur.append(w)
        txt = w["w"].strip()
        if len(cur) >= 3 or txt.endswith((".", "?", "!", ",")):
            chunks.append(cur); cur = []
    if cur: chunks.append(cur)
    for ci, ch in enumerate(chunks):
        nxt = chunks[ci + 1][0]["s"] if ci + 1 < len(chunks) else ch[-1]["e"] + 0.4
        for wi, w in enumerate(ch):
            s = w["s"] - start
            e = (ch[wi + 1]["s"] if wi + 1 < len(ch) else min(nxt, ch[-1]["e"] + 0.5)) - start
            if e <= s: e = s + 0.08
            parts = []
            for wj, w2 in enumerate(ch):
                t = censor(w2["w"].strip().upper().strip(",."))
                if wj == wi:
                    parts.append(f"{{\\1c&H00E5FF&\\fscx108\\fscy108}}{t}{{\\1c&HFFFFFF&\\fscx100\\fscy100}}")
                else:
                    parts.append(t)
            pop = "\\t(0,80,\\fscx104\\fscy104)" if wi == 0 else ""
            ev.append(f"Dialogue: 1,{ts(s)},{ts(e)},Cap,,0,0,0,,{{\\pos({W//2},{cap_y}){pop}}}" + " ".join(parts))
    open(out, "w").write(hdr + "\n".join(ev) + "\n")

def render(src, words, clip, out, layout):
    st, en = clip["start"], clip["end"]
    fx = {round(t, 1): v for t, v in clip.get("fix", [])}
    nw = []
    for w in words:
        k = round(w["s"], 1)
        if k in fx:
            if fx[k] == "": continue
            w = dict(w, w=fx[k])
        if nw and w["w"].strip().startswith("-"):
            nw[-1] = dict(nw[-1], w=nw[-1]["w"].rstrip() + w["w"].strip(), e=w["e"]); continue
        nw.append(w)
    words = nw
    ass = out.replace(".mp4", ".ass")
    if layout == "stream":
        # facecam (top) + gameplay (bottom)
        cap_y, hook_y = 1180, 840
        vf = ("[0:v]split=2[a][b];"
              "[a]crop=540:405:1346:12,scale=1080:810:flags=lanczos[cam];"
              "[b]crop=1051:1080:230:0,scale=1080:1110:flags=lanczos[game];"
              f"[cam][game]vstack=inputs=2,setsar=1,ass={ass}[v]")
    else:
        # full gameplay: blurred fill + centred 16:9 enlarged crop
        cap_y, hook_y = 1530, 400
        vf = ("[0:v]split=2[a][b];"
              "[a]scale=-2:1920,crop=1080:1920,boxblur=30:3,eq=brightness=-0.2[bg];"
              "[b]crop=1320:1080:0:0,scale=1080:884:flags=lanczos[fg];"
              f"[bg][fg]overlay=0:518,setsar=1,ass={ass}[v]")
    build_ass(words, st, en, clip.get("hook", ""), ass, cap_y, hook_y)
    cmd = ["ffmpeg", "-v", "error", "-y", "-ss", f"{st}", "-t", f"{en-st}", "-i", src,
           "-filter_complex", vf, "-map", "[v]", "-map", "0:a",
           "-af", "loudnorm=I=-14:TP=-1.5:LRA=11,afade=t=out:st=%.2f:d=0.3" % (en - st - 0.3),
           "-r", "30", "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-profile:v", "high",
           "-pix_fmt", "yuv420p", "-c:a", "aac", "-b:a", "192k", "-ar", "48000",
           "-movflags", "+faststart", out]
    subprocess.run(cmd, check=True)
    os.remove(ass)

if __name__ == "__main__":
    src, wordsjson, clipsjson, outdir, layout = sys.argv[1:6]
    segs = json.load(open(wordsjson))
    words = [w for s in segs for w in s["words"]]
    os.makedirs(outdir, exist_ok=True)
    for c in json.load(open(clipsjson)):
        out = os.path.join(outdir, c["id"] + ".mp4")
        print("render", c["id"], c["start"], c["end"], flush=True)
        render(src, words, c, out, layout)
        with open(os.path.join(outdir, c["id"] + ".txt"), "w") as f:
            f.write(c["caption"].strip() + "\n")
