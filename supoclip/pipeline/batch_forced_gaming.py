"""Like batch.py, but locks SupoClip's gaming layout to the facecam/HUD boxes found on a reference gameplay
segment, so cutscenes keep the streamer's facecam panel. Usage: batch_forced_gaming.py REF.mp4 <batch.py args>"""
import sys, runpy
sys.path.insert(0, "/home/user/tools/supoclip/backend")
from pathlib import Path
import src.media.gaming_layout as gl
ref = Path(sys.argv.pop(1))
import subprocess, json
w, h, d = 1920, 1080, 30.0
profiles = [p for p in gl.analyze_gaming_clip(ref, w, h, d) if p.is_gaming]
assert profiles, "reference segment not detected as gaming"
print("reference profile:", profiles[0].summary(), flush=True)
import os
if os.environ.get("NO_HUD"): profiles[0].hud = []
gl.analyze_gaming_clip = lambda path, width, height, duration: [profiles[0]]
sys.argv[0] = "/home/user/work/scripts/batch.py"
runpy.run_path("/home/user/work/scripts/batch.py", run_name="__main__")
