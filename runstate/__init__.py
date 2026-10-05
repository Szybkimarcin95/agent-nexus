import json
class RunStore:
 def __init__(self,root): self.root=root; self.root.mkdir(parents=True,exist_ok=True)
 def save(self,envelope):
  p=self.root/(envelope["run_id"]+".json"); p.write_text(json.dumps(envelope,sort_keys=True)); return p
 def load(self,run_id): return json.loads((self.root/(run_id+".json")).read_text())
