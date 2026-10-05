import json,time
class EventLog:
 def __init__(self,path): self.path=path
 def append(self,event):
  row=dict(event,ts=time.time()); self.path.parent.mkdir(parents=True,exist_ok=True); self.path.open("a",encoding="utf-8").write(json.dumps(row,sort_keys=True)+"\n"); return row
 def read(self): return [json.loads(x) for x in self.path.read_text().splitlines() if x.strip()] if self.path.exists() else []
