from __future__ import annotations
import hashlib, json, os, time
from pathlib import Path

GENESIS = "GENESIS-{predefined}"

def _hash(prev: str, entry: dict) -> str:
    body = json.dumps(entry, sort_keys=True, ensure_ascii=False, default=str)
    return hashlib.sha256((prev + body).encode("utf-8")).hexdigest()

class AppendOnlyLog:
    def __init__(self, path: Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._prev_hash, self._version = GENESIS, 0
        if self.path.exists():
            entries = self.read_all()
            if entries:
                self._version = entries[-1]["version"]
                self._prev_hash = entries[-1]["hash_curr"]

    def append(self, action, entity, payload, run_id, trace_id, role=""):
        self._version += 1
        entry = {"version": self._version, "action": action, "entity": entity,
                 "payload": payload, "ts": time.time(), "run_id": run_id,
                 "trace_id": trace_id, "role": role, "hash_prev": self._prev_hash}
        entry["hash_curr"] = _hash(self._prev_hash, entry)
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
            f.flush()
            os.fsync(f.fileno())
        self._prev_hash = entry["hash_curr"]
        return entry

    def read_all(self):
        if not self.path.exists():
            return []
        out = []
        for line in self.path.read_text(encoding="utf-8", errors="replace").splitlines():
            try:
                if line.strip(): out.append(json.loads(line))
            except json.JSONDecodeError:
                continue
        return out

    def verify_chain(self):
        entries = self.read_all()
        prev = GENESIS
        for e in entries:
            if e.get("hash_prev") != prev:
                return {"ok": False, "entries": len(entries), "problems": ["prev-chain-mismatch"], "broken_at": e.get("version")}
            want = _hash(prev, {k:v for k,v in e.items() if k != "hash_curr"})
            if e.get("hash_curr") != want:
                return {"ok": False, "entries": len(entries), "problems": ["hash-chain-mismatch"], "broken_at": e.get("version")}
            prev = e["hash_curr"]
        return {"ok": True, "entries": len(entries), "problems": [], "broken_at": None}

    def latest_version(self):
        return self._version
