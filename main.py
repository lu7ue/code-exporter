import tkinter as tk
from tkinter import messagebox
from pathlib import Path
import os

# --- Ignore rules (cross-language, conservative) --- #

SKIP_DIRS = {
    # VCS / IDE
    ".git", ".svn", ".hg", ".idea", ".vscode", ".cache",
    # Python
    "__pycache__", "venv", ".venv", "env", ".mypy_cache", ".pytest_cache", ".tox", ".ruff_cache",
    # Node / JS
    "node_modules", ".yarn", ".yarn/cache", ".pnp", ".pnp.cjs", ".pnpm-store", ".parcel-cache",
    "dist", "build", "coverage", ".next", ".nuxt", ".svelte-kit", ".angular",
    # Java / Kotlin / Android
    "out", "target", ".gradle", "build", ".cxx",
    # Rust
    "target", ".cargo",
    # Go / PHP / Ruby / Swift
    "vendor", "Pods", ".bundle", ".swiftpm", ".build", "Packages",
    # Misc tool caches
    ".sass-cache", ".nyc_output"
}

SKIP_FILES = {
    # OS cruft
    ".DS_Store", "Thumbs.db", "desktop.ini",
    # Lock files that don’t add code insight
    "package-lock.json", "yarn.lock", "pnpm-lock.yaml", "Pipfile.lock", "poetry.lock",
    "composer.lock", "Cargo.lock", "Podfile.lock", "Gemfile.lock"
}

SKIP_EXTS = {
    # Compiled / bytecode / objects
    ".pyc", ".pyo", ".class", ".o", ".obj", ".dll", ".so", ".dylib", ".exe",
    # Editor swap/backup/temp
    ".log", ".tmp", ".bak", ".swp", ".swo",
    # Large binaries that rarely help for “code review” style exports
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico", ".pdf",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".mp4", ".mov", ".avi", ".mp3", ".wav"
}

def should_skip_file(path: Path) -> bool:
    """Return True if a file should be skipped."""
    if path.name in SKIP_FILES:
        return True
    if path.suffix.lower() in SKIP_EXTS:
        return True
    return False

def should_prune_dir(dirname: str) -> bool:
    """Return True if a directory should be pruned from traversal."""
    return dirname in SKIP_DIRS

# --- Functions --- #

def scan_folder():
    """Scan the given folder and list all files inside it (with filtering)."""
    folder = folder_entry.get().strip()
    root = Path(folder)

    if not root.exists() or not root.is_dir():
        messagebox.showerror("Error", "Invalid folder path!")
        return

    # Clear previous results
    for widget in files_frame.winfo_children():
        widget.destroy()
    file_vars.clear()
    files.clear()

    i = 0
    # Use os.walk so we can prune directories in-place for speed
    for dirpath, dirs, filenames in os.walk(root):
        # Prune ignored dirs BEFORE descending
        dirs[:] = [d for d in dirs if not should_prune_dir(d)]

        base = Path(dirpath)
        for filename in filenames:
            file_path = base / filename
            # Skip files by name/extension
            if should_skip_file(file_path):
                continue
            # Also skip if any ancestor is in SKIP_DIRS (defensive, in case of symlinks, etc.)
            if any(part in SKIP_DIRS for part in file_path.relative_to(root).parts):
                continue

            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(
                files_frame,
                text=str(file_path.relative_to(root)),
                variable=var,
                anchor="w"
            )
            cb.grid(row=i, column=0, sticky="w")
            file_vars.append(var)
            files.append(file_path)
            i += 1

    if i == 0:
        messagebox.showinfo("No Files Found", "No eligible files found in this folder!")

def export_files():
    """Export selected files and their contents into one text file."""
    if not files:
        messagebox.showwarning("Warning", "No files to export!")
        return

    downloads = Path.home() / "Downloads"
    output_file = downloads / "project_export.txt"

    with open(output_file, "w", encoding="utf-8") as out:
        for file_path, var in zip(files, file_vars):
            if var.get():
                try:
                    content = file_path.read_text(encoding="utf-8").strip()
                    if not content:
                        content = "empty file."
                except (UnicodeDecodeError, FileNotFoundError):
                    content = "[Could not read file]"
                out.write(f"{file_path}:\n{content}\n\n")

    messagebox.showinfo("Export Complete", f"Exported selected files to:\n{output_file}")

# --- GUI (User Interface) --- #

root = tk.Tk()
root.title("File Exporter")

tk.Label(root, text="Folder Path:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="OK", command=scan_folder).grid(row=0, column=2, padx=5, pady=5)

files_frame = tk.Frame(root)
files_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

canvas = tk.Canvas(files_frame)
scrollbar = tk.Scrollbar(files_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

tk.Button(root, text="Export Selected Files", command=export_files).grid(
    row=2, column=0, columnspan=3, pady=10
)

files = []
file_vars = []
files_frame = scrollable_frame

root.mainloop()
