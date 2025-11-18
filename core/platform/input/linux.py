"""Linux input driver using PyAutoGUI and xdotool/wmctrl"""

from typing import Tuple, Optional
import pyautogui
import subprocess
from .base import InputDriver


class LinuxInputDriver(InputDriver):
    """
    Linux-specific input driver using PyAutoGUI and X11 tools.

    Note: This driver may not work as reliably as the Windows AHK driver
    because BTD6 has strict input detection. Requires xdotool or wmctrl
    for window management.

    Dependencies:
        - xdotool (for window detection)
        - wmctrl (alternative for window detection)
    """

    def __init__(self):
        """Initialize the Linux driver."""
        self._has_xdotool = self._check_command("xdotool")
        self._has_wmctrl = self._check_command("wmctrl")

        if not self._has_xdotool and not self._has_wmctrl:
            print(
                "Warning: xdotool or wmctrl not found. Window detection may not work."
            )
            print("Install with: sudo apt-get install xdotool wmctrl")

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
            print(f"Warning: Scancode {key} not directly supported on Linux")
            return

        # Strip AHK-style formatting if present
        key = key.strip("{}").replace("sc", "")

        # PyAutoGUI press
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
        Check if BTD6 window is currently focused on Linux.

        Uses xdotool or wmctrl to check the active window.

        Returns:
            True if BTD6 is focused, False otherwise
        """
        title = self.get_active_window_title()
        if title:
            return "BloonsTD6" in title or "BTD6" in title
        return True  # Assume focused if we can't determine

    def get_active_window_title(self) -> Optional[str]:
        """
        Get the title of the currently active window on Linux.

        Returns:
            Window title or None if unable to determine
        """
        # Try xdotool first
        if self._has_xdotool:
            try:
                result = subprocess.run(
                    ["xdotool", "getactivewindow", "getwindowname"],
                    capture_output=True,
                    text=True,
                    timeout=1,
                )
                if result.returncode == 0:
                    return result.stdout.strip()
            except Exception:
                pass

        # Fallback to wmctrl
        if self._has_wmctrl:
            try:
                result = subprocess.run(
                    ["wmctrl", "-l"], capture_output=True, text=True, timeout=1
                )
                if result.returncode == 0:
                    # Parse wmctrl output to find active window
                    # Format: window_id desktop hostname title
                    lines = result.stdout.strip().split("\n")
                    if lines:
                        # Get the first window (usually active)
                        parts = lines[0].split(None, 3)
                        if len(parts) >= 4:
                            return parts[3]
            except Exception:
                pass

        return None

    def screenshot(self):
        """
        Capture a screenshot of the current screen.

        Returns:
            PIL Image object
        """
        return pyautogui.screenshot()

    @staticmethod
    def _check_command(command: str) -> bool:
        """
        Check if a command is available on the system.

        Args:
            command: Command name to check

        Returns:
            True if command is available
        """
        try:
            result = subprocess.run(["which", command], capture_output=True, timeout=1)
            return result.returncode == 0
        except Exception:
            return False
