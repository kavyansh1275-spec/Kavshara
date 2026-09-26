import json
from pathlib import Path
from datetime import datetime, timezone

MEMORY_ROOT = Path("data")
MEMORY_ROOT.mkdir(parents=True, exist_ok=True)

FACTS_FILE = MEMORY_ROOT / "facts.json"
EPISODES_FILE = MEMORY_ROOT / "episodes.json"
PREFERENCES_FILE = MEMORY_ROOT / "preferences.json"


def _load(path):
    if not path.exists():
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _save(path, data):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def remember_fact(subject, fact, source="user"):
    subject = str(subject).strip()
    fact = str(fact).strip()
    if not subject or not fact:
        return {"error": "subject and fact are required."}

    items = _load(FACTS_FILE)
    now = datetime.now(timezone.utc).isoformat()
    item = {"subject": subject, "fact": fact, "source": source, "updated_at": now}

    for existing in items:
        if existing["subject"].lower() == subject.lower():
            existing.update(item)
            _save(FACTS_FILE, items)
            return {"status": "updated", "fact": existing}

    items.append(item)
    _save(FACTS_FILE, items)
    return {"status": "saved", "fact": item}


def recall_memory(query, limit=10):
    query = str(query).strip().lower()
    if not query:
        return {"error": "query is required."}

    collections = [
        ("fact", _load(FACTS_FILE)),
        ("preference", _load(PREFERENCES_FILE)),
        ("episode", _load(EPISODES_FILE)),
    ]
    matches = []
    for kind, items in collections:
        for item in items:
            haystack = json.dumps(item, ensure_ascii=False).lower()
            if query in haystack:
                matches.append({"type": kind, **item})

    return {"query": query, "count": len(matches[:limit]), "results": matches[:limit]}


def remember_preference(category, preference):
    category = str(category).strip()
    preference = str(preference).strip()
    if not category or not preference:
        return {"error": "category and preference are required."}

    items = _load(PREFERENCES_FILE)
    now = datetime.now(timezone.utc).isoformat()
    item = {"category": category, "preference": preference, "updated_at": now}

    for existing in items:
        if existing["category"].lower() == category.lower():
            existing.update(item)
            _save(PREFERENCES_FILE, items)
            return {"status": "updated", "preference": existing}

    items.append(item)
    _save(PREFERENCES_FILE, items)
    return {"status": "saved", "preference": item}


def remember_episode(summary, project=".", tags=None):
    summary = str(summary).strip()
    if not summary:
        return {"error": "summary is required."}

    items = _load(EPISODES_FILE)
    item = {
        "summary": summary,
        "project": str(project),
        "tags": tags if isinstance(tags, list) else [],
        "created_at": datetime.now(timezone.utc).isoformat(),
    }
    items.append(item)
    _save(EPISODES_FILE, items)
    return {"status": "saved", "episode": item}


def list_memory():
    return {
        "facts": _load(FACTS_FILE),
        "preferences": _load(PREFERENCES_FILE),
        "episodes": _load(EPISODES_FILE),
    }


def build_memory_tools(registry):
    registry.register(
        "remember_fact",
        "Store a durable fact. Arguments: subject, fact, source optional.",
        remember_fact,
    )
    registry.register(
        "recall_memory",
        "Search structured long-term memory. Argument: query; limit optional.",
        recall_memory,
    )
    registry.register(
        "remember_preference",
        "Store a durable preference. Arguments: category, preference.",
        remember_preference,
    )
    registry.register(
        "remember_episode",
        "Store a past event or completed-work summary. Arguments: summary, project optional, tags optional list.",
        remember_episode,
    )
    registry.register(
        "list_memory",
        "List structured long-term memory.",
        list_memory,
    )
    return registry
