# Import the tkinter library for GUI creation
import tkinter as tk
# Import messagebox from tkinter to show pop-up messages (error/warning/info)
from tkinter import messagebox
# Import Path from pathlib for easy and clean file and folder handling
from pathlib import Path

# If you want to view more notes about working with files in python and Tkinter usage, please check this link: https://github.com/lu7ue/noteverse/tree/main/what_i_learnt/Python

# --- Functions --- #

def scan_folder():
    """Scan the given folder and list all files inside it."""
    
    # Get the text input from the Entry widget (folder path)
    folder = folder_entry.get().strip()
    
    # Convert the folder string into a Path object for easier path handling
    root = Path(folder)

    # Check if the path exists and is a directory
    if not root.exists() or not root.is_dir():
        messagebox.showerror("Error", "Invalid folder path!")  # Show error popup if invalid
        return  # Stop the function here

    # Clear any previous results (checkboxes and data lists)
    for widget in files_frame.winfo_children():
        widget.destroy()  # Remove all previous checkboxes from the frame
    file_vars.clear()  # Clear list of BooleanVars (checkbox states)
    files.clear()      # Clear list of file paths

    # Walk through all files in the folder (recursively)
    for i, file_path in enumerate(root.rglob("*")):
        # Only include actual files (ignore folders)
        if file_path.is_file():
            # Create a BooleanVar to track whether this file is selected or not
            var = tk.BooleanVar(value=False)  # Default unchecked
            
            # Create a checkbox with the file's relative path as the label
            cb = tk.Checkbutton(
                files_frame,
                text=str(file_path.relative_to(root)),  # Display path relative to folder root
                variable=var,  # Connect this checkbox to the BooleanVar
                anchor="w"     # Align text to the left (west)
            )
            
            # Place the checkbox in the grid layout (each on a new row)
            cb.grid(row=i, column=0, sticky="w")
            
            # Store the variable and file path for later use
            file_vars.append(var)
            files.append(file_path)


def export_files():
    """Export selected files and their contents into one text file."""
    
    # If there are no files listed, show a warning
    if not files:
        messagebox.showwarning("Warning", "No files to export!")
        return

    # Define the output file path inside the user's Downloads folder
    downloads = Path.home() / "Downloads"
    output_file = downloads / "project_export.txt"

    # Open (or create) the export file for writing (overwrite mode)
    with open(output_file, "w", encoding="utf-8") as out:
        # Go through each file and its checkbox state together
        for file_path, var in zip(files, file_vars):
            if var.get():  # Only include checked (selected) files
                try:
                    # Read the file content and strip extra blank lines/spaces
                    content = file_path.read_text(encoding="utf-8").strip()
                    if not content:
                        content = "empty file."  # Mark empty files
                except (UnicodeDecodeError, FileNotFoundError):
                    # Handle files that can’t be read properly
                    content = "[Could not read file]"
                
                # Write file path and its content into the export file
                out.write(f"{file_path}:\n{content}\n\n")

    # Show info popup when export finishes successfully
    messagebox.showinfo("Export Complete", f"Exported selected files to:\n{output_file}")


# --- GUI (User Interface) --- #

# Create the main application window
root = tk.Tk()
root.title("File Exporter")  # Set window title

# --- Folder input section --- #
tk.Label(root, text="Folder Path:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
# Entry box for user to input the folder path
folder_entry = tk.Entry(root, width=50)
folder_entry.grid(row=0, column=1, padx=5, pady=5)
# "OK" button to trigger folder scan
tk.Button(root, text="OK", command=scan_folder).grid(row=0, column=2, padx=5, pady=5)

# --- File list area (scrollable) --- #
# Create a frame to hold checkboxes (inside a scrollable area)
files_frame = tk.Frame(root)
files_frame.grid(row=1, column=0, columnspan=3, sticky="nsew", padx=5, pady=5)

# Allow the file list frame to expand with the window
root.grid_rowconfigure(1, weight=1)
root.grid_columnconfigure(1, weight=1)

# --- Scrollbar setup --- #
canvas = tk.Canvas(files_frame)  # Canvas acts as a scrollable area
scrollbar = tk.Scrollbar(files_frame, orient="vertical", command=canvas.yview)
scrollable_frame = tk.Frame(canvas)  # Actual frame that will hold the checkboxes

# Update scrollable region whenever new widgets are added
scrollable_frame.bind(
    "<Configure>",
    lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
)

# Embed the scrollable frame into the canvas
canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
# Connect scrollbar to the canvas
canvas.configure(yscrollcommand=scrollbar.set)

# Pack (display) the canvas and scrollbar side by side
canvas.pack(side="left", fill="both", expand=True)
scrollbar.pack(side="right", fill="y")

# --- Export button at the bottom --- #
tk.Button(root, text="Export Selected Files", command=export_files).grid(
    row=2, column=0, columnspan=3, pady=10
)

# --- Data storage --- #
files = []       # Stores the Path objects (actual file paths)
file_vars = []   # Stores the BooleanVar linked to each checkbox

# Redirect file checkboxes to appear inside the scrollable frame
files_frame = scrollable_frame

# Keep the GUI running (event loop)
root.mainloop()
