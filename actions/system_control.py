import ctypes
import subprocess

import pyautogui


def _press(key: str, times: int = 1) -> None:
    for _ in range(max(1, times)):
        pyautogui.press(key)


def _set_brightness(level: int) -> str:
    level = max(0, min(100, level))
    try:
        # WmiMonitorBrightnessMethods works on most laptops/displays
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-Command",
                f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods)"
                f".WmiSetBrightness(1,{level})",
            ],
            check=True,
            capture_output=True,
            timeout=10,
        )
        return f"Set brightness to {level}%."
    except Exception as e:
        return f"Could not change brightness (not supported on this display?): {e}"


def system_control(command: str) -> str:
    """
    Performs a system-level control action on Windows.

    Recognised commands (the parameter is matched case-insensitively):
      - "volume up" / "volume down" / "mute" / "unmute"
      - "set volume <0-100>"  (approximate, via repeated key presses)
      - "play" / "pause" / "next" / "previous"
      - "brightness up" / "brightness down" / "set brightness <0-100>"
      - "lock"
      - "sleep"
      - "shutdown" / "restart"

    Args:
        command: The control instruction (e.g., "volume up", "lock", "shutdown").

    Returns:
        A string message describing what was done.
    """
    if not command or not command.strip():
        return "No system command provided."

    cmd = command.strip().lower()

    try:
        # --- Volume ---
        if cmd in ("mute", "unmute", "toggle mute"):
            _press("volumemute")
            return "Toggled mute."
        if "volume up" in cmd or cmd in ("louder", "increase volume"):
            _press("volumeup", 5)
            return "Increased volume."
        if "volume down" in cmd or cmd in ("quieter", "decrease volume"):
            _press("volumedown", 5)
            return "Decreased volume."
        if cmd.startswith("set volume"):
            digits = "".join(c for c in cmd if c.isdigit())
            target = int(digits) if digits else 50
            target = max(0, min(100, target))
            # Reset to 0 then step up. Each volumeup ~= 2%.
            _press("volumedown", 50)
            _press("volumeup", round(target / 2))
            return f"Set volume to about {target}%."

        # --- Media ---
        if cmd in ("play", "pause", "play/pause", "playpause", "play pause"):
            _press("playpause")
            return "Toggled play/pause."
        if cmd in ("next", "next track", "skip"):
            _press("nexttrack")
            return "Skipped to next track."
        if cmd in ("previous", "prev", "previous track", "back"):
            _press("prevtrack")
            return "Went to previous track."

        # --- Brightness ---
        if cmd.startswith("set brightness"):
            digits = "".join(c for c in cmd if c.isdigit())
            return _set_brightness(int(digits) if digits else 50)
        if "brightness up" in cmd:
            return _set_brightness(100)
        if "brightness down" in cmd:
            return _set_brightness(30)

        # --- Power / session ---
        if cmd == "lock":
            ctypes.windll.user32.LockWorkStation()
            return "Locked the workstation."
        if cmd == "sleep":
            subprocess.run(
                ["rundll32.exe", "powrprof.dll,SetSuspendState", "0", "1", "0"],
                check=False,
            )
            return "Putting the PC to sleep."
        if cmd == "shutdown":
            subprocess.run(["shutdown", "/s", "/t", "30"], check=False)
            return "Shutting down in 30 seconds. Run 'shutdown /a' to cancel."
        if cmd == "restart":
            subprocess.run(["shutdown", "/r", "/t", "30"], check=False)
            return "Restarting in 30 seconds. Run 'shutdown /a' to cancel."
        if cmd in ("cancel shutdown", "abort shutdown", "cancel restart"):
            subprocess.run(["shutdown", "/a"], check=False)
            return "Cancelled any pending shutdown/restart."

        return f"Unknown system command: '{command}'."
    except Exception as e:
        return f"Failed to run system command '{command}': {e}"
