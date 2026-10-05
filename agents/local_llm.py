from __future__ import annotations
import json
from dataclasses import dataclass
from pathlib import Path

try:
    from llama_cpp import Llama
    LLM_AVAILABLE = True
except ImportError:
    Llama = None
    LLM_AVAILABLE = False

DEFAULT_MODEL_DIRS = [Path.home()/"models", Path.home()/"agent-nexus"/"models", Path("/sdcard/models")]

@dataclass
class LLMDecision:
    tool: str | None
    payload: dict
    confidence: float
    model_used: str
    reasoning: str

class LocalLLM:
    def __init__(self, model_path=None, n_ctx=2048, n_threads=2, n_batch=64, temperature=0.1):
        self.llm=None; self.model_path=None; self.model_name="none"; self.temperature=temperature
        self.fallback_mode=not LLM_AVAILABLE
        self.reason="llama-cpp-python not installed" if not LLM_AVAILABLE else ""
        if not LLM_AVAILABLE: return
        found=self._find_model(model_path)
        if not found:
            self.fallback_mode=True; self.reason="no GGUF model found on device"; return
        try:
            self.llm=Llama(model_path=str(found),n_ctx=n_ctx,n_threads=n_threads,n_batch=n_batch,verbose=False)
            self.model_path=found; self.model_name=found.name
        except Exception as exc:
            self.fallback_mode=True; self.reason=f"model load failed: {exc}"

    def _find_model(self, explicit):
        if explicit and Path(explicit).is_file(): return Path(explicit)
        for d in DEFAULT_MODEL_DIRS:
            if d.exists():
                found=sorted(d.glob("*.gguf"))
                if found: return found[0]
        return None

    def _safe(self, task):
        low=task.lower()
        for marker in ("ignore previous instructions","ignore instructions","add tool","expand capability","override system","delete everything"):
            if marker in low: return False, marker
        return True, ""

    def decide(self, task, allowed_tools, role="GraphResearcher"):
        safe, marker=self._safe(task)
        if not safe:
            return LLMDecision(None,{"reason":"prompt-injection-marker: "+marker,"blocked":True},1.0,self.model_name,"prompt injection blocked")
        if self.fallback_mode or self.llm is None:
            tool,payload=self._fsm(task)
            return LLMDecision(tool,payload,0.5,"fsm-fallback","no local model; deterministic FSM")
        prompt="Return only JSON tool calls. Allowed tools: "+json.dumps(allowed_tools)+" Task: "+task
        try:
            raw=self.llm.create_completion(prompt=prompt,max_tokens=256,temperature=self.temperature)
            obj=json.loads(raw.get("choices",[{}])[0].get("text","").strip().strip(chr(96)))
            tool=obj.get("tool"); payload=obj.get("payload",{})
            if tool is not None and tool not in allowed_tools:
                return LLMDecision(None,{"reason":"tool outside allowed list","blocked":True},0.3,self.model_name,"capability pre-filter")
            return LLMDecision(tool,payload,0.8,self.model_name,"structured local LLM decision")
        except Exception as exc:
            tool,payload=self._fsm(task)
            return LLMDecision(tool,payload,0.2,"fsm-fallback","LLM parse failure: "+str(exc))

    def _fsm(self, task):
        low=task.lower()
        for keys,tool in [(("utwórz","usuń","napisz"),"neo4j.write"),(("schema",),"neo4j.schema"),(("top 10","węzłów","wezłów"),"neo4j.read"),(("projekt","projekty"),"neo4j.read"),(("issue",),"github.issue.read"),(("pull request"," pr"),"github.pr.read")]:
            if any(k in low for k in keys): return tool,{"task":task,"fallback":True}
        return None,{"reason":"cannot_answer","task":task}
