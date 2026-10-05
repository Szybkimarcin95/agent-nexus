import json
from observability.span_integrity import scan
def test_missing_file(tmp_path):
 r=scan(tmp_path/"none"); assert not r["ok"]
def test_clean_file(tmp_path):
 p=tmp_path/"x"; p.write_text(json.dumps({"trace_id":"T","run_id":"R","event":"x"})+"\n"); r=scan(p); assert r["ok"] and r["checked"]==1
def test_missing_trace(tmp_path):
 p=tmp_path/"x"; p.write_text(json.dumps({"run_id":"R"})+"\n"); assert not scan(p)["ok"]
def test_duplicate_idem(tmp_path):
 p=tmp_path/"x"; x=json.dumps({"trace_id":"T","run_id":"R","payload":{"idem":"K"}})+"\n"; p.write_text(x+x); assert not scan(p)["ok"]
def test_malformed(tmp_path):
 p=tmp_path/"x"; p.write_text("bad\n"); r=scan(p); assert not r["ok"] and r["malformed_lines"]==1
