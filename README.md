# Code Exporter

This is a super simple Python tool that makes exporting the contents of project files much easier.  

Just paste the **absolute path** of your project folder into the input box and click "OK". The tool will scan your project and list all the files it finds. You can then select the files you want to export by checking the boxes next to them. Once you click the "Export" button, the contents of the selected files will be saved into a single `.txt` file in your computer’s Downloads folder. Each file in the export includes its path and content, and empty files or folders are marked with placeholders like “Empty file” or “Empty folder.”

I created this tool to make it faster to copy project contents. For example, when I want to ask GPT to help me understand someone else’s project, I don’t have to manually open each file and copy its contents one by one — everything I need is collected automatically in one place.  

While building this tool, I also learned a lot about working with files in Python and using Tkinter to build a GUI. It was a really fun experience, and I added detailed comments in the first commit so you can check them out if you’re curious about how it works. I plan to improve this tool in future versions. Show a better UI, add instructions and display error messages.

If you want to use this tool on your computer, clone this repository and navigate to the project folder. Then, run:
```python
python -m venv venv          # Create a virtual environment
source venv/bin/activate     # Activate the environment
python main.py               # Run the tool
```
I’m using macOS, so if you’re on Windows, the commands may differ slightly — check and use the correct ones for your system.
