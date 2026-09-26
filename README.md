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
- Controlled Windows desktop gateway for approved user-content folders (Desktop, Documents, Downloads, Pictures, Videos, Music, OneDrive)
- Windows Start Menu application discovery and launching\n- Safe opening of approved files and folders\n- Directory listing and basic file metadata inspection
- Local Windows text-to-speech output
- Speech-to-text input foundation
- Interactive microphone voice commands
- Native Windows/Tkinter desktop chat interface
- Explicit desktop-access status and controls
- Controlled text-file creation, copying, renaming, and directory creation
- Controlled HTTP/HTTPS browser opening
- V11-V20 advanced foundations: research knowledge base, disabled workflows, project version records, reusable skills, local knowledge graph, explicit model-routing policy, and integrated personal workspace foundation

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

# Optional desktop GUI
python desktop_app.py
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
24. use interactive microphone voice commands
25. compare changes and report the result

## Safety boundary

Workspace tools stay inside `workspace/`. Desktop tools are separately permission-gated and restricted to approved user-content folders. File creation/copying refuses to overwrite existing files unless `overwrite=true` is explicitly supplied. Python execution is limited to workspace Python files and has a short timeout. There is no general-purpose shell tool. Voice input is explicit/foreground-only and is not started automatically.

## Commands

- `/help`
- `/status`
- `/remember <text>`
- `/voice`
- `/access`
- `/revoke`
- `/exit`

## Automated QA

GitHub Actions runs Python compilation, core-module imports, and a web-fetch safety smoke test on pushes and pull requests.


## V11-V20 roadmap

| Version | Foundation |
|---|---|
| V11 | Controlled Windows desktop interaction |
| V12 | Research and local knowledge base |
| V13 | Permission-gated workflow definitions |
| V14 | Project/version records |
| V15 | Reusable skill registry |
| V16 | Unified knowledge graph |
| V17 | Explicit local/cloud model routing policy |
| V18 | Advanced coding/editing orchestration foundation |
| V19 | Integrated personal workspace foundation |
| V20 | Unified Kavshara OS foundation |

The advanced workflow system stores workflow definitions but does not execute arbitrary commands, and workflows start disabled. Cloud model routing is disabled unless explicitly opted in through environment configuration.
