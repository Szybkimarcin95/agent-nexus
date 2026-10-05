import json,threading,urllib.request
from http.server import HTTPServer
from observability.span_viewer import make_handler
def test_span_endpoints(tmp_path):
 p=tmp_path/"spans.jsonl"; p.write_text(json.dumps({"run_id":"R1","trace_id":"T1","event":"read"})+"\n")
 s=HTTPServer(("127.0.0.1",0),make_handler(p)); threading.Thread(target=s.serve_forever,daemon=True).start(); base=f"http://127.0.0.1:{s.server_port}"
 assert json.loads(urllib.request.urlopen(base+"/spans.json").read())[0]["run_id"]=="R1"
 assert json.loads(urllib.request.urlopen(base+"/stats.json").read())["count"]==1
 assert json.loads(urllib.request.urlopen(base+"/integrity.json").read())["ok"] is True
 s.shutdown()
