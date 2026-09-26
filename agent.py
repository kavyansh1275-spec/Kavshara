import json
import re
from config import SYSTEM_PROMPT


class Agent:
    def __init__(self, provider, tools, memory, max_steps=8):
        self.provider = provider
        self.tools = tools
        self.memory = memory
        self.max_steps = max_steps

    def _system_prompt(self):
        tool_text = "\n".join(
            f"- {t['name']}: {t['description']}" for t in self.tools.descriptions()
        )
        return SYSTEM_PROMPT + """
\nYou are an agent, not only a chatbot.
For coding tasks, inspect existing files before changing them when useful.
Before changing an unfamiliar project, use project_summary or scan_project and find_in_project to understand its structure. Load get_project_memory for existing projects, create_snapshot before substantial multi-file changes, then compare_snapshot and save_project_memory after changes.\nAfter edits, use validate_project for Python/JSON projects. Then inspect_python and run_python when appropriate.
If a tool returns an error, diagnose it and try a reasonable correction.
Do not claim a task is complete until the available evidence supports it.

AVAILABLE TOOLS:
""" + (tool_text or "- None.") + """

TOOL PROTOCOL:
When a tool is needed, respond with ONLY valid JSON:
{"type":"tool_call","tool":"TOOL_NAME","arguments":{}}
Never invent tool names or arguments.
After a tool result, continue the task or provide the final answer.
"""

    def _parse_tool_call(self, text):
        candidates = [text]
        match = re.search(r"\{.*\}", text, re.DOTALL)
        if match:
            candidates.append(match.group(0))
        for candidate in candidates:
            try:
                data = json.loads(candidate)
            except json.JSONDecodeError:
                continue
            if (
                isinstance(data, dict)
                and data.get("type") == "tool_call"
                and isinstance(data.get("tool"), str)
                and isinstance(data.get("arguments", {}), dict)
            ):
                return data
        return None

    def run(self, user_message):
        messages = [
            {
                "role": "system",
                "content": self._system_prompt()
                + "\n\nSAVED MEMORY:\n"
                + self.memory.context(),
            },
            {"role": "user", "content": user_message},
        ]

        for step in range(self.max_steps):
            reply = self.provider.chat(messages)
            call = self._parse_tool_call(reply)

            if not call:
                return reply

            tool_name = call["tool"]
            try:
                result = self.tools.execute(tool_name, call.get("arguments", {}))
            except Exception as exc:
                result = {"error": str(exc), "tool": tool_name}

            messages.append({"role": "assistant", "content": reply})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"TOOL RESULT (step {step + 1}):\n"
                        + json.dumps(result, ensure_ascii=False, default=str)
                        + "\n\nContinue the task. Verify your work when appropriate."
                    ),
                }
            )

        return "I reached my tool-step limit before completing the task."
