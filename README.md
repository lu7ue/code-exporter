# Code Exporter

Code Exporter is a simple Python tool that makes exporting project files fast and convenient. It saves time and keeps your exports well-organized.

Instead of manually opening each file, you can just paste the absolute path of your project folder into the input box and click "OK". The tool will scan your project and list all files it finds.   

You can then select the ones you want to export. When you click "Export", the selected files and their contents are saved into a single `.txt` file in your Downloads folder.  

Each file in the export includes its file path and content. Empty files or folders are automatically labeled as "Empty file" or "Could not read file".

---

## Current Features

- **Folder Scanning and Filtering:** Scan a folder and list all readable files inside it. Automatically skip unnecessary files and folders such as `.git`, `__pycache__`, `node_modules`, `.vscode`, images, logs, and binaries.  
- **File Selection and Exporting:** Select specific files using checkboxes and export them into a single text file (`project_export.txt`) saved in the Downloads folder. Each exported file includes its path and content.  
- **Empty File Handling:** Automatically mark empty or unreadable files with placeholders like "empty file" or "[Could not read file]".  
- **Pop-up Notifications:** Show clear pop-up messages for invalid folder paths, empty scan results, and successful exports.  
- **Simple Graphical Interface:** Provide a lightweight Tkinter-based GUI for visual folder input and file selection.

---

## How to Run

Clone this repository and navigate to the project folder, then run:

```python
python -m venv venv          # Create a virtual environment
source venv/bin/activate     # Activate the environment
python main.py               # Run the tool
```
If you are using Windows, the commands may differ slightly.  
Activate your environment using the appropriate command for your system before running `python main.py`.

### Build as a Standalone App (macOS Example)

If you want to turn this tool into a standalone app so you can run it directly without using the terminal, follow these steps:

1. Install PyInstaller (only needed once): `pip install pyinstaller`
2. In the project folder, run: `pyinstaller --noconfirm --onefile --windowed main.py`.  
    This will automatically create two folders: `build` and `dist`. Inside the `dist` folder, you will find an executable file named `main`.  
3. (Optional) Rename the file for clarity: `mv dist/main dist/CodeExporter-macOS`
4. Now you can simply double-click `CodeExporter-macOS` to open the app. It works exactly the same as running the Python script, but doesn’t require opening a terminal.

> Tip: 
> 1. You can move the CodeExporter-macOS file anywhere you like (for example, to your Applications folder) and run it directly.
> 2. If you want to share this tool with your friends, you can simply send them the `CodeExporter-macOS` file.<br>
>   However, they might need to grant permission to run it — for example, on macOS, go to `System Settings` → `Privacy & Security`, click `Run Anyway`, and if necessary, run the following command in the Terminal to make it executable: `chmod +x /path/to/CodeExporter-macOS`.

---

## Upcoming Features

**Basic Features**  
- Improve Default Ignore Rules: Automatically skip common useless files, including `.godot/shader_cache` and `.cfg` for game engine projects.  
- Read `.gitignore`: Automatically detect and apply rules from the project's `.gitignore` file.  
- Settings File (Auto-Created): Automatically create a settings file on first run; all user preferences are saved and read from it later.

**Personalization and Memory (depends on Settings File)**  
- Custom Exclude Rules: Add or remove any files or folders you want to skip.  
- Recent Paths: Automatically remember recently scanned folders for quick access.  
- Auto-Save Settings: Automatically save and restore preferences such as ignore rules and recently scanned folders.  
- Favorite Paths: Bookmark frequently used folders for one-click access.  
- Path Limit Control: Define how many recent or favorite paths to keep.  
- Import/Export Settings: Backup or transfer your personal settings to another device or version.

**Export and Security**  
- Export Archives: Support exporting selected files as `.zip` or `.tar.gz` archives.  
- Sensitive Info Scan: Detect and warn about sensitive data such as passwords, API keys, or private keys.

**Display and Visualization**  
- Project Structure List: Show a directory tree after scanning.  
- Project Structure Graph (Visualization): Generate a tree-style project map after the user clicks a button and allow exporting it as an image.

**Interaction and Integration**  
- Select All / Deselect All: Quickly select, unselect, or invert file selections.  
- Graphical Interface (GUI): Drag and drop folders for an intuitive, visual workflow.  
- VS Code Extension: Use CodeExporter directly from VS Code by right-clicking a folder.