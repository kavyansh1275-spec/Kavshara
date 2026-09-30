# Kavshara V1 — Foundation

A clean, local AI conversation foundation for Kavshara using Ollama/Qwen.

## Requirements

- Python 3.11+
- Ollama installed and running
- A local Ollama model, for example `qwen2.5:3b`

## Run

From the repository root:

```powershell
cd v1
python main.py
```

The default model is `qwen2.5:3b`. You can change it with:

```powershell
$env:KAVSHARA_MODEL="qwen2.5:3b"
```

Other supported environment variables:

- `KAVSHARA_OLLAMA_URL` — default `http://localhost:11434`
- `KAVSHARA_MODEL` — default `qwen2.5:3b`
- `KAVSHARA_TEMPERATURE` — default `0.7`
- `KAVSHARA_REQUEST_TIMEOUT` — default `120`
- `KAVSHARA_LOG_LEVEL` — default `INFO`

## Architecture

```text
User → main.py → KavsharaAgent → LLMProvider → Ollama/Qwen → Response
```

`main.py` is only the entry/dispatch layer. It does not interpret commands.

V1 deliberately contains no computer control, browser automation, messaging,
purchasing, permanent memory, autonomous actions, or external integrations.
