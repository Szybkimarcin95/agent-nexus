#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
BASE="$(cd "$(dirname "$0")/.." && pwd)"
cd "$BASE"
STAMP=$(date -u +%Y%m%d_%H%M%S)
OUT="$HOME/agent-nexus-v0.3.0-rc_$STAMP.tar.gz"
PYTHONPATH=. /data/data/com.termux/files/home/.agent-nexus/venv-termux/bin/python -m pytest -q tests/test_knowledge.py tests/test_szy18_sim.py tests/test_sign_manifest.py tests/test_runbook_env.py tests/test_szy22_local_llm.py
PYTHONPATH=. /data/data/com.termux/files/home/.agent-nexus/venv-termux/bin/python -c "from pathlib import Path; from release.sign_manifest import write_manifest,verify_manifest; b=Path.cwd(); m=write_manifest(b,b/'manifest.json','ReleaseManager'); v=verify_manifest(b,m); print(v); raise SystemExit(0 if v['ok'] else 1)"
tar -czf "$OUT" --exclude="__pycache__" --exclude=".pytest_cache" --exclude=".venv" -C "$(dirname "$BASE")" "$(basename "$BASE")"
printf "RC_READY=%s\nSZY-10=LOCKED\nAPI=OFF\nDOCKER=UNAVAILABLE\n" "$OUT"
