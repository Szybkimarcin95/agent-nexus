from capability import decide,Decision
from invariants import check_inv007_untrusted_content_cannot_expand_permissions,InvariantViolation
class GoldenRunner:
 def __init__(self,path): self.path=path
 def run_A(self,t):
  d=decide("GraphResearcher",t["tool"]); return {"id":t["id"],"status":"success" if d==Decision.ALLOW else "blocked","decision":d.value}
 def run_B(self,t):
  d=decide("Supervisor",t["tool"]); return {"id":t["id"],"executed":False,"status":"approval_required" if d==Decision.NEEDS_APPROVAL else "blocked"}
 def run_C(self,t):
  try: check_inv007_untrusted_content_cannot_expand_permissions(t["text"])
  except InvariantViolation: return {"id":t["id"],"status":"injection_blocked"}
  return {"id":t["id"],"status":"UNEXPECTED"}
