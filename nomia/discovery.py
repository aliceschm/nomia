import importlib
import sys
from pathlib import Path

from nomia.config import load_config
from nomia.project_scan import find_python_files, path_to_module
from nomia.registry import clear_registry, get_registry


def discover_functions(config_path: str | None = None):
    clear_registry()

    config = load_config(config_path)
    project_root = config["_project_root"]
    sources = config["sources"]

    project_root_str = str(project_root)
    if project_root_str not in sys.path:
        sys.path.insert(0, project_root_str)

    for source in sources:
        root = (project_root / source).resolve()
        files = find_python_files(root)

        print(files)

        for file in files:
            module_name = path_to_module(file, project_root)
            print(f"Importing: {module_name}")
            importlib.import_module(module_name)

    return get_registry()