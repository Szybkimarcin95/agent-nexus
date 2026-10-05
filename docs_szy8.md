# SZY-8 durable store

The first implementation is a JSON prototype for Termux and local development.

Each run is stored as one atomically replaced JSON file under runs/. Usage counters and terminal budget status are persisted with the run. Idempotency records are stored in idempotency.json; a repeated key returns the original effect, while a different result for the same key raises a conflict.

Migration path: preserve the envelope fields and move runs/effects into SQLite with a unique run_id and unique idempotency_key, then PostgreSQL for multi-device operation. Use transactions around usage consumption and effect insertion. The JSON prototype intentionally stays single-writer and uses a file lock at the caller boundary.

Budget policy: a limit is exceeded when usage becomes greater than the configured maximum; the run is marked budget_exceeded and the reason is persisted.
