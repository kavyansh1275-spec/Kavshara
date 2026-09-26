import json
from pathlib import Path
from config import MEMORY_FILE, MAX_MEMORY_ITEMS


class Memory:
    def __init__(self, path: str = MEMORY_FILE):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.items = self._load()

    def _load(self):
        if not self.path.exists():
            return []
        try:
            data = json.loads(self.path.read_text(encoding="utf-8"))
            return data if isinstance(data, list) else []
        except (json.JSONDecodeError, OSError):
            return []

    def save(self):
        self.path.write_text(
            json.dumps(self.items[-MAX_MEMORY_ITEMS:], indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def add(self, content: str, kind: str = "note"):
        content = content.strip()
        if not content:
            return
        self.items.append({"kind": kind, "content": content})
        self.save()

    def recent(self, limit: int = 10):
        return self.items[-limit:]

    def context(self, limit: int = 10) -> str:
        recent = self.recent(limit)
        if not recent:
            return "No saved memory."
        return "\n".join(f"- {item['content']}" for item in recent)
