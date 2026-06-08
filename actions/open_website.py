import webbrowser


def open_website(url: str) -> str:
    """
    Opens a website URL in the user's default browser safely.
    Uses webbrowser.open() to avoid shell injection risks.

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
        # Open in default browser safely (no shell injection risk)
        webbrowser.open(url)

        return f"Opened '{url}' in your browser."
    except Exception as e:
        return f"Failed to open website '{url}': {e}"
