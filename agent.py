import json
import re
from config import SYSTEM_PROMPT


class Agent:
    def __init__(self, provider, tools, memory, max_steps=6):
        self.provider = provider
        self.tools = tools
        self.memory = memory
        self.max_steps = max_steps

    def _system_prompt(self):
        tool_text = "\n".join(
            f"- {t['name']}: {t['description']}" for t in self.tools.descriptions()
        )
        return SYSTEM_PROMPT + "\n\nAvailable tools:\n" + (tool_text or "- None.") + """
\n\nTOOL PROTOCOL:
When a tool is needed, respond with ONLY:
{"type":"tool_call","tool":"TOOL_NAME","arguments":{}}
Never invent a tool. After a tool result, continue the task or give the final answer.
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
            ):
                return data
        return None

    def run(self, user_message):
        messages = [
            {"role": "system", "content": self._system_prompt()
             + "\n\nSaved memory:\n" + self.memory.context()},
            {"role": "user", "content": user_message},
        ]

        for _ in range(self.max_steps):
            reply = self.provider.chat(messages)
            call = self._parse_tool_call(reply)

            if not call:
                return reply

            try:
                result = self.tools.execute(call["tool"], call.get("arguments", {}))
            except Exception as exc:
                result = {"error": str(exc), "tool": call["tool"]}

            messages.append({"role": "assistant", "content": reply})
            messages.append({
                "role": "user",
                "content": "TOOL RESULT:\n"
                + json.dumps(result, ensure_ascii=False, default=str)
                + "\n\nContinue the task.",
            })

        return "I reached my tool-step limit before completing the task."
