# Kavshara

Kavshara is a focused local-first personal AI assistant built around three things:

- 🎙️ **Listen** — foreground push-to-talk voice input.
- 🗣️ **Talk** — natural English/Hindi/Hinglish conversation with Windows voice output.
- 💻 **Code** — inspect, write, debug, validate, test, and improve projects in Kavshara's workspace.

## Personality

Kavshara speaks like a **caring elder-sister-style assistant**: warm, patient, practical, encouraging, and never romantic or flirty.

She can say things naturally such as:

> "Haan, samajh gayi. Pehle code dekhte hain, phir ek-ek problem fix karte hain."

The personality is only an AI style; Kavshara does not pretend to be a real family member.

## Voice

Voice is **push-to-talk / foreground-only**.

- Click **Talk to Kavshara** or use `/voice`.
- Speak normally in English, Hindi, or Hinglish.
- Speech recognition uses `en-IN`.
- Kavshara speaks the response through Windows System.Speech.
- Continuous/background microphone listening is not started automatically.

## Coding

Kavshara can work inside its controlled `workspace/`:

1. inspect a project
2. read relevant files
3. create/edit code
4. run supported Python code
5. inspect errors
6. validate Python/JSON
7. test and iterate
8. explain what changed

It does not claim that code worked unless the available tools actually verify it.

## Run

Install dependencies:

```powershell
pip install -r requirements.txt
```

Start the conversational CLI:

```powershell
python main.py
```

Or start the desktop interface:

```powershell
python desktop_app.py
```

Commands:

```
/help
/status
/remember <text>
/voice
/exit
```

## Architecture

```
Voice / Text
     ↓
  Kavshara Brain
     ↓
 Local Ollama model
     ↓
 Conversation OR Coding tools
     ↓
 Verified response
```

## Safety

- Voice input is explicit and foreground-only.
- Coding tools are scoped to Kavshara's workspace.
- There is no unrestricted shell tool.
- Kavshara does not silently access the microphone.
- Kavshara does not pretend an action succeeded when it did not.
