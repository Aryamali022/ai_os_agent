import os
import string
import time


def search_file(query: str) -> str:
    """
    Searches for files across all drives on the PC.
    Prioritises common user folders (Desktop, Documents, Downloads) before
    doing a broader drive-wide scan. Stops after max_results or TIMEOUT_SECONDS.

    Args:
        query: The file name or keyword to search for.

    Returns:
        A string listing the found file paths or a not-found message.
    """
    if not query or not query.strip():
        return "No file name provided to search."

    query_lower = query.strip().lower()
    found_files = []
    max_results = 15
    TIMEOUT_SECONDS = 20  # stop scanning after this many seconds

    skip_dirs = {
        "Windows", "Program Files", "Program Files (x86)", "ProgramData",
        "$Recycle.Bin", "System Volume Information", "Recovery",
        "AppData", "node_modules", ".git", "venv", ".venv", "__pycache__",
        "build", "dist", ".idea", ".vscode", "site-packages",
    }

    # Search common user folders first for a fast hit
    user_home = os.path.expanduser("~")
    priority_dirs = [
        os.path.join(user_home, "Desktop"),
        os.path.join(user_home, "Documents"),
        os.path.join(user_home, "Downloads"),
        os.path.join(user_home, "Pictures"),
        os.path.join(user_home, "Videos"),
        os.path.join(user_home, "Music"),
        user_home,
    ]

    # Then add full drive roots (excluding duplicates)
    drives = [f"{l}:\\" for l in string.ascii_uppercase if os.path.exists(f"{l}:\\")]
    search_roots = priority_dirs + drives

    deadline = time.monotonic() + TIMEOUT_SECONDS

    for root_dir in search_roots:
        if not os.path.isdir(root_dir):
            continue
        if len(found_files) >= max_results:
            break
        if time.monotonic() > deadline:
            break

        try:
            for root, dirs, files in os.walk(root_dir, topdown=True):
                if len(found_files) >= max_results or time.monotonic() > deadline:
                    break

                dirs[:] = [d for d in dirs if d not in skip_dirs and not d.startswith('.')]

                for file_name in files:
                    if query_lower in file_name.lower():
                        full_path = os.path.join(root, file_name)
                        # Avoid duplicates when drive roots overlap with priority dirs
                        if full_path not in found_files:
                            found_files.append(full_path)
                        if len(found_files) >= max_results:
                            break

        except PermissionError:
            continue
        except Exception as e:
            return f"Error while searching: {e}"

    if found_files:
        file_list = "\n".join([f"📄 {path}" for path in found_files])
        timed_out = time.monotonic() > deadline
        note = f" (showing first {max_results})" if len(found_files) >= max_results else ""
        timeout_note = " (search timed out — more files may exist)" if timed_out else ""
        return f"Found {len(found_files)} file(s){note}{timeout_note}:\n{file_list}"
    else:
        timed_out = time.monotonic() > deadline
        extra = " (search timed out — try a more specific name)" if timed_out else ""
        return f"No files found matching '{query}'.{extra}"
