import tkinter as tk
import tkinter.ttk as ttk
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
    "dist", "coverage", ".next", ".nuxt", ".svelte-kit", ".angular",
    # Java / Kotlin / Android
    "out", "target", ".gradle", ".cxx",
    # Rust
    "target", ".cargo",
    # Go / PHP / Ruby / Swift
    "vendor", "Pods", ".bundle", ".swiftpm", ".build", "Packages",
    # Misc tool caches
    ".sass-cache", ".nyc_output",
    # Godot engine cache
    ".godot", "shader_cache",
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
    # Large binaries unlikely helpful for code reviewing
    ".png", ".jpg", ".jpeg", ".gif", ".webp", ".ico",
    ".zip", ".tar", ".gz", ".bz2", ".7z",
    ".mp4", ".mov", ".avi", ".mp3", ".wav",
    # Godot / game engine config & cache
    ".cfg", ".import", ".translation",
    # More image & vector assets
    ".svg", ".tiff", ".bmp",
    # 3D / CAD files
    ".blend", ".fbx", ".obj", ".stl", ".dae",
    # Misc project clutter
    ".lock", ".orig", ".rej", ".psd",
    # Document formats
    ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx",
    # eBook / text archives
    ".epub", ".mobi",
    # Additional binary blobs
    ".rtf", ".odt", ".ods", ".odp",
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

# --- Read .gitignore and convert its patterns to usable sets --- #
def load_gitignore_patterns(root: Path):
    """
    Read .gitignore and return two sets:
    - ignored_dirs: directory names that should be skipped
    - ignored_files: file name patterns or extensions to skip
    """
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
            ignored_files.add(line[1:])   # store ".log"
            continue

        ignored_files.add(line)

    return ignored_dirs, ignored_files

# --- Main actions --- #

def scan_folder():
    """Scan the given folder and list all files inside it (with filtering)."""
    folder = folder_entry.get().strip()
    root = Path(folder)

    if not root.exists() or not root.is_dir():
        messagebox.showerror("Error", "Invalid folder path!")
        return

    gitignore_dirs, gitignore_files = load_gitignore_patterns(root)

    # Hide selection bar during refresh
    select_all_var.set(False)
    invert_var.set(False)
    selection_bar.grid_remove()

    # Clear previous file list
    for widget in scrollable_frame.winfo_children():
        widget.destroy()
    files.clear()
    file_vars.clear()

    i = 0

    for dirpath, dirs, filenames in os.walk(root):
        dirs[:] = [d for d in dirs if not should_prune_dir(d) and d not in gitignore_dirs]

        base = Path(dirpath)

        for filename in filenames:
            file_path = base / filename

            if should_skip_file(file_path):
                continue

            if file_path.name in gitignore_files or file_path.suffix in gitignore_files:
                continue

            if any(part in SKIP_DIRS for part in file_path.relative_to(root).parts):
                continue

            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(
                scrollable_frame,
                text=str(file_path.relative_to(root)),
                variable=var,
                anchor="w",
                command=update_select_all_state  # When this file checkbox changes, update Select All
            )
            cb.grid(row=i, column=0, sticky="w")
            file_vars.append(var)
            files.append(file_path)
            i += 1

    if i == 0:
        messagebox.showinfo("No Files Found", "No eligible files found in this folder!")
    else:
        selection_bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        separator = ttk.Separator(files_frame_container, orient="horizontal")
        separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0,5))

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
                except:
                    content = "[Could not read file]"
                out.write(f"{file_path}:\n{content}\n\n")

    messagebox.showinfo("Export Complete", f"Exported selected files to:\n{output_file}")

# --- GUI --- #

root = tk.Tk()
root.title("Otter")

tk.Label(root, text="Folder Path:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
tk.Button(root, text="OK", command=scan_folder).grid(row=0, column=2, padx=5, pady=5)

# Container holding selection bar + file list
files_frame_container = tk.Frame(root)
files_frame_container.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

files_frame_container.grid_columnconfigure(0, weight=1)
files_frame_container.grid_columnconfigure(1, weight=0)
files_frame_container.grid_rowconfigure(2, weight=1)

root.grid_rowconfigure(1, weight=1)
for c in range(3):
    root.grid_columnconfigure(c, weight=1)

# --- Selection toggles (always exist, initially hidden) --- #

select_all_var = tk.BooleanVar(value=False)
invert_var = tk.BooleanVar(value=False)

def update_select_all_state():
    """Update the Select All checkbox based on current file selections."""
    if file_vars and all(v.get() for v in file_vars):
        select_all_var.set(True)
    else:
        select_all_var.set(False)

def toggle_select_all():
    """When Select All is toggled, apply its state to all file checkboxes."""
    state = select_all_var.get()
    for v in file_vars:
        v.set(state)

def toggle_invert():
    """Invert current selection once, then reset the invert checkbox."""
    if invert_var.get():
        for v in file_vars:
            v.set(not v.get())
        invert_var.set(False)
        update_select_all_state()

selection_bar = tk.Frame(files_frame_container)

selection_bar.grid_columnconfigure(0, weight=1)

select_all_cb = tk.Checkbutton(selection_bar, text="Select All", variable=select_all_var, command=toggle_select_all)
invert_cb = tk.Checkbutton(selection_bar, text="Invert Selection", variable=invert_var, command=toggle_invert)

select_all_cb.grid(row=0, column=1, padx=5, sticky="e")
invert_cb.grid(row=0, column=2, padx=10, sticky="e")

selection_bar.grid_remove()

# --- Scrollable area --- #

canvas = tk.Canvas(files_frame_container)
scrollbar = tk.Scrollbar(files_frame_container, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
canvas.configure(yscrollcommand=scrollbar.set)

canvas.grid(row=2, column=0, sticky="nsew")
scrollbar.grid(row=2, column=1, sticky="ns")

files = []
file_vars = []

tk.Button(root, text="Export Selected Files", command=export_files).grid(
    row=2, column=0, columnspan=3, pady=10
)

def _on_mousewheel(event):
    # Windows + Linux
    canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

def _on_mac_scroll(event):
    # macOS uses event.delta with inverted direction
    canvas.yview_scroll(int(-1 * event.delta), "units")

# Windows / Linux
root.bind_all("<MouseWheel>", _on_mousewheel)

# macOS two-finger scroll
root.bind_all("<Shift-MouseWheel>", _on_mousewheel)
root.bind_all("<Button-4>", lambda e: canvas.yview_scroll(-3, "units"))
root.bind_all("<Button-5>", lambda e: canvas.yview_scroll(3, "units"))
root.bind_all("<MouseWheel>", _on_mac_scroll)

root.mainloop()
