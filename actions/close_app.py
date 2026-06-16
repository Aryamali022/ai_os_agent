import psutil

# Friendly names users might say -> the actual process executable name(s)
APP_PROCESS_ALIASES = {
    "notepad": ["notepad.exe"],
    "calculator": ["calculator.exe", "calc.exe", "win32calc.exe"],
    "calc": ["calculator.exe", "calc.exe", "win32calc.exe"],
    "paint": ["mspaint.exe", "paintstudio.view.exe"],
    "word": ["winword.exe"],
    "excel": ["excel.exe"],
    "powerpoint": ["powerpnt.exe"],
    "chrome": ["chrome.exe"],
    "google chrome": ["chrome.exe"],
    "edge": ["msedge.exe"],
    "microsoft edge": ["msedge.exe"],
    "firefox": ["firefox.exe"],
    "brave": ["brave.exe"],
    "spotify": ["spotify.exe"],
    "vlc": ["vlc.exe"],
    "vs code": ["code.exe"],
    "vscode": ["code.exe"],
    "visual studio code": ["code.exe"],
    "explorer": ["explorer.exe"],
    "file explorer": ["explorer.exe"],
    "task manager": ["taskmgr.exe"],
    "cmd": ["cmd.exe"],
    "command prompt": ["cmd.exe"],
    "powershell": ["powershell.exe", "pwsh.exe"],
    "terminal": ["windowsterminal.exe"],
}


def close_app(app_name: str) -> str:
    """
    Closes (terminates) all running processes matching the given application name.

    Matches against a friendly-name alias table first; if the name isn't known,
    falls back to a case-insensitive substring match on running process names.

    Args:
        app_name: The application name to close (e.g., "notepad", "chrome").

    Returns:
        A string message indicating which processes were closed, or that none
        were found.
    """
    if not app_name or not app_name.strip():
        return "No application name provided to close."

    name = app_name.strip().lower()

    # Resolve to a set of target executable names
    target_exes = set(APP_PROCESS_ALIASES.get(name, []))
    # Always also allow matching the raw name with/without .exe
    raw = name[:-4] if name.endswith(".exe") else name
    fallback_match = raw  # used for substring matching

    terminated = []
    failed = []

    for proc in psutil.process_iter(["name"]):
        proc_name = (proc.info.get("name") or "").lower()
        if not proc_name:
            continue

        is_match = (
            proc_name in target_exes
            or (not target_exes and fallback_match in proc_name)
        )
        if not is_match:
            continue

        try:
            proc.terminate()
            terminated.append(proc_name)
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            failed.append(proc_name)
        except Exception:
            failed.append(proc_name)

    if terminated:
        unique = sorted(set(terminated))
        msg = f"Closed '{app_name}' ({len(terminated)} process(es): {', '.join(unique)})."
        if failed:
            msg += f" Could not close {len(failed)} process(es) (access denied)."
        return msg

    if failed:
        return f"Found '{app_name}' but could not close it (access denied). Try running as administrator."

    return f"No running application found matching '{app_name}'."
