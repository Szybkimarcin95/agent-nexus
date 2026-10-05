import json
from http.server import BaseHTTPRequestHandler,HTTPServer
def load(path):
 return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []
def make_handler(path):
 class H(BaseHTTPRequestHandler):
  def do_GET(self):
   spans=load(path)
   if self.path=="/spans.json": body=json.dumps(spans).encode()
   elif self.path=="/stats.json": body=json.dumps({"count":len(spans),"runs":len({x.get("run_id") for x in spans})}).encode()
   elif self.path=="/integrity.json": body=json.dumps({"ok":all(x.get("run_id") and x.get("trace_id") for x in spans),"count":len(spans)}).encode()
   else: body=b"<html><body><h1>Agent Nexus Span Viewer</h1><p>Use /spans.json, /stats.json or /integrity.json</p></body></html>"
   self.send_response(200); self.send_header("Content-Type","application/json" if self.path.endswith(".json") else "text/html"); self.end_headers(); self.wfile.write(body)
  def log_message(self,*a): pass
 return H
def serve(path,port=5150): HTTPServer(("127.0.0.1",port),make_handler(path)).serve_forever()
