import json
from pathlib import Path
from typing import Any

from nomia.models import (
    CURRENT_SCHEMA_VERSION,
    STATE_CODE_HASH_KEY,
    STATE_FUNCTIONS_KEY,
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
        return state

    if not isinstance(rules, dict):
        raise ValueError(f"State field '{STATE_RULES_KEY}' must be an object: {path}")

    for rule_id, rule_data in rules.items():
        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ValueError(f"State contains an invalid rule id: {path}")

        if not isinstance(rule_data, dict):
            raise ValueError(
                f"State entry for rule '{rule_id}' must be an object: {path}"
            )

        functions = rule_data.get(STATE_FUNCTIONS_KEY)

        if functions is None:
            rule_data[STATE_FUNCTIONS_KEY] = {}
            continue

        if not isinstance(functions, dict):
            raise ValueError(
                f"State field '{STATE_FUNCTIONS_KEY}' for rule '{rule_id}' must be an object: {path}"
            )

        for function_name, function_data in functions.items():
            if not isinstance(function_name, str) or not function_name.strip():
                raise ValueError(
                    f"State contains an invalid function name for rule '{rule_id}': {path}"
                )

            if not isinstance(function_data, dict):
                raise ValueError(
                    f"State entry for function '{function_name}' in rule '{rule_id}' must be an object: {path}"
                )

            code_hash = function_data.get(STATE_CODE_HASH_KEY)

            if not isinstance(code_hash, str) or not code_hash.strip():
                raise ValueError(
                    f"State field '{STATE_CODE_HASH_KEY}' for function '{function_name}' in rule '{rule_id}' must be a non-empty string: {path}"
                )

    return state


def save_state(project_root: Path, state: dict[str, Any]) -> None:
    path = _state_file(project_root)
    path.parent.mkdir(parents=True, exist_ok=True)

    with path.open("w", encoding="utf-8") as file:
        json.dump(state, file, indent=2, ensure_ascii=False)