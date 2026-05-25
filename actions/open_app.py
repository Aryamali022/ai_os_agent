import time
import pyautogui


def open_app(app_name: str) -> str:
    """
    Opens a Windows application using keyboard automation.
    Simulates: Press Win key -> Type app name -> Press Enter.

    Args:
        app_name: The name of the application to open.

    Returns:
        A string message indicating success or failure.
    """
    if not app_name:
        return "No application name provided."

    try:
        # Press Windows key to open Start Menu search
        pyautogui.press("win")
        time.sleep(0.5)

        # Type the application name
        pyautogui.typewrite(app_name.strip(), interval=0.05)
        time.sleep(0.5)

        # Press Enter to launch the top result
        pyautogui.press("enter")

        return f"Successfully launched '{app_name}'."
    except Exception as e:
        return f"Failed to open '{app_name}': {e}"
