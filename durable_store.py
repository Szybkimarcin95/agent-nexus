"""SZY-8 JSON durable store with deterministic budgets and idempotency."""
import json, os, re, tempfile, time
from pathlib import Path
from dataclasses import dataclass, asdict
class BudgetExceeded(RuntimeError): pass
class IdempotencyConflict(RuntimeError): pass
@dataclass
class Budget:
    max_tool_calls: int = 20
    max_tokens: int = 10000
    max_runtime_seconds: float = 300.0
@dataclass
class Usage:
    tool_calls: int = 0
    tokens: int = 0
    started_at: float = 0.0
class DurableStore:
    def __init__(self, root):
        self.root=Path(root); self.root.mkdir(parents=True, exist_ok=True)
        self.runs=self.root/"runs"; self.runs.mkdir(exist_ok=True)
        self.effects=self.root/"idempotency.json"
    def _atomic(self,path,data):
        fd,tmp=tempfile.mkstemp(prefix=".tmp-",dir=path.parent)
        try:
            with os.fdopen(fd,"w",encoding="utf-8") as f:
                json.dump(data,f,indent=2,sort_keys=True); f.flush(); os.fsync(f.fileno())
            os.replace(tmp,path)
        finally:
            if os.path.exists(tmp): os.unlink(tmp)
    def create_run(self,run_id,budget=None,state=None):
        if not re.fullmatch(r"RUN-[A-Za-z0-9-]+",run_id): raise ValueError("invalid run ID")
        p=self.runs/(run_id+".json")
        if p.exists(): raise FileExistsError(run_id)
        now=time.time(); b=budget or Budget()
        doc={"run_id":run_id,"status":"running","budget":asdict(b),"usage":asdict(Usage(started_at=now)),"state":state,"created_at":now,"updated_at":now}
        self._atomic(p,doc); return doc
    def load_run(self,run_id):
        p=self.runs/(run_id+".json")
        if not p.exists(): raise FileNotFoundError(run_id)
        return json.loads(p.read_text())
    def save_run(self,doc):
        doc["updated_at"]=time.time(); self._atomic(self.runs/(doc["run_id"]+".json"),doc)
    def consume(self,run_id,tool_calls=0,tokens=0,now=None):
        doc=self.load_run(run_id); u=doc["usage"]; b=doc["budget"]; now=now or time.time()
        u["tool_calls"]+=tool_calls; u["tokens"]+=tokens; elapsed=now-u["started_at"]
        reason=("max_tool_calls" if u["tool_calls"]>b["max_tool_calls"] else "max_tokens" if u["tokens"]>b["max_tokens"] else "max_runtime_seconds" if elapsed>b["max_runtime_seconds"] else None)
        if reason:
            doc["status"]="budget_exceeded"; doc["budget_reason"]=reason; self.save_run(doc); raise BudgetExceeded(reason)
        self.save_run(doc); return doc
    def record_effect(self,key,result):
        data=json.loads(self.effects.read_text()) if self.effects.exists() else {}
        if key in data:
            if data[key]!=result: raise IdempotencyConflict(key)
            return data[key]
        data[key]=result; self._atomic(self.effects,data); return result
    def has_effect(self,key):
        return self.effects.exists() and key in json.loads(self.effects.read_text())
