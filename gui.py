import tkinter as tk 
import tkinter.ttk as ttk 
import os
from tkinter import messagebox 
from pathlib import Path 
from tkinterdnd2 import TkinterDnD, DND_FILES 
from scanner import scan_folder as scanner_run 
from dnd import handle_drop 
from fnmatch import fnmatch

# ---------------- App Launcher ---------------- # 
def launch_app():
    app = TkinterDnD.Tk()
    app.title("Otter")
    
    # Set initial window size
    app.geometry("650x500")
    
    UI(app)
    app.resizable(False, False)
    app.mainloop()

# ---------------- Main UI Class ---------------- # 
class UI:
    def __init__(self, root):
        self.root = root
        self.files = []
        self.file_vars = []
        self.current_folder = None

        self.structure_text = None
        
        # Create main container
        self.main_container = tk.Frame(self.root)
        self.main_container.pack(fill="both", expand=True)
        
        self.pages = {}
        self.current_page = None
        
        self.create_main_page()
        self.create_structure_page()
        self.create_settings_page()
        
        self.show_page("main")

    def create_main_page(self):
        """Create main page"""
        page = tk.Frame(self.main_container)
        self.pages["main"] = page
        
        self.build_layout(page)
        self.configure_scroll()

    def create_structure_page(self):
        page = tk.Frame(self.main_container)
        self.pages["structure"] = page

        # Back button at top left
        tk.Button(
            page, text="← Back", command=lambda: self.show_page("main")
        ).grid(row=0, column=0, sticky="w", padx=10, pady=10)

        # Title
        tk.Label(page, text="Project Structure", font=("Arial", 16)).grid(
            row=1, column=0, sticky="w", padx=10, pady=(10, 5)
        )

        # Configure grid weights for the page
        page.grid_rowconfigure(2, weight=1)
        page.grid_columnconfigure(0, weight=1)

        # Main container for the text widget and controls
        main_container = tk.Frame(page, bd=1, relief=tk.SUNKEN)
        main_container.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0, 10))

        # Configure main container grid
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)

        # Toolbar frame at the top of the container
        toolbar = tk.Frame(main_container, height=35)
        toolbar.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        toolbar.grid_propagate(False)  # Keep fixed height

        # Configure toolbar columns
        toolbar.grid_columnconfigure(0, weight=1)  # Spacer on left
        toolbar.grid_columnconfigure(1, weight=0)  # Copy button on right

        # Copy button in toolbar
        self.copy_btn = tk.Button(
            toolbar, 
            text="Copy", 
            width=8,
            command=self.copy_structure_graph
        )
        self.copy_btn.grid(row=0, column=1, padx=5)

        # Text display area with scrollbar
        text_frame = tk.Frame(main_container)
        text_frame.grid(row=1, column=0, sticky="nsew", padx=5, pady=(0, 5))

        # Configure text frame grid
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        text_frame.grid_columnconfigure(1, weight=0)

        # Create scrollbar
        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # Create text widget
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

    def create_settings_page(self):
        """Create settings page"""
        page = tk.Frame(self.main_container)
        self.pages["settings"] = page
        
        tk.Button(
            page, text="← Back", command=lambda: self.show_page("main")
        ).place(x=10, y=10)
        
        tk.Label(
            page, text="Settings (placeholder)", font=("Arial", 16)
        ).place(x=20, y=60)

    def show_page(self, page_name):
        """Show specified page"""
        if self.current_page:
            self.current_page.pack_forget()
        
        self.current_page = self.pages[page_name]
        self.current_page.pack(fill="both", expand=True)
        
        # Force immediate update and rendering
        self.root.update_idletasks()
        
        # Special handling for main page to force canvas refresh
        if page_name == "main" and self.files:
            self._force_canvas_refresh()

    def _force_canvas_refresh(self):
        """Force canvas to refresh and display content immediately"""
        # Multiple methods to ensure canvas refreshes
        self.canvas.update_idletasks()
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        self.canvas.yview_moveto(0)  # Reset to top
        self.root.after(10, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.root.after(20, lambda: self.canvas.update_idletasks())

    # ------------------------------------------------- 
    def build_layout(self, parent):
        # Configure parent grid
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(1, weight=1)
        
        self.build_path_input(parent)
        self.build_drop_zone(parent)
        self.build_file_list_area(parent)
        self.build_bottom_bar(parent)

    # ------------------------------------------------- 
    # Folder path input row 
    def build_path_input(self, parent):
        # Adjusted padding to reduce space between label and entry
        parent.grid_columnconfigure(0, weight=0)  # Label column - no expansion
        parent.grid_columnconfigure(1, weight=1)  # Entry column - expands
        parent.grid_columnconfigure(2, weight=0)  # Button column - no expansion
        
        tk.Label(parent, text="Folder Path:").grid(
            row=0, column=0, padx=8, pady=15, sticky="w"  # Increased padx from 3 to 8 for better spacing
        )
        self.folder_entry = tk.Entry(parent, width=52)
        self.folder_entry.grid(row=0, column=1, padx=5, sticky="ew")  # Increased padx from 3 to 5
        tk.Button(parent, text="OK", command=self.scan).grid(
            row=0, column=2, padx=8  # Increased padx from 3 to 8
        )

    # ------------------------------------------------- 
    # Drop zone 
    def build_drop_zone(self, parent):
        frame = tk.Frame(parent)
        frame.grid(row=1, column=0, columnspan=3, padx=12, pady=12, sticky="ew")
        
        canvas = tk.Canvas(frame, height=60, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)
        self.drop_canvas = canvas

        # Draw border
        def draw_border(color="#8e8e93"):
            canvas.delete("border")
            w = max(canvas.winfo_width() - 4, 1)
            h = max(canvas.winfo_height() - 4, 1)
            canvas.create_rectangle(
                2, 2, w, h, outline=color, width=1, tag="border"
            )

        canvas.bind("<Configure>", lambda e: draw_border())
        canvas.after(50, draw_border)

        # Center text
        self.drop_text_id = canvas.create_text(
            0, 0, text="Paste your project path above\nor drop the folder here", 
            anchor="center", fill="#444", justify="center"
        )

        def reposition_text(event):
            canvas.coords(
                self.drop_text_id, canvas.winfo_width() / 2, canvas.winfo_height() / 2
            )

        canvas.bind("<Configure>", reposition_text)

        # Drag events
        frame.drop_target_register(DND_FILES)
        frame.dnd_bind("<<Drop>>", lambda e: handle_drop(e, self.folder_entry, self.scan))
        frame.dnd_bind("<<DragEnter>>", lambda e: draw_border("#555555"))
        frame.dnd_bind("<<DragLeave>>", lambda e: draw_border())

    # ------------------------------------------------- 
    # File list + scroll area 
    def build_file_list_area(self, parent):
        # Configure parent grid weights
        parent.grid_rowconfigure(2, weight=1)
        parent.grid_columnconfigure(0, weight=1)
        parent.grid_columnconfigure(1, weight=0)
        parent.grid_columnconfigure(2, weight=0)
        
        self.container = tk.Frame(parent)
        self.container.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)
        
        # Configure container internal grid weights
        self.container.grid_rowconfigure(2, weight=1)
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_columnconfigure(1, weight=0)

        # Selection bar
        self.select_all_var = tk.BooleanVar(value=False)
        bar = tk.Frame(self.container)
        self.selection_bar = bar
        
        # Configure bar columns: Clear button on left, spacer in middle, other buttons on right
        bar.grid_columnconfigure(0, weight=0)  # Clear button - no expansion
        bar.grid_columnconfigure(1, weight=1)  # Spacer - expands
        bar.grid_columnconfigure(2, weight=0)  # Select All - no expansion
        bar.grid_columnconfigure(3, weight=0)  # Invert Selection - no expansion
        
        # Clear button on the left
        tk.Button(
            bar, text="Clear", command=self.clear_all
        ).grid(row=0, column=0, padx=5, sticky="w")
        
        # Select All and Invert Selection on the right
        tk.Checkbutton(
            bar, text="Select All", variable=self.select_all_var,
            command=self.toggle_select_all
        ).grid(row=0, column=2, padx=5, sticky="e")
        
        tk.Button(
            bar, text="Invert Selection", command=self.do_invert
        ).grid(row=0, column=3, padx=10, sticky="e")
        
        bar.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 5))
        bar.grid_remove()

        # Separator
        self.separator = ttk.Separator(self.container, orient="horizontal")
        self.separator.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(10, 15))
        self.separator.grid_remove()

        # Scrollable list
        scroll_container = tk.Frame(self.container)
        scroll_container.grid(row=2, column=0, columnspan=2, sticky="nsew")
        
        scroll_container.grid_rowconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(0, weight=1)
        scroll_container.grid_columnconfigure(1, weight=0)
        
        self.canvas = tk.Canvas(scroll_container)
        self.scroll_frame = tk.Frame(self.canvas)
        
        # Use a frame inside canvas for better rendering
        self.scrollable_frame_container = self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        
        # Configure canvas to expand properly
        self.scroll_frame.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)
        
        scrollbar = tk.Scrollbar(scroll_container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def _on_frame_configure(self, event=None):
        """Update canvas scroll region and ensure proper rendering"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        # Force immediate update
        self.canvas.update_idletasks()

    def _on_canvas_configure(self, event=None):
        """Update the scrollable frame width to match canvas"""
        self.canvas.itemconfig(self.scrollable_frame_container, width=event.width)
        # Force refresh when canvas is configured
        self._on_frame_configure()

    # ------------------------------------------------- 
    # Export + Structure + Settings buttons 
    def build_bottom_bar(self, parent):
        # Bottom button bar 
        self.bottom_bar = tk.Frame(parent)
        self.bottom_bar.grid(row=3, column=0, columnspan=3, pady=15)
        
        # Buttons (initially hidden except Settings) 
        self.btn_export = tk.Button(self.bottom_bar, text="Export Selected Files", command=self.export_files)
        self.btn_structure = tk.Button(self.bottom_bar, text="Project Structure", command=lambda: self.show_page("structure"))
        self.btn_settings = tk.Button(self.bottom_bar, text="Settings", command=lambda: self.show_page("settings"))
        
        # Initial state: only show Settings centered 
        self.btn_settings.grid(row=0, column=0, padx=5)

    # ------------------------------------------------- 
    # Scroll behavior 
    def configure_scroll(self):
        # Bind scroll events to canvas
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind_all("<Button-4>", self._on_mousewheel)
        self.canvas.bind_all("<Button-5>", self._on_mousewheel)

    def _on_mousewheel(self, event):
        """Handle mouse wheel events"""
        if event.delta:
            self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
        else:
            if event.num == 4:
                self.canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                self.canvas.yview_scroll(1, "units")

    # ------------------------------------------------- 
    # Clear all function
    def clear_all(self):
        """Clear current project path and reset to initial view state"""
        # Clear folder entry
        self.folder_entry.delete(0, tk.END)
        
        # Clear file list
        for w in list(self.scroll_frame.winfo_children()):
            w.destroy()
        
        # Reset file-related variables
        self.files = []
        self.file_vars = []
        self.current_folder = None
        self.select_all_var.set(False)
        
        # Hide selection bar and separator
        self.selection_bar.grid_remove()
        self.separator.grid_remove()
        
        # Reset bottom buttons to initial state (only Settings)
        for w in self.bottom_bar.winfo_children():
            w.grid_forget()
        self.btn_settings.grid(row=0, column=0, padx=5)
        
        # Force canvas update
        self._on_frame_configure()

    # ------------------------------------------------- 
    # Scan 
    def scan(self):
        folder = Path(self.folder_entry.get().strip())
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("Error", "Invalid folder path!")
            return
            
        self.current_folder = folder
        self.select_all_var.set(False)
        
        # Clear existing file list
        for w in list(self.scroll_frame.winfo_children()):
            w.destroy()
            
        self.files = scanner_run(folder)
        self.file_vars = []
        
        if not self.files:
            messagebox.showinfo("No Files Found", "No eligible files found in this folder!")
            # Hide selection bar and separator
            self.selection_bar.grid_remove()
            self.separator.grid_remove()
            
            # Reset bottom buttons
            for w in self.bottom_bar.winfo_children():
                w.grid_forget()
            self.btn_settings.grid(row=0, column=0, padx=5)
            return

        # Show selection bar and separator
        self.selection_bar.grid()
        self.separator.grid()
        
        # Create file checkboxes
        for i, p in enumerate(self.files):
            var = tk.BooleanVar(value=False)
            # Use Frame to wrap each checkbox for proper layout
            frame = tk.Frame(self.scroll_frame)
            frame.grid(row=i, column=0, sticky="ew", padx=5, pady=1)
            frame.grid_columnconfigure(0, weight=1)
            
            cb = tk.Checkbutton(
                frame, text=str(p.relative_to(folder)),
                variable=var, anchor="w", command=self.update_select_all_state
            )
            cb.grid(row=0, column=0, sticky="w")
            
            self.file_vars.append(var)

        self.canvas.yview_moveto(0)
        
        # Force immediate rendering update after scan
        self._force_canvas_refresh()
        
        # Switch bottom bar to full mode 
        for w in self.bottom_bar.winfo_children():
            w.grid_forget()
            
        self.btn_export.grid(row=0, column=0, padx=5)
        self.btn_structure.grid(row=0, column=1, padx=5)
        self.btn_settings.grid(row=0, column=2, padx=5)

        self.generate_structure_graph()

    # ------------------------------------------------- 
    def update_select_all_state(self):
        if self.file_vars and all(v.get() for v in self.file_vars):
            self.select_all_var.set(True)
        else:
            self.select_all_var.set(False)

    # ------------------------------------------------- 
    def export_files(self):
        if not self.files:
            messagebox.showwarning("Warning", "No files to export!")
            return

        # If no file is selected, warn the user 
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
    # Selection toggles 
    def toggle_select_all(self):
        state = self.select_all_var.get()
        for v in self.file_vars:
            v.set(state)

    def do_invert(self):
        for v in self.file_vars:
            v.set(not v.get())
        self.update_select_all_state()

    # -------------------------------------------------
    # Generate project structure graph
    def generate_structure_graph(self):
        if not self.current_folder:
            return

        root = self.current_folder

        # load .gitignore
        gitignore = root / ".gitignore"
        patterns = []
        if gitignore.exists():
            for line in gitignore.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                patterns.append(line)

        def default_ignore(name: str):
            if name.startswith("."):
                return True
            bad = [
                "build", "dist", "target", "__pycache__", "node_modules",
                "venv", ".venv", "env", "out", ".cache", ".mypy_cache",
                ".pytest_cache", ".gradle", ".cargo", "Pods", ".dart_tool",
            ]
            return name in bad

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

        def collect_items(path: Path, prefix: str = ""):
            try:
                items = sorted(path.iterdir(), key=lambda p: p.name.lower())
            except (PermissionError, OSError):
                return
            
            # filter items
            filtered_items = []
            for item in items:
                if ignored(item) or default_ignore(item.name):
                    continue
                filtered_items.append(item)
            
            for i, item in enumerate(filtered_items):
                is_last = (i == len(filtered_items) - 1)
                
                # current line prefix
                if is_last:
                    line_prefix = prefix + "└── "
                    next_prefix = prefix + "    "
                else:
                    line_prefix = prefix + "├── "
                    next_prefix = prefix + "│   "
                
                tree_lines.append(f"{line_prefix}{item.name}")
                
                # if directory, recurse
                if item.is_dir():
                    collect_items(item, next_prefix)

        # special handling for root directory
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
    # Copy structure graph to clipboard
    def copy_structure_graph(self):
        """Copy structure graph to clipboard with button state feedback"""
        content = self.structure_text.get("1.0", "end-1c")
        if not content.strip():
            return
        
        # Copy to clipboard
        self.root.clipboard_clear()
        self.root.clipboard_append(content)
        
        # Change button state
        self.copy_btn.config(text="Copied!", state="disabled")
        
        # Restore original state after 2 seconds
        def restore_button():
            self.copy_btn.config(text="Copy", state="normal")
        
        self.root.after(2000, restore_button)