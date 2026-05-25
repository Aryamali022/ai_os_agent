import subprocess


def open_app(app_name: str) -> str:
    """
    Opens a Windows application by name.

    Args:
        app_name: The executable name of the application to open.

    Returns:
        A string message indicating success or failure.
    """
    if not app_name:
        return "No application name provided."

    try:
        subprocess.Popen(f"start {app_name.strip()}", shell=True)
        return f"Successfully launched '{app_name}'."
    except Exception as e:
        return f"Failed to open '{app_name}': {e}"
