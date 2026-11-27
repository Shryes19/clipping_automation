import sys, json
from faster_whisper import WhisperModel
wav, out = sys.argv[1], sys.argv[2]
m = WhisperModel("small.en", device="cpu", compute_type="int8", cpu_threads=4)
import wave, numpy as np
wf=wave.open(wav); audio=np.frombuffer(wf.readframes(wf.getnframes()),dtype=np.int16).astype(np.float32)/32768.0
segs, info = m.transcribe(audio, word_timestamps=True, vad_filter=True, beam_size=5)
res=[]
for s in segs:
    res.append({"start":s.start,"end":s.end,"text":s.text.strip(),"words":[{"s":w.start,"e":w.end,"w":w.word} for w in s.words]})
    print(f"{s.start:.1f} {s.text}", flush=True)
json.dump(res, open(out,"w"))
def ts(t):
    h=int(t//3600); m_=int(t%3600//60); s_=t%60
    return f"{h:02d}:{m_:02d}:{s_:06.3f}".replace(".",",")
with open(out.replace(".json",".srt"),"w") as f:
    for i,s in enumerate(res,1):
        f.write(f"{i}\n{ts(s['start'])} --> {ts(s['end'])}\n{s['text']}\n\n")
