import sys, json
from faster_whisper import WhisperModel
m = WhisperModel("medium", device="cpu", compute_type="int8", cpu_threads=4)
import wave, numpy as np
w=wave.open(sys.argv[1]); a=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).astype(np.float32)/32768
segs, info = m.transcribe(a, language="en", word_timestamps=True, vad_filter=True)
out=[]
for s in segs:
    out.append({"start":s.start,"end":s.end,"text":s.text,"words":[{"start":w.start,"end":w.end,"word":w.word} for w in s.words]})
    print(f"[{s.start:.1f}] {s.text}", flush=True)
json.dump(out, open(sys.argv[2],"w"))
