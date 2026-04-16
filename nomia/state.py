import json
from pathlib import Path
from typing import Any

from nomia.models import (
    CURRENT_SCHEMA_VERSION,
    STATE_RULES_KEY,
    STATE_SCHEMA_VERSION_KEY,
    create_empty_state,
)

STATE_DIR_NAME = ".nomia"
STATE_FILE_NAME = "state.json"


def _state_file(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME / STATE_FILE_NAME


def load_state(project_root: Path) -> dict[str, Any]:
    path = _state_file(project_root)

    if not path.exists():
        return create_empty_state()

    try:
        with path.open("r", encoding="utf-8") as file:
            state = json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid state file JSON: {path}") from exc

    if not isinstance(state, dict):
        raise ValueError(f"State file must contain a JSON object: {path}")

    if STATE_SCHEMA_VERSION_KEY not in state:
        state[STATE_SCHEMA_VERSION_KEY] = CURRENT_SCHEMA_VERSION

    rules = state.get(STATE_RULES_KEY)

    if rules is None:
        state[STATE_RULES_KEY] = {}
    elif not isinstance(rules, dict):
        raise ValueError(f"State field '{STATE_RULES_KEY}' must be an object: {path}")

    return state


def save_state(project_root: Path, state: dict[str, Any]) -> None:
    path = _state_file(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)