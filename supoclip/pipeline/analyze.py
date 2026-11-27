"""Run SupoClip's transcript formatting, caching and AI clip analysis on a pre-transcribed file."""
import sys, json, asyncio, os
from pathlib import Path
sys.path.insert(0, "/home/user/tools/supoclip/backend")
from src.media.transcription import format_transcript_for_analysis, cache_transcript_data
import src.ai as ai, httpx
_OP = ai.OllamaProvider
def _LongOllama(*a, **k):
    k.setdefault("http_client", httpx.AsyncClient(timeout=httpx.Timeout(3600.0, connect=30.0)))
    return _OP(*a, **k)
ai.OllamaProvider = _LongOllama
ai.TRANSCRIPT_ANALYSIS_TIMEOUT_SECONDS = 3000; ai.ANALYSIS_TOTAL_TIMEOUT_SECONDS = 6000; ai.RERANK_TIMEOUT_SECONDS = 1500
from src.ai import get_most_relevant_parts_by_transcript

video = Path(sys.argv[1]); words_json = sys.argv[2]; out = sys.argv[3]
instructions = sys.argv[4] if len(sys.argv) > 4 else None
segs = json.load(open(words_json))
result = {"text": " ".join(s["text"].strip() for s in segs), "language": "en",
          "segments": [{"start": s["start"], "end": s["end"], "text": s["text"],
                        "words": [{"word": w["word"], "start": float(w["start"]), "end": float(w["end"]), "probability": 1.0} for w in s["words"]]} for s in segs]}
cache_transcript_data(video, result)
transcript = "\n".join(format_transcript_for_analysis(result))
Path(out).with_suffix(".transcript.txt").write_text(transcript)
dur = segs[-1]["end"]
analysis = asyncio.run(get_most_relevant_parts_by_transcript(transcript, instructions=instructions, source_duration=dur))
json.dump(analysis.model_dump(), open(out, "w"), indent=2)
for s in analysis.most_relevant_segments:
    print(s.start_time, s.end_time, s.relevance_score, s.hook_title, "|", s.text[:120])
