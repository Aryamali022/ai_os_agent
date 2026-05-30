import os
import string


def search_file(query: str) -> str:
    """
    Searches for files across ALL drives on the PC.
    Returns the file paths directly to the chat interface.
    Skips system/hidden/heavy directories for speed.

    Args:
        query: The file name or keyword to search for.

    Returns:
        A string listing the found file paths or a not-found message.
    """
    if not query:
        return "No file name provided to search."

    query_lower = query.strip().lower()
    found_files = []
    max_results = 15

    # Directories to skip for speed and to avoid permission errors
    skip_dirs = {
        "Windows", "Program Files", "Program Files (x86)", "ProgramData",
        "$Recycle.Bin", "System Volume Information", "Recovery",
        "AppData", "node_modules", ".git", "venv", ".venv", "__pycache__",
        "build", "dist", ".idea", ".vscode", "site-packages",
    }

    # Discover all available drives (C:\, D:\, E:\, etc.)
    drives = []
    for letter in string.ascii_uppercase:
        drive = f"{letter}:\\"
        if os.path.exists(drive):
            drives.append(drive)

    try:
        for drive in drives:
            if len(found_files) >= max_results:
                break

            for root, dirs, files in os.walk(drive, topdown=True):
                # Skip unwanted directories in-place for speed
                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]

                for file_name in files:
                    if query_lower in file_name.lower():
                        full_path = os.path.join(root, file_name)
                        found_files.append(full_path)

                        if len(found_files) >= max_results:
                            break
                if len(found_files) >= max_results:
                    break

    except Exception as e:
        return f"Error while searching: {e}"

    if found_files:
        file_list = "\n".join([f"📄 {path}" for path in found_files])
        count_msg = f"(showing first {max_results})" if len(found_files) >= max_results else ""
        drives_str = ", ".join(drives)
        return f"Found {len(found_files)} matching file(s) {count_msg} across drives ({drives_str}):\n{file_list}"
    else:
        return f"No files found matching '{query}' on any drive."
