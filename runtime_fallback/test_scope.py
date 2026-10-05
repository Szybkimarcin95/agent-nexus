import hashlib,json,uuid
from .mini_graph import MiniGraph
from capability import CAPABILITIES,APPROVAL_REQUIRED
from invariants import check_inv002_no_gated_without_record,check_inv003_no_tool_outside_capability,check_inv004_every_side_effect_has_idempotency_key,check_inv007_untrusted_content_cannot_expand_permissions
def test_idem(run,tool,payload): return "test:"+run+":"+tool+":"+hashlib.sha256(json.dumps(payload,sort_keys=True).encode()).hexdigest()[:12]
def gate_write_test(role,tool,payload,run,records):
 check_inv003_no_tool_outside_capability(role,tool); check_inv002_no_gated_without_record(tool,records); check_inv007_untrusted_content_cannot_expand_permissions(json.dumps(payload)); key=test_idem(run,tool,payload); check_inv004_every_side_effect_has_idempotency_key(tool,key); return {"authorized":True,"scope":"test","idempotency_key":key,"canonical_tool":CAPABILITIES[tool].canonical_name}
class TestScopeRuntime:
 def __init__(self,base,role="Supervisor"): self.base=base/"test_scope"; self.base.mkdir(parents=True,exist_ok=True); self.role=role
 def exercise(self,run_id=None):
  run=run_id or "test-"+uuid.uuid4().hex[:8]; g=MiniGraph(self.base/(run+".sqlite")); rec=[{"tool":"neo4j.write","decision":"approved"}]; results=[]
  for props in [{"tag":"alpha"},{"tag":"beta"},{"tag":"alpha"}]:
   gate=gate_write_test(self.role,"neo4j.write",props,run,rec); out=g.write_node("testwrite",props,gate["idempotency_key"]); results.append(out)
  return {"run_id":run,"results":results,"replays":sum(x.get("idempotent_replay",False) for x in results)}
 def verify_no_production_leak(self,prod):
  if not prod.exists(): return {"leak":False,"prod_count":0}
  g=MiniGraph(prod); nodes=g.read_nodes(); leak=sum(n["label"]=="testwrite" for n in nodes); return {"leak":leak>0,"leaked_test_nodes":leak,"prod_count":len(nodes)}
