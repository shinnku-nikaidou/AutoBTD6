"""Input driver base class - abstract interface for platform-specific input control"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any


class InputDriver(ABC):
    """
    Abstract base class for platform-specific input drivers.

    This interface defines the contract for all input operations needed
    by the BTD6 automation system, allowing different implementations
    for Windows (AHK), macOS, and Linux.
    """

    @abstractmethod
    def send_key(self, key: str, delay: int = 15, duration: int = 30) -> None:
        """
        Send a keyboard key press.

        Args:
            key: Key to send (can be a string key name or int scancode)
            delay: Delay between key down and key up in milliseconds
            duration: Duration to hold the key in milliseconds
        """
        pass

    @abstractmethod
    def click(self, pos: Tuple[int, int]) -> None:
        """
        Click the mouse at the specified position.

        Args:
            pos: (x, y) coordinates to click
        """
        pass

    @abstractmethod
    def move_to(self, pos: Tuple[int, int]) -> None:
        """
        Move the mouse cursor to the specified position.

        Args:
            pos: (x, y) coordinates to move to
        """
        pass

    @abstractmethod
    def is_game_focused(self) -> bool:
        """
        Check if the BTD6 game window is currently focused.

        Returns:
            True if BTD6 window is focused, False otherwise
        """
        pass

    @abstractmethod
    def get_active_window_title(self) -> Optional[str]:
        """
        Get the title of the currently active window.

        Returns:
            Window title string, or None if unable to determine
        """
        pass

    @abstractmethod
    def screenshot(self) -> Any:
        """
        Capture a screenshot of the current screen.

        Returns:
            PIL Image object of the screenshot
        """
        ...
