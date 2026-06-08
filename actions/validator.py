import time
import os
import pyautogui


def validate_app_opened(app_name: str, wait_time: int = 3) -> bool:
    """
    Validates if an app was opened by taking a screenshot and using
    Windows built-in OCR to check if the app name is visible on the screen.

    Falls back to pygetwindow title matching if OCR is unavailable.

    Args:
        app_name: The name of the application to check for.
        wait_time: Seconds to wait before taking the screenshot.

    Returns:
        True if the app appears to be open, False otherwise.
    """
    print(f"[Validator] Checking if '{app_name}' is open...")
    time.sleep(wait_time)

    # --- Method 1: OCR-based validation (screenshot + Windows OCR) ---
    try:
        extracted_text = _ocr_screen()
        if extracted_text and app_name.lower() in extracted_text:
            print(f"[Validator] OCR confirmed '{app_name}' is visible on screen.")
            return True
    except Exception as e:
        print(f"[Validator] OCR method failed: {e}. Trying fallback...")

    # --- Method 2: Fallback to window title matching ---
    try:
        import pygetwindow as gw
        windows = gw.getAllTitles()
        for title in windows:
            if app_name.lower() in title.lower():
                print(f"[Validator] Window title match found: '{title}'")
                return True
    except ImportError:
        print("[Validator] pygetwindow not installed. Skipping window title check.")
    except Exception as e:
        print(f"[Validator] Window title check failed: {e}")

    print(f"[Validator] Could not confirm '{app_name}' is open.")
    return False


def _ocr_screen() -> str:
    """
    Takes a screenshot and runs Windows OCR on it.
    Returns all extracted text in lowercase, or empty string on failure.
    """
    import asyncio

    screenshot_path = os.path.abspath("_temp_validator_screenshot.png")

    try:
        # Take screenshot
        pyautogui.screenshot(screenshot_path)

        # Run OCR using Windows SDK
        extracted = asyncio.run(_perform_ocr_async(screenshot_path))
        return extracted
    finally:
        # Always clean up
        if os.path.exists(screenshot_path):
            os.remove(screenshot_path)


async def _perform_ocr_async(image_path: str) -> str:
    """
    Uses the built-in Windows 10/11 OCR engine via winrt.
    Returns extracted text in lowercase.
    """
    from winrt.windows.media.ocr import OcrEngine
    from winrt.windows.globalization import Language
    from winrt.windows.graphics.imaging import BitmapDecoder
    from winrt.windows.storage import StorageFile

    abs_path = os.path.abspath(image_path)

    # Load image file
    file = await StorageFile.get_file_from_path_async(abs_path)
    stream = await file.open_async(0)  # FileAccessMode.Read

    # Decode bitmap
    decoder = await BitmapDecoder.create_async(stream)
    bitmap = await decoder.get_software_bitmap_async()

    # Run OCR (English)
    engine = OcrEngine.try_create_from_language(Language("en-US"))
    result = await engine.recognize_async(bitmap)

    return result.text.lower()
