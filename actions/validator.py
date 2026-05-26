import pygetwindow as gw


def validate_app_opened(app_name: str, max_retries: int = 5, delay: float = 1.0) -> dict:
    """
    Validates whether an application window is open by checking window titles.

    Args:
        app_name: The name of the application to look for.
        max_retries: Number of times to check before giving up.
        delay: Seconds to wait between each retry.

    Returns:
        A dict with 'is_open' (bool) and 'window_title' (str) if found.
    """
    import time

    app_lower = app_name.strip().lower()

    for attempt in range(max_retries):
        windows = gw.getAllTitles()
        for title in windows:
            if title and app_lower in title.lower():
                return {"is_open": True, "window_title": title}
        time.sleep(delay)

    return {"is_open": False, "window_title": ""}
