"""Render a list of clips with SupoClip's renderer, trimming dead air via keep_ranges built from word timestamps."""
import sys, json, logging
from pathlib import Path
sys.path.insert(0, "/home/user/tools/supoclip/backend")
logging.basicConfig(level=logging.WARNING)
from src.video_utils import create_optimized_clip
video = Path(sys.argv[1]); words = json.load(open(sys.argv[2])); spec = json.load(open(sys.argv[3])); outdir = Path(sys.argv[4])
only = sys.argv[5].split(",") if len(sys.argv) > 5 else None
W = [w for s in words for w in s["words"]]
for c in spec:
    if only and c["id"] not in only: continue
    s, e = c["start"], c["end"]; excl = c.get("exclude", [])
    ws = [w for w in W if w["start"] >= s - 0.1 and w["end"] <= e + 0.3 and not any(a <= w["start"] < b for a, b in excl)]
    ranges = []
    for w in ws:
        a, b = max(s, w["start"] - 0.25), min(e, w["end"] + 0.35)
        if ranges and a - ranges[-1][1] < c.get("max_gap", 2.0): ranges[-1][1] = max(ranges[-1][1], b)
        else: ranges.append([a, b])
    ranges[0][0] = s if ranges[0][0] - s < 1.5 else ranges[0][0]
    out = outdir / f"{c['id']}_raw.mp4"
    rep = {}
    ok = create_optimized_clip(video, s, e, out, add_subtitles=True, caption_template=c.get("template", "hormozi"),
        output_format="vertical", keep_ranges=[tuple(r) for r in ranges], hook_title=c["hook"], extend_to_sentence=False, layout_report=rep)
    print(c["id"], "OK" if ok else "FAIL", round(sum(b - a for a, b in ranges), 1), "s kept", rep.get("vertical_layout", {}).get("kind"), flush=True)
