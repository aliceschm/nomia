from pathlib import Path


IGNORED = {
    ".venv",
    "__pycache__",
    "build",
    "dist",
    ".git",
    ".mypy_cache",
    ".pytest_cache",
}


def find_python_files(root: Path) -> list[Path]:
    files: list[Path] = []

    for path in root.rglob("*.py"):

        if any(part in IGNORED for part in path.parts):
            continue

        files.append(path)

    return files


def path_to_module(path: Path, project_root: Path) -> str:
    relative = path.relative_to(project_root)

    parts = list(relative.with_suffix("").parts)

    # example_app/__init__.py -> example_app
    if parts[-1] == "__init__":
        parts = parts[:-1]

    return ".".join(parts)