import importlib
import sys
from collections.abc import Callable

from nomia.output import log
from nomia.project_scan import find_python_files, path_to_module


def _is_rule_function(obj: object) -> bool:
    return callable(obj) and hasattr(obj, "__nomia_rule__")


def _collect_rule_functions(module: object) -> list[tuple[str, Callable]]:
    discovered: list[tuple[str, Callable]] = []

    for obj in module.__dict__.values():
        if not _is_rule_function(obj):
            continue

        rule_id = getattr(obj, "__nomia_rule__")
        discovered.append((rule_id, obj))

    return discovered


def discover_functions(
    config: dict, verbose: bool = False
) -> list[tuple[str, Callable]]:
    project_root = config["_project_root"]
    sources = config["sources"]

    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
        log(f"Added to sys.path: {project_root_str}", verbose)

    discovered: list[tuple[str, Callable]] = []

    for source in sources:
        root = (project_root / source).resolve()
        files = find_python_files(root)

        log(f"Scanning source: {root}", verbose)
        log(f"Python files found: {len(files)}", verbose)

        for file in files:
            module_name = path_to_module(file, project_root)
            log(f"Importing: {module_name}", verbose)

            try:
                module = importlib.import_module(module_name)
            except Exception as exc:
                raise RuntimeError(
                    f"Failed to import module '{module_name}' from '{file}'. Original error: {exc}"
                ) from exc

            discovered.extend(_collect_rule_functions(module))

    return discovered
