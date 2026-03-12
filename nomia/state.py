import json
from pathlib import Path
from typing import Any

STATE_DIR = Path(".nomia")
STATE_FILE = STATE_DIR / "state.json"


def load_state() -> dict[str, Any]:
    if not STATE_FILE.exists():
        return {"rules": {}}

    with STATE_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


def save_state(state: dict[str, Any]) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)

    with STATE_FILE.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)