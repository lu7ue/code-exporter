# Build Standalone Applications (macOS & Windows)

This guide explains how to package Otter into a standalone executable using **PyInstaller**, allowing you to run the tool without opening a terminal or installing Python.

## Windows Build Guide

To build the Windows version, you must run PyInstaller on a Windows system (cross-platform builds are not supported).

1. Install PyInstaller: `pip install pyinstaller`.
2. Run the build command in the project folder: `pyinstaller --noconfirm --onefile --windowed main.py`. 
    The output will appear in the `dist` folder as `main.exe`.
3. (Optional) Rename the file: `rename dist\main.exe Otter-Windows.exe`.
4. Double-click `Otter-Windows.exe` to run it.

## macOS Build Guide

Follow these steps to generate a standalone macOS application:

1. Install PyInstaller (only needed once): `pip install pyinstaller`
2. In the project folder, run: `pyinstaller --noconfirm --onefile --windowed main.py`.  
    This will automatically create two folders: `build` and `dist`. Inside the `dist` folder, you will find an executable file named `main`.  
3. (Optional) Rename the file for clarity: `mv dist/main dist/Otter-macOS`
4. Now you can simply double-click `Otter-macOS` to open the app. It works exactly the same as running the Python script, but doesn’t require opening a terminal.

> Tip: 
> 1. You can move the `Otter-macOS` file anywhere you like (for example, to your Applications folder) and run it directly.
> 2. If you want to share this tool with your friends, you can simply send them the `Otter-macOS` file.<br>
>   However, they might need to grant permission to run it — for example, on macOS, go to `System Settings` → `Privacy & Security`, click `Run Anyway`, and if necessary, run the following command in the Terminal to make it executable: `chmod +x /the-path-to/Otter-macOS`.