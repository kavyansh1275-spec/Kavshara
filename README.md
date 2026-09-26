# Kavshara

Local-first personal AI assistant in Python.

## Current capabilities

- Conversational CLI
- Ollama/local model support
- Persistent JSON memory
- Model-driven multi-step agent loop
- Safe workspace filesystem tools
- Python syntax inspection
- Controlled Python execution
- Automatic tool-result feedback

## Architecture

```
User
  ↓
Brain
  ↓
Agent
  ↓
Choose tool
  ↓
Execute
  ↓
Inspect result
  ↓
Choose next action
  ↓
Final response
```

## Run

```powershell
pip install -r requirements.txt
python main.py
```

Try:

```
Create a Python calculator at projects/calculator.py, test it, and fix any syntax errors.
```

Kavshara can now:
1. inspect the workspace
2. create/edit files
3. inspect Python syntax
4. run Python files
5. read execution errors
6. make another change
7. test again
8. report the result

## Safety boundary

Filesystem operations are restricted to `workspace/`.
Python execution is limited to workspace Python files and has a short timeout.
There is no general-purpose shell tool.

## Commands

- `/help`
- `/status`
- `/remember <text>`
- `/exit`
