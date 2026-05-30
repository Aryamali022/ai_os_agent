import subprocess
import time
import pyautogui


def search_web(query: str) -> str:
    """
    Searches Google for the given query by opening Edge directly with a Google search URL.
    This is much more reliable than typing into the browser manually.

    Args:
        query: The search query to look up on Google.

    Returns:
        A string message indicating success or failure.
    """
    if not query:
        return "No search query provided."

    try:
        # Build the Google search URL with the query
        search_url = f"https://www.google.com/search?q={query.strip().replace(' ', '+')}"

        # Open Edge directly with the search URL
        subprocess.Popen(["cmd.exe", "/c", "start", "msedge", search_url])
        time.sleep(2)

        # Make Edge full screen
        pyautogui.press("f11")

        return f"Searched Google for '{query}' in Microsoft Edge."
    except Exception as e:
        return f"Failed to search for '{query}': {e}"
