import importlib
import sys

from nomia.config import load_config
from nomia.output import log
from nomia.project_scan import find_python_files, path_to_module
from nomia.registry import clear_registry, get_registry


def discover_functions(config_path: str | None = None, verbose: bool = False):
    clear_registry()

    config = load_config(config_path)
    project_root = config["_project_root"]
    sources = config["sources"]

    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)
        log(f"Added to sys.path: {project_root_str}", verbose)

    for source in sources:
        root = (project_root / source).resolve()
        files = find_python_files(root)

        log(f"Scanning source: {root}", verbose)
        log(f"Python files found: {len(files)}", verbose)

        for file in files:
            module_name = path_to_module(file, project_root)
            log(f"Importing: {module_name}", verbose)
            importlib.import_module(module_name)

    return get_registry()
