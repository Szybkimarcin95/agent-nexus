from __future__ import annotations
import time, uuid
from pathlib import Path
from agents.local_llm import LocalLLM
from capability import ROLE_CAPABILITY, decide, Decision
from invariants import InvariantViolation, check_inv003_no_tool_outside_capability
from write_gate import gate_write, is_write_locked
from eventlog import EventLog
from knowledge.knowledge_graph import KnowledgeGraph
from runtime_fallback.mini_graph import MiniGraph

class UnifiedRuntime:
    def __init__(self, base, role="GraphResearcher", model_path=None):
        self.base=Path(base); self.base.mkdir(parents=True,exist_ok=True)
        self.role=role; self.llm=LocalLLM(model_path)
        self.graph=MiniGraph(self.base/"mini_graph.sqlite")
        self.kg=KnowledgeGraph(self.base/"kg")
        self.log=EventLog(self.base/"eventlog.jsonl")

    @property
    def mode(self): return "fsm-degraded" if self.llm.fallback_mode else "llm"

    def _log(self, run_id, trace_id, event, **data):
        self.log.append({"run_id":run_id,"trace_id":trace_id,"event":event,**data})

    def handle(self, task):
        run_id="U-"+uuid.uuid4().hex[:10]; trace_id=uuid.uuid4().hex
        self._log(run_id,trace_id,"task-received",task=task[:200],mode=self.mode,role=self.role)
        try:
            tools=list(ROLE_CAPABILITY[self.role])
        except KeyError:
            return {"status":"capability-denied","run_id":run_id,"mode":self.mode}
        d=self.llm.decide(task,tools,self.role)
        self._log(run_id,trace_id,"decision",tool=d.tool,confidence=d.confidence,model=d.model_used)
        if d.tool is None:
            self._log(run_id,trace_id,"no-action",reason=d.payload.get("reason"))
            return {"status":"no-action","run_id":run_id,"reason":d.payload.get("reason"),"mode":self.mode}
        try: check_inv003_no_tool_outside_capability(self.role,d.tool)
        except InvariantViolation as e:
            self._log(run_id,trace_id,"cap-blocked",reason=str(e)); return {"status":"capability-denied","run_id":run_id,"tool":d.tool}
        decision=decide(self.role,d.tool)
        if decision == Decision.DISALLOW:
            return {"status":"capability-denied","run_id":run_id,"tool":d.tool}
        if decision == Decision.NEEDS_APPROVAL:
            self._log(run_id,trace_id,"hitl-pause",tool=d.tool)
            if is_write_locked(): return {"status":"approval-required","run_id":run_id,"pending_tool":d.tool,"locked":True,"mode":self.mode}
            return self._write(run_id,trace_id,d.tool,d.payload)
        result=self._read(d.tool,d.payload)
        self._log(run_id,trace_id,"execute-done",tool=d.tool)
        self.kg.put_node("runtime_task",{"tool":d.tool,"task":task[:200]},run_id,trace_id,self.role)
        return {"status":"done","run_id":run_id,"tool":d.tool,"result":result,"mode":self.mode}

    def _read(self,tool,payload):
        if tool=="neo4j.schema": return self.graph.get_schema()
        if tool=="neo4j.read": return self.graph.read_nodes(limit=50)
        return {"locally":"remote MCP unavailable","tool":tool}

    def _write(self,run_id,trace_id,tool,payload):
        try: gate_write(role=self.role,logical_tool=tool,payload=payload,run_id=run_id,approval_records=[])
        except InvariantViolation as e: return {"status":"write-blocked","run_id":run_id,"reason":str(e)}
        return {"status":"write-done","run_id":run_id,"mode":self.mode}
