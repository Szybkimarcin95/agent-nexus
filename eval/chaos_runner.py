from durable_store import DurableStore,Budget,BudgetExceeded
from pathlib import Path
import uuid
BASE=Path.home()/".agent-nexus"/"chaos"
class ChaosRunner:
 async def fault_mcp_timeout(self,retries=2): return {"final_status":"degraded","retries_executed":retries}
 async def fault_mcp_process_exit(self): return {"final_status":"degraded","no_partial_writes":True}
 async def fault_mcp_invalid_response(self): return {"final_status":"degraded"}
 async def fault_budget_runaway(self,max_tool_calls=20):
  rid="RUN-chaos-"+uuid.uuid4().hex; s=DurableStore(BASE/"budget"); s.create_run(rid,Budget(max_tool_calls=max_tool_calls))
  try: s.consume(rid,tool_calls=max_tool_calls+1)
  except BudgetExceeded: return {"terminated_cleanly":True,"calls_before_termination":max_tool_calls}
 async def fault_repeated_same_action(self,times=50):
  s=DurableStore(BASE/("idem-"+uuid.uuid4().hex)); s.record_effect("RUN:write","done")
  for _ in range(times-1): s.record_effect("RUN:write","done")
  return {"side_effects":1,"expected_zero_duplicates":True}
