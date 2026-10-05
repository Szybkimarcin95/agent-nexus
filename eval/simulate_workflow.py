import json
import uuid
from pathlib import Path

from eventlog import EventLog
from runstate import RunStore
from runtime_fallback.test_scope import TestScopeRuntime


class FullWorkflowSimulation:
    def __init__(self, base):
        self.base = Path(base)
        self.base.mkdir(parents=True, exist_ok=True)
        self.store = RunStore(self.base / "runs")
        self.log = EventLog(self.base / "sim_eventlog.jsonl")

    def _event(self, run_id, trace_id, name, **extra):
        self.log.append({"run_id": run_id, "trace_id": trace_id, "event": name, **extra})

    def simulate_full_cycle(self, task, role="Supervisor"):
        run_id = "sim-" + uuid.uuid4().hex[:12]
        trace_id = uuid.uuid4().hex
        envelope = {
            "run_id": run_id, "agent_name": "SimAgent", "prompt": task,
            "status": "paused_approval", "trace_id": trace_id,
            "pending_action": {"tool": "neo4j.write", "server": "neo4j",
                               "payload_preview": {"sim": "test"},
                               "rationale": "simulated write"},
            "approvals": [],
            "sdk_state_blob": json.dumps({"simulated_state": task}),
        }
        self._event(run_id, trace_id, "task_received", task=task)
        self.store.save(envelope)
        assert self.store.load(run_id)["status"] == "paused_approval"

        state = self.store.load(run_id)
        state["approvals"].append({"actor": "simulator", "decision": "approved"})
        state["status"] = "running"
        self.store.save(state)
        self._event(run_id, trace_id, "approval_recorded", decision="approved")

        assert self.store.load(run_id)["approvals"]
        result = TestScopeRuntime(self.base, role=role).exercise(run_id=run_id)
        self._event(run_id, trace_id, "shadow_write_exercised",
                    replays=result["replays"])
        self._event(run_id, trace_id, "audit_completed")

        problems = 0
        spans = 0
        event_path = self.base / "sim_eventlog.jsonl"
        for line in event_path.read_text().splitlines():
            if not line.strip():
                continue
            spans += 1
            item = json.loads(line)
            if item.get("run_id") != run_id or item.get("trace_id") != trace_id:
                problems += 1
        return {
            "run_id": run_id, "trace_id": trace_id, "phases_completed": 4,
            "final_status": "COMPLETED", "audit_spans": spans,
            "audit_problems": problems,
            "test_scope_replays": result["replays"],
            "write_exercise_ok": result["replays"] == 1,
        }
