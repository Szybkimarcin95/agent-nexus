from capability import CAPABILITIES,ROLE_CAPABILITY,APPROVAL_REQUIRED
class InvariantViolation(Exception): pass
def check_inv002_no_gated_without_record(tool,records):
    if tool in APPROVAL_REQUIRED and not any(r.get("tool")==tool and r.get("decision")=="approved" for r in records): raise InvariantViolation("INV-002")
def check_inv003_no_tool_outside_capability(role,tool):
    if tool not in ROLE_CAPABILITY.get(role,set()): raise InvariantViolation("INV-003")
def check_inv004_every_side_effect_has_idempotency_key(tool,key):
    if tool in CAPABILITIES and not CAPABILITIES[tool].read_only and not key: raise InvariantViolation("INV-004")
def check_inv006_budget_ok(status):
    if status=="budget_exceeded": raise InvariantViolation("INV-006")
def check_inv007_untrusted_content_cannot_expand_permissions(text):
    markers=("ignore previous instructions","add tool","expand capability","become admin","write-cypher enabled","read-only disabled","create a pr")
    low=text.lower()
    for m in markers:
        if m in low: raise InvariantViolation("INV-007")
def check_inv008_read_only_runtime_exposes_no_write_tools(tools):
    for tool in tools:
        cap=next((c for c in CAPABILITIES.values() if c.canonical_name==tool),None)
        if cap and not cap.read_only: raise InvariantViolation("INV-008")
