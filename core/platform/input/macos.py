"""macOS input driver using PyAutoGUI and keyboard library"""

from typing import Tuple, Optional
import pyautogui
import subprocess
from .base import InputDriver


class MacOSInputDriver(InputDriver):
    """
    macOS-specific input driver using PyAutoGUI.

    Note: This driver may not work as reliably as the Windows AHK driver
    because BTD6 has strict input detection. PyAutoGUI keystrokes may
    not be recognized by the game on macOS.

    For best results, consider using accessibility APIs or AppleScript,
    but this requires additional setup and permissions.
    """

    def __init__(self):
        """Initialize the macOS driver."""
        # Check if we have accessibility permissions
        self._has_accessibility = self._check_accessibility()
        if not self._has_accessibility:
            print(
                "Warning: macOS accessibility permissions may be required "
                "for input control."
            )

    def send_key(self, key: str, delay: int = 15, duration: int = 30) -> None:
        """
        Send a keyboard key using PyAutoGUI.

        Note: This may not work with BTD6 due to input detection.

        Args:
            key: Key to send (string key name)
            delay: Delay between key presses (not fully supported)
            duration: Key press duration (not fully supported)
        """
        # Convert scancode to key name if needed
        if isinstance(key, int):
            # On macOS, we can't directly use scancodes like AHK
            # This is a limitation of the platform
            print(f"Warning: Scancode {key} not directly supported on macOS")
            return

        # Strip AHK-style formatting if present
        key = key.strip("{}").replace("sc", "")

        # PyAutoGUI press (less reliable than AHK's SendEvent)
        pyautogui.press(key)

    def click(self, pos: Tuple[int, int]) -> None:
        """
        Click the mouse at the specified position.

        Args:
            pos: (x, y) coordinates to click
        """
        pyautogui.click(pos)

    def move_to(self, pos: Tuple[int, int]) -> None:
        """
        Move mouse cursor to the specified position.

        Args:
            pos: (x, y) coordinates to move to
        """
        pyautogui.moveTo(pos)

    def is_game_focused(self) -> bool:
        """
        Check if BTD6 window is currently focused on macOS.

        Uses AppleScript to check the frontmost application.

        Returns:
            True if BTD6 is focused, False otherwise
        """
        try:
            script = (
                'tell application "System Events" to get name of '
                "first application process whose frontmost is true"
            )
            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=1
            )
            app_name = result.stdout.strip()
            return "BloonsTD6" in app_name or "BTD6" in app_name
        except Exception as e:
            print(f"Warning: Could not check active window on macOS: {e}")
            return True  # Assume focused to avoid blocking

    def get_active_window_title(self) -> Optional[str]:
        """
        Get the title of the currently active window on macOS.

        Returns:
            Window title or None if unable to determine
        """
        try:
            script = (
                'tell application "System Events" to get name of '
                "first application process whose frontmost is true"
            )
            result = subprocess.run(
                ["osascript", "-e", script], capture_output=True, text=True, timeout=1
            )
            return result.stdout.strip() if result.returncode == 0 else None
        except Exception:
            return None

    def screenshot(self):
        """
        Capture a screenshot of the current screen.

        Returns:
            PIL Image object
        """
        return pyautogui.screenshot()

    @staticmethod
    def _check_accessibility() -> bool:
        """
        Check if we have accessibility permissions on macOS.

        Returns:
            True if permissions are granted (or can't determine)
        """
        try:
            # Try to get the active window as a permission check
            script = 'tell application "System Events" to get name of first process'
            result = subprocess.run(
                ["osascript", "-e", script],
                capture_output=True,
                text=True,
                timeout=1,
            )
            return result.returncode == 0
        except Exception:
            return True  # Assume we have permissions
