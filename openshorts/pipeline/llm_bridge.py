# OpenAI-compatible bridge: saves each prompt to disk and waits for a human/agent-written answer file.
import json, os, time, itertools, sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
D = sys.argv[1]; ctr = itertools.count(1)
class H(BaseHTTPRequestHandler):
    def do_POST(self):
        body = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if body.get("response_format", {}).get("type") == "json_schema":
            self.send_response(400); self.end_headers(); self.wfile.write(b'{"error":"response_format json_schema unsupported"}'); return
        n = next(ctr); req = f"{D}/req_{n}.txt"; ans = f"{D}/ans_{n}.json"
        open(req, "w").write(body["messages"][-1]["content"])
        while not os.path.exists(ans): time.sleep(2)
        time.sleep(1); txt = open(ans).read()
        out = json.dumps({"choices":[{"message":{"role":"assistant","content":txt}}],"usage":{}}).encode()
        self.send_response(200); self.send_header("Content-Type","application/json"); self.end_headers(); self.wfile.write(out)
    def log_message(self, *a): pass
ThreadingHTTPServer(("127.0.0.1", 8765), H).serve_forever()
