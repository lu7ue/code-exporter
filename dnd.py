import os

def handle_drop(event, folder_entry, scan_callback):
    """Handle folder drop event."""
    path = event.data.strip().strip("{}")
    if os.path.isdir(path):
        folder_entry.delete(0, "end")
        folder_entry.insert(0, path)
        scan_callback()
