import time
import pyautogui
from actions.validator import validate_app_opened


def open_app(app_name: str) -> str:
    """
    Opens a Windows application using keyboard automation.
    Simulates: Press Win key -> Type app name -> Press Enter.
    Then validates whether the app actually opened.

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
        time.sleep(1)

        # Validate if the app actually opened
        result = validate_app_opened(app_name)

        if result["is_open"]:
            return f"Successfully launched '{app_name}'. Window found: '{result['window_title']}'."
        else:
            return f"Attempted to launch '{app_name}', but could not confirm it opened."

    except Exception as e:
        return f"Failed to open '{app_name}': {e}"
