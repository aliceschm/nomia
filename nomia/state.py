import json
from pathlib import Path
from typing import Any
from nomia.models import create_empty_state, STATE_SCHEMA_VERSION_KEY, CURRENT_SCHEMA_VERSION

STATE_DIR_NAME = ".nomia"
STATE_FILE_NAME = "state.json"


def _state_file(project_root: Path) -> Path:
    return project_root / STATE_DIR_NAME / STATE_FILE_NAME


def load_state(project_root: Path) -> dict[str, Any]:
    path = _state_file(project_root)

    if not path.exists():
        return create_empty_state()

    with path.open("r", encoding="utf-8") as file:
        state = json.load(file)

    if STATE_SCHEMA_VERSION_KEY not in state:
        state[STATE_SCHEMA_VERSION_KEY] = CURRENT_SCHEMA_VERSION

    return state


def save_state(project_root: Path, state: dict[str, Any]) -> None:
    path = _state_file(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)
