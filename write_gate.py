import os,hashlib,json,time
from capability import CAPABILITIES,APPROVAL_REQUIRED,Decision,decide
from invariants import InvariantViolation,check_inv002_no_gated_without_record,check_inv003_no_tool_outside_capability,check_inv004_every_side_effect_has_idempotency_key,check_inv007_untrusted_content_cannot_expand_permissions
def is_write_locked(): return os.environ.get("AGENT_NEXUS_WRITE","0")!="1"
def generate_idempotency_key(run_id,tool,payload):
 blob=json.dumps(payload,sort_keys=True,ensure_ascii=False,separators=(",",":"))
 return f"{run_id}:{tool}:{hashlib.sha256(blob.encode()).hexdigest()[:12]}"
def gate_write(role,logical_tool,payload,run_id,approval_records,tokens_used=0,tool_calls_used=0,budget_max_tool_calls=100,budget_max_total_tokens=50000):
 if is_write_locked(): raise InvariantViolation("SZY-10-LOCKED")
 if logical_tool not in APPROVAL_REQUIRED: return {"authorized":False,"reason":"not-a-write-tool"}
 check_inv003_no_tool_outside_capability(role,logical_tool)
 if decide(role,logical_tool)!=Decision.NEEDS_APPROVAL: raise InvariantViolation("SZY-10-DECISION")
 check_inv002_no_gated_without_record(logical_tool,approval_records)
 key=generate_idempotency_key(run_id,logical_tool,payload); check_inv004_every_side_effect_has_idempotency_key(logical_tool,key)
 check_inv007_untrusted_content_cannot_expand_permissions(json.dumps(payload,ensure_ascii=False,default=str))
 if tool_calls_used+1>budget_max_tool_calls: raise InvariantViolation("INV-006-budget-exceeded:tool-calls")
 if tokens_used>budget_max_total_tokens: raise InvariantViolation("INV-006-budget-exceeded:tokens")
 return {"authorized":True,"logical_tool":logical_tool,"canonical_tool":CAPABILITIES[logical_tool].canonical_name,"server":CAPABILITIES[logical_tool].server,"idempotency_key":key,"role":role,"run_id":run_id,"authorized_at":time.time()}
