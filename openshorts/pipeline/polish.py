"""Re-burn OpenShorts hook + captions on the clean reframed clip with a corrected
transcript, after optional delogo; then loudness-normalize.
usage: polish.py <openshorts_dir> <out_dir> <stem> <clip_no> <final_path> <source_video> <layout: twitch|track>"""
import sys, os, json, copy, re, shutil, subprocess
osdir, out, stem, n, final = sys.argv[1:6]
source, layout = sys.argv[6], sys.argv[7]
sys.path.insert(0, osdir); os.chdir(osdir)
os.environ.setdefault("AUTO_HOOK", "1"); os.environ["AUTO_HOOK_SECONDS"] = "3"; os.environ["WATERMARK"] = "0"
import main, layout_ranges
n = int(n)
meta = json.load(open(f"{out}/{stem}_metadata.json"))
clip = copy.deepcopy(meta["shorts"][n-1])
tr = copy.deepcopy(meta["transcript"])
FIX = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "fixes.json")))
PAIR = {tuple(k.lower().split("|")): v for k, v in FIX["pairs"].items()}
ONE = {k.lower(): v for k, v in FIX["words"].items()}
def norm(w): return re.sub(r"[^\w']", "", w.lower())
for seg in tr["segments"]:
    ws = seg.get("words", []); i = 0; new = []
    while i < len(ws):
        w = ws[i]
        if i + 1 < len(ws) and (norm(w["word"]), norm(ws[i+1]["word"])) in PAIR:
            w2 = ws[i+1]; rep = PAIR[(norm(w["word"]), norm(w2["word"]))]
            trail = re.sub(r"^.*?([.,!?]*)$", r"\1", w2["word"].strip())
            new.append({**w, "word": " " + rep + trail, "end": w2["end"]}); i += 2; continue
        k = norm(w["word"])
        if k in ONE:
            trail = re.sub(r"^.*?([.,!?]*)$", r"\1", w["word"].strip())
            w = {**w, "word": " " + ONE[k] + trail}
        new.append(w); i += 1
    seg["words"] = new
    seg["text"] = "".join(x["word"] for x in new)
src = f"{out}/{stem}_clip_{n}.mp4"
work = f"{out}/polish_{n}"; os.makedirs(work, exist_ok=True)
clean = f"{work}/{stem}_clip_{n}.mp4"
dur = clip["end"] - clip["start"]
if layout == "yt":
    # edited creator video: gameplay centre on top, the creators' facecams (bottom-left inset) below
    vf = ("[0:v]split[a][b];[a]crop=928:1080:680:0,scale=1080:1256:flags=lanczos[top];"
          "[b]crop=700:430:0:650,scale=1080:664:flags=lanczos[bot];[top][bot]vstack=2,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(clip["start"]), "-i", source, "-t", f"{dur:.3f}",
                    "-filter_complex", vf, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "17",
                    "-preset", "medium", "-c:a", "aac", "-b:a", "192k", clean], check=True)
    json.dump({"ranges": [{"start": 0.0, "end": round(dur, 3), "layout": "split"}]}, open(clean + ".layout.json", "w"))
elif layout == "twitch":
    # streamer layout: facecam (fixed inset, top-right of the stream) on top, gameplay below
    vf = ("[0:v]split[a][b];[a]crop=536:417:1348:0,scale=1080:840:flags=lanczos[top];"
          "[b]crop=1000:1000:340:40,scale=1080:1080:flags=lanczos[bot];[top][bot]vstack=2,format=yuv420p[v]")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(clip["start"]), "-i", source, "-t", f"{dur:.3f}",
                    "-filter_complex", vf, "-map", "[v]", "-map", "0:a", "-c:v", "libx264", "-crf", "17",
                    "-preset", "medium", "-c:a", "aac", "-b:a", "192k", clean], check=True)
    json.dump({"ranges": [{"start": 0.0, "end": round(dur, 3), "layout": "split"}]}, open(clean + ".layout.json", "w"))
else:
    shutil.copy(src, clean)
    if os.path.exists(src + ".layout.json"): shutil.copy(src + ".layout.json", clean + ".layout.json")
split = layout_ranges.split_ranges(layout_ranges.read(clean))
plan = main.auto_caption_clip(clean, tr, clip["start"], clip["end"], split_ranges=split, plan_only=True)
hooked = main.auto_hook_clip(clean, clip, captions=plan)
res = hooked[1].pop("_captioned", None) if hooked else None
if not res: sys.exit("burn failed")
subprocess.run(["ffmpeg", "-v", "error", "-y", "-i", res, "-c:v", "copy",
                "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                "-movflags", "+faststart", final], check=True)
print("OK", final)
