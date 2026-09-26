import json
import re
from config import SYSTEM_PROMPT


class Agent:
    def __init__(self, provider, tools, memory, max_steps=10):
        self.provider = provider
        self.tools = tools
        self.memory = memory
        self.max_steps = max_steps

    def _system_prompt(self):
        tool_text = "\n".join(
            f"- {t['name']}: {t['description']}" for t in self.tools.descriptions()
        )
        return SYSTEM_PROMPT + """

CODING WORKFLOW:
- For coding requests, first inspect relevant files/project structure when needed.
- Use the coding and project tools to create or edit code.
- Use validation, inspection, and test tools after meaningful changes.
- Prefer a direct implementation over a long explanation.
- You may use approved workspace tools for the coding project.
- Do not use research, workflow, knowledge-graph, cloud-routing, or unrelated automation tools unless the user explicitly asks for that capability and it is actually available.

TOOL PROTOCOL:
When a tool is needed, respond with ONLY valid JSON:
{"type":"tool_call","tool":"TOOL_NAME","arguments":{}}
Never invent tool names or arguments.
After a tool result, continue the task or provide the final answer.

AVAILABLE CODING TOOLS:
""" + (tool_text or "- None.")

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

            try:
                result = self.tools.execute(call["tool"], call.get("arguments", {}))
            except Exception as exc:
                result = {"error": str(exc), "tool": call["tool"]}

            messages.append({"role": "assistant", "content": reply})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        f"TOOL RESULT (step {step + 1}):\n"
                        + json.dumps(result, ensure_ascii=False, default=str)
                        + "\n\nContinue the coding task and verify your work when appropriate."
                    ),
                }
            )

        return "Maine task ko safely stop kiya because tool-step limit reach ho gayi. Agar kaam incomplete hai, hum next run mein continue kar sakte hain."
