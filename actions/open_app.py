import time
import pyautogui
from actions.validator import validate_app_opened


def open_app(app_name: str) -> str:
    """
    Opens a Windows application using keyboard automation.
    Simulates: Press Win key -> Type app name -> Press Enter.
    Then validates whether the app actually opened using OCR.
    If the app is not found, it falls back to opening its website in Edge.

    Args:
        app_name: The name of the application to open.

    Returns:
        A string message indicating success or fallback.
    """
    if not app_name:
        return "No application name provided."

    try:
        # Step 1: Press Windows key to open Start Menu search
        pyautogui.press("win")
        time.sleep(0.5)

        # Step 2: Type the application name
        pyautogui.typewrite(app_name.strip(), interval=0.05)
        time.sleep(0.5)

        # Step 3: Press Enter to launch the top result
        pyautogui.press("enter")
        time.sleep(1)

        # Step 4: Validate if the app actually opened using OCR
        is_open = validate_app_opened(app_name)

        if is_open:
            return f"Successfully launched '{app_name}' on your PC."
        else:
            # Close the Start Menu first (press Escape) before falling back
            pyautogui.press("escape")
            time.sleep(0.5)

            # Fallback: open the website version in Edge
            from actions.open_website import open_website
            fallback_result = open_website(app_name)
            return f"App '{app_name}' not found locally. Opened website instead: {fallback_result}"

    except Exception as e:
        return f"Failed to open '{app_name}': {e}"
