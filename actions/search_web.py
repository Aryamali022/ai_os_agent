import time
import pyautogui


def search_web(query: str) -> str:
    """
    Opens Microsoft Edge in full screen, navigates to Google,
    and searches the query from Google's search bar.

    Args:
        query: The search query to look up on Google.

    Returns:
        A string message indicating success or failure.
    """
    if not query:
        return "No search query provided."

    try:
        # Step 1: Open Microsoft Edge
        pyautogui.press("win")
        time.sleep(0.5)
        pyautogui.typewrite("edge", interval=0.05)
        time.sleep(0.5)
        pyautogui.press("enter")
        time.sleep(3)

        # Step 2: Make Edge full screen
        pyautogui.press("f11")
        time.sleep(0.5)

        # Step 3: Go to Google
        pyautogui.hotkey("ctrl", "l")
        time.sleep(0.3)
        pyautogui.typewrite("google.com", interval=0.03)
        pyautogui.press("enter")
        time.sleep(3)

        # Step 4: Google's search bar is auto-focused on load, just type
        pyautogui.typewrite(query.strip(), interval=0.03)
        time.sleep(0.3)
        pyautogui.press("enter")

        return f"Searching Google for '{query}' in Microsoft Edge."
    except Exception as e:
        return f"Failed to search for '{query}': {e}"
