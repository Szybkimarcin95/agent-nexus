#!/data/data/com.termux/files/usr/bin/bash
set -eu
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
if ! command -v docker >/dev/null 2>&1; then
  echo "DEPLOYMENT_STATUS=BLOCKED_DOCKER_MISSING"
  echo "Local fallback is available: run pytest from $ROOT"
  exit 2
fi
cd "$ROOT/observability"
docker compose up -d
echo "DEPLOYMENT_STATUS=STARTED"
