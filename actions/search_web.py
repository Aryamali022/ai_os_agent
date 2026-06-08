import webbrowser
from urllib.parse import quote_plus


def search_web(query: str) -> str:
    """
    Searches Google for the given query by opening the default browser with a Google search URL.
    Uses urllib.parse.quote_plus for proper URL encoding of special characters.

    Args:
        query: The search query to look up on Google.

    Returns:
        A string message indicating success or failure.
    """
    if not query:
        return "No search query provided."

    try:
        # Build the Google search URL with properly encoded query
        encoded_query = quote_plus(query.strip())
        search_url = f"https://www.google.com/search?q={encoded_query}"

        # Open in default browser safely (no shell injection risk)
        webbrowser.open(search_url)

        return f"Searched Google for '{query}' in your browser."
    except Exception as e:
        return f"Failed to search for '{query}': {e}"
