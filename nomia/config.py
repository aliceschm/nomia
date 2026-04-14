from pathlib import Path

import yaml


DEFAULT_CONFIG_NAMES = ("nomia.yaml", "nomia.yml")


def resolve_config_path(config_path: str | None = None) -> Path:
    if config_path:
        path = Path(config_path).expanduser().resolve()

        if not path.exists():
            raise FileNotFoundError(f"Configuration file not found: {path}")

        return path

    current = Path.cwd().resolve()

    for directory in (current, *current.parents):
        for name in DEFAULT_CONFIG_NAMES:
            candidate = directory / name
            if candidate.exists():
                return candidate

    expected = " or ".join(DEFAULT_CONFIG_NAMES)
    raise FileNotFoundError(
        f"No configuration file found. Expected {expected} in the current directory or its parents."
    )


def load_config(config_path: str | None = None) -> dict:
    path = resolve_config_path(config_path)

    with path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file) or {}

    if not isinstance(data, dict):
        raise ValueError("Configuration file must contain a YAML object at the root.")

    sources = data.get("sources")
    if not sources:
        raise ValueError(
            "Configuration file must define at least one source in 'sources'."
        )

    if not isinstance(sources, list) or not all(
        isinstance(source, str) for source in sources
    ):
        raise ValueError("'sources' must be a list of strings.")

    rules = data.get("rules", [])

    if not isinstance(rules, list):
        raise ValueError("'rules' must be a list.")

    for rule in rules:
        if not isinstance(rule, dict):
            raise ValueError("Each rule in 'rules' must be an object.")

        rule_id = rule.get("id")

        if rule_id is None:
            raise ValueError("Each rule in 'rules' must define an 'id'.")

        if not isinstance(rule_id, str) or not rule_id.strip():
            raise ValueError("Rule 'id' must be a non-empty string.")

    project_root = path.parent

    for source in sources:
        source_path = (project_root / source).resolve()

        if not source_path.exists():
            raise ValueError(f"Configured source does not exist: {source}")

        try:
            source_path.relative_to(project_root)
        except ValueError as exc:
            raise ValueError(
                f"Configured source must be inside the project root: {source}"
            ) from exc
        
    data["_config_path"] = path
    data["_project_root"] = project_root

    return data
