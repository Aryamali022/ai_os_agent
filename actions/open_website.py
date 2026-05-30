import subprocess
import time
import pyautogui


def open_website(url: str) -> str:
    """
    Opens a website URL directly in Microsoft Edge using the command line.
    This is more reliable than keyboard automation for URL navigation.

    Args:
        url: The website URL to open (e.g., 'youtube.com').

    Returns:
        A string message indicating success or failure.
    """
    if not url:
        return "No website URL provided."

    url = url.strip()

    # Ensure the URL has a proper prefix
    if not url.startswith("http://") and not url.startswith("https://"):
        # If the LLM just gave the name (like 'youtube'), append .com
        if "." not in url:
            url = url + ".com"
        url = "https://" + url

    try:
        # Open Edge directly with the URL via command line (most reliable method)
        subprocess.Popen(["cmd.exe", "/c", "start", "msedge", url])
        time.sleep(2)

        # Make Edge full screen
        pyautogui.press("f11")

        return f"Opened '{url}' in Microsoft Edge."
    except Exception as e:
        return f"Failed to open website '{url}': {e}"
