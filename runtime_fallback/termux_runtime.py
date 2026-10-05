import time,uuid
from .local_router import route
from .mini_graph import MiniGraph
from capability import decide,Decision
from invariants import check_inv007_untrusted_content_cannot_expand_permissions,InvariantViolation
from write_gate import is_write_locked
from eventlog import EventLog
class TermuxRuntime:
 def __init__(self,base,role="GraphResearcher"):
  self.base=base; self.role=role; base.mkdir(parents=True,exist_ok=True); self.graph=MiniGraph(base/"mini.sqlite"); self.log=EventLog(base/"events.jsonl")
 def handle(self,task):
  run_id="T-"+uuid.uuid4().hex[:10]; trace_id=uuid.uuid4().hex
  try: check_inv007_untrusted_content_cannot_expand_permissions(task)
  except InvariantViolation:
   self.log.append({"run_id":run_id,"trace_id":trace_id,"event":"input-blocked"}); return {"status":"blocked","run_id":run_id,"trace_id":trace_id}
  tool,payload=route(task); d=decide(self.role,tool)
  if d==Decision.DISALLOW:return {"status":"capability-denied","run_id":run_id,"tool":tool}
  if d==Decision.NEEDS_APPROVAL:return {"status":"approval-required","run_id":run_id,"pending_tool":tool,"locked":is_write_locked()}
  if tool=="neo4j.schema": result=self.graph.get_schema()
  elif tool=="neo4j.read": result=self.graph.read_nodes_top_degree() if "top 10" in task.lower() else self.graph.read_nodes()
  else: result={"locally":"unavailable"}
  self.log.append({"run_id":run_id,"trace_id":trace_id,"event":"read-complete","tool":tool})
  return {"status":"done","run_id":run_id,"tool":tool,"result":result}
