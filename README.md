# Kavshara

Local-first personal AI assistant in Python.

## V1 agent foundation
- Ollama/local model
- Persistent JSON memory
- Model-driven agent loop
- Safe workspace filesystem tools
- Extensible tool registry

## Run
```powershell
pip install -r requirements.txt
python main.py
```

Try:
```
list the files in my workspace
create a file called hello.txt containing Hello from Kavshara
```

Kavshara can decide when to use a tool, execute it, inspect the result, and continue.

## Commands
`/help` `/status` `/remember <text>` `/exit`

Filesystem tools are restricted to `workspace/`.
