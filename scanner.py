import os
from pathlib import Path

# --- Ignore rules --- #

SKIP_DIRS = {
    ".git", ".svn", ".hg", ".idea", ".vscode", ".cache",
    "__pycache__", "venv", ".venv", "env", ".mypy_cache", ".pytest_cache",
    ".tox", ".ruff_cache",
    "node_modules", ".yarn", ".yarn/cache", ".pnp", ".pnp.cjs",
    ".pnpm-store", ".parcel-cache", "dist", "coverage", ".next",
    ".nuxt", ".svelte-kit", ".angular", "out", "target", ".gradle",
    ".cxx", ".cargo", "vendor", "Pods", ".bundle", ".swiftpm",
    ".build", "Packages", ".sass-cache", ".nyc_output",
    ".godot", "shader_cache",
}

SKIP_FILES = {
    ".DS_Store", "Thumbs.db", "desktop.ini",
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml",
    "Pipfile.lock", "poetry.lock", "composer.lock",
    "Cargo.lock", "Podfile.lock", "Gemfile.lock"
}

SKIP_EXTS = {
    ".pyc", ".pyo", ".class", ".o", ".obj", ".dll", ".so", ".dylib",
    ".exe", ".log", ".tmp", ".bak", ".swp", ".swo",
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
    ".zip", ".tar", ".gz", ".bz2", ".7z", ".mp4", ".mov",
    ".avi", ".mp3", ".wav", ".cfg", ".import", ".translation",
    ".svg", ".tiff", ".bmp", ".blend", ".fbx", ".obj", ".stl",
    ".dae", ".lock", ".orig", ".rej", ".psd", ".pdf", ".doc",
    ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".epub", ".mobi",
    ".rtf", ".odt", ".ods", ".odp"
}

def should_skip_file(path: Path) -> bool:
    """Return True if a file should be excluded."""
    if path.name in SKIP_FILES:
        return True
    if path.suffix.lower() in SKIP_EXTS:
        return True
    return False

def should_prune_dir(dirname: str) -> bool:
    """Return True if a directory should not be scanned."""
    return dirname in SKIP_DIRS

# --- Gitignore support --- #

def load_gitignore_patterns(root: Path):
    """Read .gitignore patterns and return ignored dirs + files."""
    gitignore_path = root / ".gitignore"
    ignored_dirs = set()
    ignored_files = set()

    if not gitignore_path.exists():
        return ignored_dirs, ignored_files

    try:
        lines = gitignore_path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return ignored_dirs, ignored_files

    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue

        if line.startswith("/"):
            line = line[1:]

        if line.endswith("/"):
            ignored_dirs.add(line.rstrip("/"))
            continue

        if line.startswith("*."):
            ignored_files.add(line[1:])
            continue

        ignored_files.add(line)

    return ignored_dirs, ignored_files

# --- Core scanning --- #

def scan_folder(root: Path):
    """
    Scan folder and return list of Path objects that pass filters.
    GUI is responsible for displaying results.
    """
    results = []

    gitignore_dirs, gitignore_files = load_gitignore_patterns(root)

    for dirpath, dirs, files in os.walk(root):
        dirs[:] = [
            d for d in dirs
            if not should_prune_dir(d) and d not in gitignore_dirs
        ]

        base = Path(dirpath)

        for name in files:
            p = base / name

            if should_skip_file(p):
                continue
            if p.name in gitignore_files or p.suffix in gitignore_files:
                continue
            if any(part in SKIP_DIRS for part in p.relative_to(root).parts):
                continue

            results.append(p)

    return results
