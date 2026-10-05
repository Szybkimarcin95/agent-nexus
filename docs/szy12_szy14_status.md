# SZY-12 / SZY-13 / SZY-14

SZY-12 has a local JSONL span fallback and Docker Compose manifest. Docker is not installed on the Termux host, so Jaeger/Prometheus/Grafana cannot be started there.

SZY-13 has a one-command start script that reports the missing Docker runtime instead of pretending deployment succeeded.

SZY-14 validates eventlog -> JSON envelope -> SQLite migration and local span wrapping without API calls.
