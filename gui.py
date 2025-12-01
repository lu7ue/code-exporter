import tkinter as tk 
import tkinter.ttk as ttk 
import os
from tkinter import messagebox 
from pathlib import Path 
from tkinterdnd2 import TkinterDnD, DND_FILES 
from scanner import scan_folder as scanner_run 
from dnd import handle_drop 
from fnmatch import fnmatch

# -------------------------------------------------
# Launch the main TkinterDnD application
# -------------------------------------------------
def launch_app():
    app = TkinterDnD.Tk()
    app.title("Otter")
    app.geometry("650x500")
    UI(app)
    app.resizable(False, False)
    app.mainloop()

# -------------------------------------------------
# Main UI controller class handling all GUI logic
# -------------------------------------------------
class UI:
    def __init__(self, root):
        self.root = root
        self.files = []
        self.file_vars = []
        self.current_folder = None
        self.structure_text = None
        
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        self.pages = {}
        self.current_page = None
        
        self.create_main_page()
        self.create_structure_page()
        self.create_settings_page()
        
        self.show_page("main")

    # -------------------------------------------------
    # Create the main page layout
    # -------------------------------------------------
    def create_main_page(self):
        page = tk.Frame(self.main_container)
        self.pages["main"] = page
        self.build_layout(page)

    # -------------------------------------------------
    # Create project structure viewing page
    # -------------------------------------------------
    def create_structure_page(self):
        page = tk.Frame(self.main_container)
        self.pages["structure"] = page

        tk.Button(
            page, text="← Back", command=lambda: self.show_page("main")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        tk.Label(page, text="Project Structure", font=("Arial", 16)).grid(
            row=1, column=0, sticky="w", padx=10, pady=(10, 5)
        )

        page.grid_rowconfigure(2, weight=1)
        page.grid_columnconfigure(0, weight=1)

        main_container = tk.Frame(page, bd=1, relief=tk.SUNKEN)
        main_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Scrollable text container
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        toolbar = tk.Frame(main_container, height=35)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        toolbar.grid_propagate(False)

        toolbar.grid_columnconfigure(0, weight=1)
        toolbar.grid_columnconfigure(1, weight=0)

        # Copy button for structure output
        self.copy_btn = tk.Button(
            toolbar, 
            text="Copy", 
            width=8,
            command=self.copy_structure_graph
        )
        self.copy_btn.grid(row=0, column=1, padx=5)

        text_frame = tk.Frame(main_container)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_columnconfigure(1, weight=0)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Read-only text widget for structure tree
        txt = tk.Text(
            text_frame, 
            wrap="none",
            yscrollcommand=scrollbar.set,
            width=70,
            height=20
        )
        txt.grid(row=0, column=0, sticky="nsew")
        scrollbar.config(command=txt.yview)

        txt.configure(state="disabled")
        self.structure_text = txt

    # -------------------------------------------------
    # Create settings page (placeholder)
    # -------------------------------------------------
    def create_settings_page(self):
        page = tk.Frame(self.main_container)
        self.pages["settings"] = page
        
        tk.Button(
            page, text="← Back", command=lambda: self.show_page("main")
        ).place(x=10, y=10)
        
        tk.Label(
            page, text="Settings (placeholder)", font=("Arial", 16)
        ).place(x=20, y=60)

    # -------------------------------------------------
    # Switch between different UI pages
    # -------------------------------------------------
    def show_page(self, page_name):
        if self.current_page:
            self.current_page.pack_forget()
        
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)
        self.root.update_idletasks()
        
        # Refresh file list canvas when returning to main page
        if page_name == "main" and self.files:
            self._force_canvas_refresh()

    # -------------------------------------------------
    # Force canvas to update and adjust scroll region
    # -------------------------------------------------
    def _force_canvas_refresh(self):
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)
        self.root.after(10, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.root.after(20, lambda: self.canvas.update_idletasks())

    # -------------------------------------------------
    # Build layout for main page
    # -------------------------------------------------
    def build_layout(self, parent):
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        self.build_path_input(parent)
        self.build_drop_zone(parent)
        self.build_file_list_area(parent)
        self.build_bottom_bar(parent)

    # -------------------------------------------------
    # Build folder input bar
    # -------------------------------------------------
    def build_path_input(self, parent):
        parent.grid_columnconfigure(0, weight=0)
        parent.grid_columnconfigure(1, weight=1)
        parent.grid_columnconfigure(2, weight=0)
        
        tk.Label(parent, text="Folder Path:").grid(
            row=0, column=0, padx=8, pady=15, sticky="w"
        )
        self.folder_entry = tk.Entry(parent, width=52)
        self.folder_entry.grid(row=0, column=1, padx=5, sticky="ew")
        # Trigger folder scanning
        tk.Button(parent, text="OK", command=self.scan).grid(
            row=0, column=2, padx=8
        )

    # -------------------------------------------------
    # Build drag-and-drop folder zone
    # -------------------------------------------------
    def build_drop_zone(self, parent):
        frame = tk.Frame(parent)
        frame.grid(row=1, column=0, columnspan=3, padx=12, pady=12, sticky="ew")
        
        canvas = tk.Canvas(frame, height=60, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        self.drop_canvas = canvas

        def draw_border(color="#8e8e93"):
            canvas.delete("border")
            w = max(canvas.winfo_width() - 4, 1)
            h = max(canvas.winfo_height() - 4, 1)
            canvas.create_rectangle(
                2, 2, w, h, outline=color, width=1, tag="border"
            )

        canvas.bind("<Configure>", lambda e: draw_border())
        canvas.after(50, draw_border)

        # Center text inside drop area
        self.drop_text_id = canvas.create_text(
            0, 0, text="Paste your project path above\nor drop the folder here", 
            anchor="center", fill="#444", justify="center"
        )

        def reposition_text(event):
            canvas.coords(
                self.drop_text_id, canvas.winfo_width() / 2, canvas.winfo_height() / 2
            )

        canvas.bind("<Configure>", reposition_text)

        # Register drag and drop events
        frame.drop_target_register(DND_FILES)
        frame.dnd_bind("<<Drop>>", lambda e: handle_drop(e, self.folder_entry, self.scan))
        frame.dnd_bind("<<DragEnter>>", lambda e: draw_border("#555555"))
        frame.dnd_bind("<<DragLeave>>", lambda e: draw_border())

    # -------------------------------------------------
    # Handle scroll events for file list
    # -------------------------------------------------
    def _on_mousewheel(self, event):
        try:
            if hasattr(event, 'delta'):
                delta = event.delta
                if delta > 0:
                    self.canvas.yview_scroll(-1, "units")
                else:
                    self.canvas.yview_scroll(1, "units")
            else:
                self.canvas.yview_scroll(1, "units")
            
            self.canvas.update_idletasks()
            return "break"
        except:
            pass
        return "break"

    # -------------------------------------------------
    # Global scroll handler (detects hover area)
    # -------------------------------------------------
    def _on_global_mousewheel(self, event):
        x, y = self.root.winfo_pointerxy()
        widget = self.root.winfo_containing(x, y)
        if widget and self._is_in_file_list_area(widget):
            self._on_mousewheel(event)

    # -------------------------------------------------
    # Check if scroll event is inside file list widgets
    # -------------------------------------------------
    def _is_in_file_list_area(self, widget):
        if widget in [self.canvas, self.scroll_frame]:
            return True
        
        try:
            parent = widget.master
            while parent:
                if parent == self.scroll_frame:
                    return True
                parent = parent.master
        except:
            pass
        
        return False

    # -------------------------------------------------
    # Build file list area with scrollable canvas
    # -------------------------------------------------
    def build_file_list_area(self, parent):
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=0)
        parent.grid_columnconfigure(2, weight=0)
        
        self.container = tk.Frame(parent)
        self.container.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        self.container.grid_rowconfigure(2, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)

        self.select_all_var = tk.BooleanVar(value=False)

        # Selection bar (hidden until files exist)
        bar = tk.Frame(self.container)
        self.selection_bar = bar
        
        bar.grid_columnconfigure(0, weight=0)
        bar.grid_columnconfigure(1, weight=1)
        bar.grid_columnconfigure(2, weight=0)
        bar.grid_columnconfigure(3, weight=0)
        
        tk.Button(
            bar, text="Clear", command=self.clear_all
        ).grid(row=0, column=0, padx=5, sticky="w")
        
        tk.Checkbutton(
            bar, text="Select All", variable=self.select_all_var,
            command=self.toggle_select_all
        ).grid(row=0, column=2, padx=5, sticky="e")
        
        tk.Button(
            bar, text="Invert Selection", command=self.do_invert
        ).grid(row=0, column=3, padx=10, sticky="e")
        
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        bar.grid_remove()

        # Horizontal separator
        self.separator = ttk.Separator(self.container, orient="horizontal")
        self.separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 15))
        self.separator.grid_remove()

        # Scrollable area
        scroll_container = tk.Frame(self.container)
        scroll_container.grid(row=2, column=0, columnspan=2, sticky="nsew")
        
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(1, weight=0)
        
        self.canvas = tk.Canvas(scroll_container)
        self.scroll_frame = tk.Frame(self.canvas)

        # Frame inside canvas
        self.scrollable_frame_container = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        # Scrolling setup
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        self._setup_macos_scroll(scroll_container)

    # -------------------------------------------------
    # Bind macOS-compatible scrolling
    # -------------------------------------------------
    def _setup_macos_scroll(self, scroll_container):
        widgets = [self.canvas, self.scroll_frame, self.container, scroll_container]
        
        for widget in widgets:
            widget.bind("<MouseWheel>", self._on_mousewheel)
            widget.bind("<Button-4>", self._on_mousewheel)
            widget.bind("<Button-5>", self._on_mousewheel)
            widget.bind("<Shift-MouseWheel>", self._on_mousewheel)
        
        self.root.bind("<MouseWheel>", self._on_global_mousewheel)
        self.root.bind("<Button-4>", self._on_global_mousewheel)
        self.root.bind("<Button-5>", self._on_global_mousewheel)
        self.root.bind("<Shift-MouseWheel>", self._on_global_mousewheel)

    # -------------------------------------------------
    # Update scroll region when frame content changes
    # -------------------------------------------------
    def _on_frame_configure(self, event=None):
        try:
            bbox = self.canvas.bbox("all")
            if bbox:
                self.canvas.configure(scrollregion=bbox)
            else:
                self.canvas.configure(scrollregion=(0, 0, 0, 0))
        except:
            pass
        
        self.canvas.update_idletasks()

    # -------------------------------------------------
    # Ensure frame width matches canvas width
    # -------------------------------------------------
    def _on_canvas_configure(self, event=None):
        if event:
            self.canvas.itemconfig(self.scrollable_frame_container, width=event.width)
        self._on_frame_configure()

    # -------------------------------------------------
    # Build bottom bar with export/settings buttons
    # -------------------------------------------------
    def build_bottom_bar(self, parent):
        self.bottom_bar = tk.Frame(parent)
        self.bottom_bar.grid(row=3, column=0, columnspan=3, pady=15)
        
        self.btn_export = tk.Button(self.bottom_bar, text="Export Selected Files", command=self.export_files)
        self.btn_structure = tk.Button(self.bottom_bar, text="Project Structure", command=lambda: self.show_page("structure"))
        self.btn_settings = tk.Button(self.bottom_bar, text="Settings", command=lambda: self.show_page("settings"))
        
        # Default: only settings button visible
        self.btn_settings.grid(row=0, column=0, padx=5)

    # -------------------------------------------------
    # Reset UI state and clear all loaded files
    # -------------------------------------------------
    def clear_all(self):
        self.folder_entry.delete(0, tk.END)
        
        # Remove all checkboxes
        for w in list(self.scroll_frame.winfo_children()):
            w.destroy()
        
        self.files = []
        self.file_vars = []
        self.current_folder = None
        self.select_all_var.set(False)
        
        self.selection_bar.grid_remove()
        self.separator.grid_remove()
        
        # Bottom buttons reset
        for w in self.bottom_bar.winfo_children():
            w.grid_forget()
        self.btn_settings.grid(row=0, column=0, padx=5)
        
        self._on_frame_configure()

    # -------------------------------------------------
    # Scan selected folder for files (delegates to scanner)
    # -------------------------------------------------
    def scan(self):
        folder = Path(self.folder_entry.get().strip())
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("Error", "Invalid folder path!")
            return
            
        self.current_folder = folder
        self.select_all_var.set(False)
        
        # Clear previous file widgets
        for w in list(self.scroll_frame.winfo_children()):
            w.destroy()
            
        self.files = scanner_run(folder)
        self.file_vars = []
        
        if not self.files:
            messagebox.showinfo("No Files Found", "No eligible files found in this folder!")
            self.selection_bar.grid_remove()
            self.separator.grid_remove()
            
            for w in self.bottom_bar.winfo_children():
                w.grid_forget()
            self.btn_settings.grid(row=0, column=0, padx=5)
            return

        self.selection_bar.grid()
        self.separator.grid()
        
        # Create a checkbox for each file
        for i, p in enumerate(self.files):
            var = tk.BooleanVar(value=False)
            frame = tk.Frame(self.scroll_frame)
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=1)
            frame.grid_columnconfigure(0, weight=1)
            
            cb = tk.Checkbutton(
                frame, text=str(p.relative_to(folder)),
                variable=var, anchor="w", command=self.update_select_all_state
            )
            cb.grid(row=0, column=0, sticky="w")
            
            for widget in [frame, cb]:
                widget.bind("<MouseWheel>", self._on_mousewheel)
                widget.bind("<Button-4>", self._on_mousewheel)
                widget.bind("<Button-5>", self._on_mousewheel)
                widget.bind("<Shift-MouseWheel>", self._on_mousewheel)
            
            self.file_vars.append(var)

        self.canvas.yview_moveto(0)
        
        self._force_canvas_refresh()
        
        for w in self.bottom_bar.winfo_children():
            w.grid_forget()
            
        # Show all footer buttons
        self.btn_export.grid(row=0, column=0, padx=5)
        self.btn_structure.grid(row=0, column=1, padx=5)
        self.btn_settings.grid(row=0, column=2, padx=5)

        self.generate_structure_graph()

    # -------------------------------------------------
    # Update the state of "Select All" checkbox
    # -------------------------------------------------
    def update_select_all_state(self):
        if self.file_vars and all(v.get() for v in self.file_vars):
            self.select_all_var.set(True)
        else:
            self.select_all_var.set(False)

    # -------------------------------------------------
    # Export selected files to a text file in Downloads
    # -------------------------------------------------
    def export_files(self):
        if not self.files:
            messagebox.showwarning("Warning", "No files to export!")
            return

        if not any(v.get() for v in self.file_vars):
            messagebox.showwarning("No Selection", "Please select at least one file to export.")
            return

        downloads = Path.home() / "Downloads" / "project_export.txt"
        try:
            with open(downloads, "w", encoding="utf-8") as out:
                for path, var in zip(self.files, self.file_vars):
                    if var.get():
                        try:
                            content = path.read_text(encoding="utf-8").strip()
                            if not content:
                                content = "empty file."
                        except:
                            content = "[Could not read file]"
                        out.write(f"{path}:\n{content}\n\n")

            messagebox.showinfo("Export Complete", f"Exported selected files to:\n{downloads}")
        except Exception as e:
            messagebox.showerror("Export Error", f"Failed to export files:\n{str(e)}")

    # -------------------------------------------------
    # Toggle all checkboxes on/off
    # -------------------------------------------------
    def toggle_select_all(self):
        state = self.select_all_var.get()
        for v in self.file_vars:
            v.set(state)

    # -------------------------------------------------
    # Invert selection for all checkboxes
    # -------------------------------------------------
    def do_invert(self):
        for v in self.file_vars:
            v.set(not v.get())
        self.update_select_all_state()

    # -------------------------------------------------
    # Generate a textual tree-like representation of the project
    # -------------------------------------------------
    def generate_structure_graph(self):
        if not self.current_folder:
            return

        root = self.current_folder

        gitignore = root / ".gitignore"
        patterns = []
        if gitignore.exists():
            for line in gitignore.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)
        
        # Basic default ignore rules
        def default_ignore(name: str):
            if name.startswith("."):
                return True
            bad = [
                "build", "dist", "target", "__pycache__", "node_modules",
                "venv", ".venv", "env", "out", ".cache", ".mypy_cache",
                ".pytest_cache", ".gradle", ".cargo", "Pods", ".dart_tool",
            ]
            return name in bad
        
        # Check if file/dir should be excluded
        def ignored(path: Path):
            try:
                rel = str(path.relative_to(root))
            except ValueError:
                return False
            for p in patterns:
                if p.endswith("/") and rel.startswith(p.rstrip("/")):
                    return True
                if "*" in p and fnmatch(rel, p):
                    return True
                if rel == p:
                    return True
            return False

        tree_lines = []

        # Recursively collect directory items
        def collect_items(path: Path, prefix: str = ""):
            try:
                items = sorted(path.iterdir(), key=lambda p: p.name.lower())
            except (PermissionError, OSError):
                return
            
            filtered_items = []
            for item in items:
                if ignored(item) or default_ignore(item.name):
                    continue
                filtered_items.append(item)
            
            for i, item in enumerate(filtered_items):
                is_last = (i == len(filtered_items) - 1)
                if is_last:
                    line_prefix = prefix + "└── "
                    next_prefix = prefix + "    "
                else:
                    line_prefix = prefix + "├── "
                    next_prefix = prefix + "│   "
                
                tree_lines.append(f"{line_prefix}{item.name}")
                
                if item.is_dir():
                    collect_items(item, next_prefix)
        
        # Handle root-level items
        root_items = []
        for item in sorted(root.iterdir(), key=lambda p: p.name.lower()):
            if ignored(item) or default_ignore(item.name):
                continue
            root_items.append(item)
        
        for i, item in enumerate(root_items):
            is_last = (i == len(root_items) - 1)
            
            if is_last:
                prefix = "└── "
                next_prefix = "    "
            else:
                prefix = "├── "
                next_prefix = "│   "
            
            tree_lines.append(f"{prefix}{item.name}")
            
            if item.is_dir():
                collect_items(item, next_prefix)

        text = "\n".join(tree_lines)
        
        self.structure_text.configure(state="normal")
        self.structure_text.delete("1.0", "end")
        self.structure_text.insert("1.0", text)
        self.structure_text.configure(state="disabled")

    # -------------------------------------------------
    # Copy structure output to clipboard
    # -------------------------------------------------
    def copy_structure_graph(self):
        content = self.structure_text.get("1.0", "end-1c")
        if not content.strip():
            return
        
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        
        self.copy_btn.config(text="Copied!", state="disabled")
        
        def restore_button():
            self.copy_btn.config(text="Copy", state="normal")
        
        self.root.after(2000, restore_button)
