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
- Project structure scanning
- Project summaries and entrypoint detection
- Cross-file text search
- Automatic tool-result feedback
- Persistent project memory
- Safe project snapshots and change comparison
- Project-wide Python/JSON validation
- Automatic validation and debugging loop
- Persistent multi-step task planning and progress
- Public web search and URL fetching
- Current-information research workflow
- Multi-source deep research
- Structured long-term memory for facts, preferences, and episodes
- Autonomous project-engineering plans
- Safe self-testing and static QA
- English, Hindi, and Hinglish conversation support
- Explicit desktop-access permission layer
- Controlled Windows desktop gateway for common user folders
- Windows Start Menu application discovery and launching
- Local Windows text-to-speech output
- Speech-to-text input foundation

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
1. scan and understand a project structure
2. find relevant code across files
3. inspect the workspace
4. create/edit files
5. inspect Python syntax
6. run Python files
7. read execution errors
8. make another change
9. test again
10. validate the project
11. debug validation/runtime errors
12. update task progress
13. research current information when needed
14. compare multiple sources and identify uncertainty
15. recall and store durable memory when useful
16. execute and track autonomous engineering plans
17. run safe QA checks before completion
18. respect desktop permissions before local access
19. communicate naturally in the user's language
20. use controlled desktop access when permitted
21. discover and launch approved Start Menu applications
22. speak responses through Windows TTS when requested
23. transcribe audio through speech recognition when available
24. compare changes and report the result

## Safety boundary

Filesystem operations are restricted to `workspace/`.
Python execution is limited to workspace Python files and has a short timeout.
There is no general-purpose shell tool.

## Commands

- `/help`
- `/status`
- `/remember <text>`
- `/exit`
