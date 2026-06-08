import time
import pyautogui


def open_app(app_name: str) -> str:
    if not app_name or not app_name.strip():
        return "No application name provided."

    name = app_name.strip()

    try:
        # Press Win key to open the Start Menu
        pyautogui.press("win")
        time.sleep(0.8)  # wait for Start Menu to appear

        # Type the app name (typewrite is reliable for plain ASCII)
        pyautogui.typewrite(name, interval=0.05)
        time.sleep(0.8)  # wait for search results to load

        # Press Enter to launch the top result
        pyautogui.press("enter")

        return f"Opened '{name}' via Start Menu."
    except Exception as e:
        return f"Could not open '{name}'. Error: {e}"
