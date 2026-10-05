#!/data/data/com.termux/files/usr/bin/bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d_%H%M%S)"
TMP="$HOME/agent-nexus-archive_$STAMP"
OUT="$HOME/agent-nexus-v0.3.0_$STAMP.tar.gz"
mkdir "$TMP"
cp -R "$ROOT"/. "$TMP"/
tar -czf "$OUT" -C "$HOME" "$(basename "$TMP")"
rm -rf "$TMP"
printf 'Archive created: %s\n' "$OUT"
