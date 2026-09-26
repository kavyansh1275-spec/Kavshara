# Kavshara

Kavshara is a local-first personal AI assistant built in Python.

## V1 goals

- Conversational CLI
- Ollama/local-model support
- Persistent JSON memory
- Simple brain/router layer
- Extensible tool interface
- Clean foundation for coding, files, research, and automation skills

## Requirements

- Python 3.11+
- Ollama installed and running locally
- A local Ollama model (default: `qwen2.5:3b`)

## Run

```powershell
python main.py
```

Then type a message. Use `/help` for commands and `/exit` to quit.

## Configuration

Set environment variables if needed:

```powershell
$env:KAVSHARA_MODEL="qwen2.5:3b"
$env:OLLAMA_HOST="http://127.0.0.1:11434"
```
