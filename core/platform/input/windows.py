"""Windows input driver using AutoHotkey (AHK)"""

from typing import Tuple, Optional
from ahk import AHK
import pyautogui
from .base import InputDriver


class WindowsInputDriver(InputDriver):
    """
    Windows-specific input driver using AutoHotkey.

    This driver uses AHK's SendEvent mode with scancodes to ensure
    that BTD6 recognizes the input correctly (BTD6 has strict input
    detection that rejects standard PyAutoGUI keystrokes).
    """

    def __init__(self):
        """Initialize the Windows driver with AHK."""
        self._ahk = AHK()

    def send_key(self, key: str, delay: int = 15, duration: int = 30) -> None:
        """
        Send a keyboard key using AHK's SendEvent mode.

        Args:
            key: Key to send (string or int scancode)
            delay: Key delay in milliseconds
            duration: Key press duration in milliseconds
        """
        ahk_key = self._convert_to_scancode(key)
        self._ahk.send(
            ahk_key, key_delay=delay, key_press_duration=duration, send_mode="Event"
        )

    def _convert_to_scancode(self, key) -> str:
        """
        Convert key to AHK scancode format if it's an integer.

        Args:
            key: Key to convert (string or int)

        Returns:
            AHK-formatted key string
        """
        if isinstance(key, int):
            return "{sc" + hex(key).replace("0x", "") + "}"
        return key

    def click(self, pos: Tuple[int, int]) -> None:
        """
        Click the mouse at the specified position.

        Uses PyAutoGUI for mouse control as it's reliable for clicks.

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
        Check if BTD6 window is currently focused.

        Returns:
            True if BTD6 is focused, False otherwise
        """
        active_window = self._ahk.get_active_window()
        if not active_window:
            return False
        return self._is_btd6_window(active_window.title)

    def get_active_window_title(self) -> Optional[str]:
        """
        Get the title of the currently active window.

        Returns:
            Window title or None if unable to determine
        """
        active_window = self._ahk.get_active_window()
        return active_window.title if active_window else None

    def screenshot(self):
        """
        Capture a screenshot of the current screen.

        Returns:
            PIL Image object
        """
        return pyautogui.screenshot()

    @staticmethod
    def _is_btd6_window(title: str) -> bool:
        """
        Check if a window title belongs to BTD6.

        Args:
            title: Window title to check

        Returns:
            True if it's a BTD6 window
        """
        return title in ["BloonsTD6", "BloonsTD6-Epic"]
