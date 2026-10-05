# Agent Nexus Runbook v0.3.0

## Scope
Termux runtime is read-only plus isolated test-scope writes. Production writes are locked. Remote deployment waits for a Linux host with Docker.

## Phase 1 — Active test suite
```bash
cd ~/agent-nexus
PYTHONPATH=. python -m pytest -q tests/
```

## Phase 2 — Termux runtime demo
```bash
python -m runtime_fallback.termux_runtime_demo
```

## Phase 3 — Local span viewer
```bash
python -m observability.span_viewer --path ~/agent-nexus/termux_rt/eventlog.jsonl --port 5150
```

## Phase 4 — Integrity scan
```bash
python -m observability.span_integrity --path ~/agent-nexus/termux_rt/eventlog.jsonl
```

## Phase 5 — Knowledge graph smoke
```bash
PYTHONPATH=. python -m pytest -q tests/test_knowledge.py
```

## Phase 6 — Manifest and archive
```bash
PYTHONPATH=. python -c "from pathlib import Path; from release.sign_manifest import write_manifest,verify_manifest; b=Path.home()/'agent-nexus'; m=write_manifest(b,b/'manifest.json','ReleaseManager'); print(verify_manifest(b,m))"
bash release/archive.sh
```

## Phase 7 — Remote Linux deployment
Only when a Docker host exists:
```bash
./deployment/remote_host_push.sh user@host
ssh user@host 'cd ~/agent-nexus && ./deployment/start.sh'
```

## Phase 8 — Controlled writes
Never enable production writes from this runbook until every gate-report field is green. Supervisor only; every write requires approval, idempotency key, run_id and trace_id.

## Rollback
Create a fresh archive with `bash release/archive.sh`; restore only to an explicitly selected destination.