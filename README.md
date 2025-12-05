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

- **Simple Graphical Interface:** A lightweight Tkinter-based interface with drag-and-drop folder input, navigation buttons, and a clear button to reset the current project.
- **Folder Scanning and Filtering:** Automatically scans a selected folder, applies built-in ignore rules, and also reads `.gitignore` to skip irrelevant files such as caches, configs, images, logs, binaries, and other noise.
- **Flexible File Selection:** Choose files using checkboxes with quick actions like select all, deselect all, or invert selection.
- **Project Structure View:** A dedicated structure page provides a tree-style visualization of the project and supports one-click copy-to-clipboard.
- **File Exporting:** Export selected files into a single consolidated text file (`project_export.txt`) stored in the Downloads folder, including each file’s path and its content.
- **Empty File Handling:** Detects unreadable or empty files and marks them with clear placeholders such as "[Empty file]" or "[Could not read file]".
- **Pop-up Notifications:** Provides concise pop-ups for invalid paths, empty results, completed exports, and other key interactions.

---

## How to Run

Clone this repository and navigate to the project folder, then run:

```python
python -m venv venv          # Create a virtual environment
source venv/bin/activate     # Activate the environment on MacOS
python main.py               # Run the tool
```
If you are using Windows, the command for activating the enviornment may differ slightly. For example, you can run `.\venv\Scripts\Activate.ps1`.  
Please activate your environment using the appropriate command for your system before running `python main.py`.

### Build as a Standalone App (macOS Example)

If you want to turn this tool into a standalone app so you can run it directly without using the terminal, follow these steps:

1. Install PyInstaller (only needed once): `pip install pyinstaller`
2. In the project folder, run: `pyinstaller --noconfirm --onefile --windowed main.py`.  
    This will automatically create two folders: `build` and `dist`. Inside the `dist` folder, you will find an executable file named `main`.  
3. (Optional) Rename the file for clarity: `mv dist/main dist/Otter-macOS`
4. Now you can simply double-click `Otter-macOS` to open the app. It works exactly the same as running the Python script, but doesn’t require opening a terminal.

> Tip: 
> 1. You can move the `Otter-macOS` file anywhere you like (for example, to your Applications folder) and run it directly.
> 2. If you want to share this tool with your friends, you can simply send them the `Otter-macOS` file.<br>
>   However, they might need to grant permission to run it — for example, on macOS, go to `System Settings` → `Privacy & Security`, click `Run Anyway`, and if necessary, run the following command in the Terminal to make it executable: `chmod +x /the-path-to/Otter-macOS`.

## Credits
Video by Magda Ehlers: https://www.pexels.com/video/an-otter-swimming-2554576/