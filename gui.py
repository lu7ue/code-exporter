import tkinter as tk
import tkinter.ttk as ttk
from tkinter import messagebox
from pathlib import Path
from tkinterdnd2 import TkinterDnD, DND_FILES

from scanner import scan_folder as scanner_run
from dnd import handle_drop


# ---------------- App Launcher ---------------- #

def launch_app():
    app = TkinterDnD.Tk()
    app.title("Otter")
    UI(app)
    app.mainloop()


# ---------------- Main UI Class ---------------- #

class UI:
    def __init__(self, root):
        self.root = root
        self.files = []
        self.file_vars = []
        self.build_layout()

    # -------------------------------------------------

    def build_layout(self):
        self.build_path_input()
        self.build_drop_zone()
        self.build_file_list_area()
        self.build_export_button()
        self.configure_scroll()

    # -------------------------------------------------
    # Folder path input row

    def build_path_input(self):
        tk.Label(self.root, text="Folder Path:").grid(
            row=0, column=0, padx=5, pady=5, sticky="w"
        )

        self.folder_entry = tk.Entry(self.root, width=50)
        self.folder_entry.grid(row=0, column=1, padx=5)

        tk.Button(self.root, text="OK", command=self.scan).grid(
            row=0, column=2, padx=5
        )

    # -------------------------------------------------
    # Drop zone

    def build_drop_zone(self):
        frame = tk.Frame(self.root)
        frame.grid(row=1, column=0, columnspan=3, padx=12, pady=12, sticky="ew")

        canvas = tk.Canvas(frame, height=60, highlightthickness=0, bd=0)
        canvas.pack(fill="both", expand=True)

        self.drop_canvas = canvas

        # ------ draw border -------
        def draw_border(color="#8e8e93"):
            canvas.delete("border")
            w = max(canvas.winfo_width() - 4, 1)
            h = max(canvas.winfo_height() - 4, 1)
            canvas.create_rectangle(
                2, 2, w, h,
                outline=color,
                width=1,
                tag="border"
            )

        canvas.bind("<Configure>", lambda e: draw_border())
        canvas.after(50, draw_border)

        # ------ center text -------
        self.drop_text_id = canvas.create_text(
            0, 0,
            text="Paste your project path above\nor drop the folder here",
            anchor="center",
            fill="#444",
            justify="center"
        )

        def reposition_text(event):
            canvas.coords(
                self.drop_text_id,
                canvas.winfo_width() / 2,
                canvas.winfo_height() / 2
            )

        canvas.bind("<Configure>", reposition_text)

        # ------ drag events -------
        frame.drop_target_register(DND_FILES)
        frame.dnd_bind("<<Drop>>", lambda e: handle_drop(e, self.folder_entry, self.scan))
        frame.dnd_bind("<<DragEnter>>", lambda e: draw_border("#555555"))
        frame.dnd_bind("<<DragLeave>>", lambda e: draw_border())

    # -------------------------------------------------
    # File list + scroll area

    def build_file_list_area(self):
        self.container = tk.Frame(self.root)
        self.container.grid(row=2, column=0, columnspan=3, sticky="nsew", padx=5)

        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(2, weight=1)

        # --- selection bar ---
        self.select_all_var = tk.BooleanVar(value=False)

        bar = tk.Frame(self.container)
        self.selection_bar = bar
        bar.grid_columnconfigure(0, weight=1)

        tk.Checkbutton(
            bar, text="Select All",
            variable=self.select_all_var,
            command=self.toggle_select_all
        ).grid(row=0, column=1, padx=5, sticky="e")

        tk.Button(
            bar, text="Invert Selection",
            command=self.do_invert
        ).grid(row=0, column=2, padx=10, sticky="e")

        bar.grid_remove()

        # --- scrollable list ---
        self.canvas = tk.Canvas(self.container)
        self.scroll_frame = tk.Frame(self.canvas)

        self.canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        self.scroll_frame.bind(
            "<Configure>",
            lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )

        scrollbar = tk.Scrollbar(self.container, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=scrollbar.set)

        self.canvas.grid(row=2, column=0, sticky="nsew")
        scrollbar.grid(row=2, column=1, sticky="ns")

    # -------------------------------------------------

    def build_export_button(self):
        tk.Button(
            self.root,
            text="Export Selected Files",
            command=self.export_files
        ).grid(row=3, column=0, columnspan=3, pady=10)

    # -------------------------------------------------
    # Scroll behavior

    def configure_scroll(self):
        # Windows / Linux
        self.root.bind_all("<MouseWheel>", self.on_scroll)
        self.root.bind_all("<Shift-MouseWheel>", self.on_scroll)

        # macOS two-finger
        self.root.bind_all("<Button-4>", lambda e: self.canvas.yview_scroll(-3, "units"))
        self.root.bind_all("<Button-5>", lambda e: self.canvas.yview_scroll(3, "units"))

    def on_scroll(self, event):
        # macOS two-finger scroll gives event.delta (positive=up, negative=down)
        if hasattr(event, "delta") and event.delta != 0:
            delta = int(-event.delta / 60)
        else:
            delta = -1 * (event.delta // 120) if event.delta != 0 else 0

        if delta == 0:
            delta = -1 if event.delta < 0 else 1

        self.canvas.yview_scroll(delta, "units")

    # -------------------------------------------------
    # Scan

    def scan(self):
        folder = Path(self.folder_entry.get().strip())
        if not folder.exists() or not folder.is_dir():
            messagebox.showerror("Error", "Invalid folder path!")
            return

        self.select_all_var.set(False)
        self.selection_bar.grid_remove()

        for w in list(self.scroll_frame.winfo_children()):
            w.destroy()

        self.files = scanner_run(folder)
        self.file_vars = []

        if not self.files:
            messagebox.showinfo("No Files Found", "No eligible files found in this folder!")
            return

        for i, p in enumerate(self.files):
            var = tk.BooleanVar(value=False)
            cb = tk.Checkbutton(
                self.scroll_frame,
                text=str(p.relative_to(folder)),
                variable=var,
                anchor="w",
                command=self.update_select_all_state
            )
            cb.grid(row=i, column=0, sticky="w")
            self.file_vars.append(var)

        self.selection_bar.grid(row=0, column=0, columnspan=2, sticky="ew")

        sep = ttk.Separator(self.container, orient="horizontal")
        sep.grid(row=1, column=0, columnspan=2, sticky="ew", pady=(0, 5))

        self.canvas.yview_moveto(0)
        self.root.update_idletasks()

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

        downloads = Path.home() / "Downloads" / "project_export.txt"

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
