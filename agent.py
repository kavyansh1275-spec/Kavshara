import json
import re

from config import SYSTEM_PROMPT


class Agent:
    """V2 reasoning loop. Tool choice is delegated to the model from tool metadata."""

    def __init__(self, provider, registry, executor, memory, max_steps=10):
        self.provider = provider
        self.registry = registry
        self.executor = executor
        self.memory = memory
        self.max_steps = max_steps

    def _system_prompt(self):
        return SYSTEM_PROMPT + """

KAVSHARA V2 TOOL USE:
- You have access to a registry of specialist tools.
- Choose tools by understanding the user's intent and the capabilities described in the registry.
- Do not use keyword rules or assume that a particular phrase always maps to a tool.
- You may call multiple tools sequentially when a task requires them.
- Use the minimum set of tools needed to complete the task.
- Read tool metadata carefully, including input schema, output format, risk level, permission and timeout.
- Never invent a tool, argument, capability, or tool result.
- A tool result is evidence from the execution layer. Inspect its status and output before deciding the next step.
- If a tool returns an error, invalid_arguments, permission_denied, or timeout status, adapt the plan or explain the limitation.
- For coding tasks, inspect relevant files before changing unfamiliar code and validate meaningful changes when possible.

TOOL CALL FORMAT:
When you decide a tool is needed, respond with ONLY valid JSON:
{"type":"tool_call","tool":"TOOL_NAME","arguments":{}}

Do not put explanations before or after a tool call.
If no tool is needed, answer the user normally.

AVAILABLE SPECIALIST TOOLS:
""" + self.registry.describe_for_agent()

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

            result = self.executor.execute(
                call["tool"],
                call.get("arguments", {}),
            )

            messages.append({"role": "assistant", "content": reply})
            messages.append(
                {
                    "role": "user",
                    "content": (
                        "TOOL RESULT:\n"
                        + json.dumps(result, ensure_ascii=False, default=str)
                        + "\n\n"
                        "Continue the task using this result. If the result failed, "
                        "diagnose the failure and choose a safe next step."
                    ),
                }
            )

        return (
            "Maine task ko safely stop kiya because the tool-step limit was reached. "
            "Agar kaam incomplete hai, next run mein continue kar sakte hain."
        )
