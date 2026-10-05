from __future__ import annotations
import argparse,json,sys
from collections import Counter
from pathlib import Path
def scan(path:Path):
    problems=[]; checked=0; seen=Counter(); events=Counter(); runs=set(); traces=set(); malformed=0
    if not path.exists(): return {"ok":False,"error":f"file not found: {path}","checked":0,"problems":1,"issues":[f"file not found: {path}"]}
    for no,line in enumerate(path.read_text(encoding="utf-8",errors="replace").splitlines(),1):
        if not line.strip(): continue
        checked+=1
        try:e=json.loads(line)
        except json.JSONDecodeError:
            malformed+=1; problems.append(f"line-{no}: malformed JSON"); continue
        if not e.get("trace_id"): problems.append(f"line-{no}: missing trace_id")
        if not e.get("run_id"): problems.append(f"line-{no}: missing run_id")
        p=e.get("payload"); idem=p.get("idem") if isinstance(p,dict) else None
        if idem: seen[idem]+=1
        events[e.get("event") or e.get("name") or "?"]+=1
        if e.get("run_id"): runs.add(e["run_id"])
        if e.get("trace_id"): traces.add(e["trace_id"])
    for k,n in seen.items():
        if n>1: problems.append(f"duplicate-idem-key:{k}(x{n})")
    return {"ok":not problems,"file":str(path),"checked":checked,"malformed_lines":malformed,"problems":len(problems),"issues":problems[:100],"events":dict(events.most_common(12)),"distinct_runs":len(runs),"distinct_traces":len(traces)}
if __name__=="__main__":
    ap=argparse.ArgumentParser(); ap.add_argument("--path",required=True); r=scan(Path(ap.parse_args().path)); print(json.dumps(r,indent=2,ensure_ascii=False)); sys.exit(0 if r["ok"] and not r["malformed_lines"] else 1)
