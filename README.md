<h1 align="center">Otter</h1>

<div align="center">
  <p align="center"><i>Gather your project files in one sweep like an otter neatly collecting what it finds.</i></p>

  <p align="center">
    <img src="https://img.shields.io/badge/license-MIT-black">
    <img src="https://img.shields.io/badge/python-3.10+-black">
    <img src="https://img.shields.io/badge/platform-macOS%20%7C%20Windows-black">
    <img src="https://img.shields.io/badge/built%20with-🤍-000000">
  </p>
</div>

<div align="center">
  <a href="https://www.pexels.com/video/an-otter-swimming-2554576/">
    <img src="img/otter.gif" width="520">
  </a>
</div>

<br>

<div align="center">
  <p>Otter is a lightweight Python tool that quickly exports project files into a single text file, including each file’s path and content.</p>
  <p>Paste your project folder path, scan the files, select what you need, and export. Empty or unreadable files are automatically marked.</p>
</div>

---

## Current Features

- **Simple Graphical Interface:** Provide a lightweight Tkinter-based GUI for visual folder input and file selection.
- **Folder Scanning and Filtering:** Scan a folder and list all readable files inside it. Automatically skip unnecessary files and folders such as `.git`, `__pycache__`, `node_modules`, `.vscode`, images, logs, and binaries.  
- **File Selection and Exporting:** Select specific files using checkboxes and export them into a single text file (`project_export.txt`) saved in the Downloads folder. Each exported file includes its path and content.  
- **Empty File Handling:** Automatically mark empty or unreadable files with placeholders like "empty file" or "[Could not read file]".  
- **Pop-up Notifications:** Show clear pop-up messages for invalid folder paths, empty scan results, and successful exports.  

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
>   However, they might need to grant permission to run it — for example, on macOS, go to `System Settings` → `Privacy & Security`, click `Run Anyway`, and if necessary, run the following command in the Terminal to make it executable: `chmod +x /the-path-to/CodeExporter-macOS`.

## Credits
Video by Magda Ehlers: https://www.pexels.com/video/an-otter-swimming-2554576/