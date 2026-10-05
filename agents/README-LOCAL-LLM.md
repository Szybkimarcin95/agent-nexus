# Agent Nexus SZY-22 Local LLM

Optional offline llama-cpp-python wrapper. With no GGUF model, the runtime uses deterministic FSM fallback. No API, no cloud and no billing.

Place a compatible GGUF file in ~/models. Prompt-injection scan runs before inference; structured output is checked against role capabilities; invariants and SZY-10 write lock remain active. No data leaves the device.