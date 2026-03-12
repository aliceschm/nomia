import importlib
from pathlib import Path

from nomia.project_scan import find_python_files, path_to_module
from nomia.registry import clear_registry, get_registry


def discover_functions(project_root: str = "example_app"):
    clear_registry()

    root = Path(project_root)
    files = find_python_files(root)

    print(files)

    for file in files:
        module_name = path_to_module(file, root.parent)
        print(f"Importing: {module_name}")
        importlib.import_module(module_name)

    return get_registry()