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
    files = []

    for path in root.rglob("*.py"):

        # se qualquer parte do caminho estiver nas ignoradas
        if any(part in IGNORED for part in path.parts):
            continue

        files.append(path)
    
    print(files)
    return files


def path_to_module(path: Path, project_root: Path) -> str:
    relative = path.relative_to(project_root)

    module = relative.with_suffix("")

    return ".".join(module.parts)