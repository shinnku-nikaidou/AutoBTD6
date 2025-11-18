"""Platform factory - automatically selects the appropriate input driver"""

import platform
from typing import Optional
from .input.base import InputDriver

# Global singleton instance
_input_driver: Optional[InputDriver] = None


def get_input_driver() -> InputDriver:
    """
    Get the input driver for the current platform (singleton pattern).

    This factory automatically detects the operating system and returns
    the appropriate driver implementation:
    - Windows: WindowsInputDriver (using AHK)
    - macOS: MacOSInputDriver (using PyAutoGUI + AppleScript)
    - Linux: LinuxInputDriver (using PyAutoGUI + xdotool)

    Returns:
        Platform-specific InputDriver instance

    Raises:
        RuntimeError: If the platform is not supported
    """
    global _input_driver

    if _input_driver is None:
        system = platform.system()

        if system == "Windows":
            from .input.windows import WindowsInputDriver

            _input_driver = WindowsInputDriver()
        elif system == "Darwin":  # macOS
            from .input.macos import MacOSInputDriver

            _input_driver = MacOSInputDriver()
        elif system == "Linux":
            from .input.linux import LinuxInputDriver

            _input_driver = LinuxInputDriver()
        else:
            raise RuntimeError(
                f"Unsupported platform: {system}. "
                f"Only Windows, macOS, and Linux are supported."
            )

    return _input_driver


def reset_driver() -> None:
    """
    Reset the singleton driver instance.

    This is primarily useful for testing or when you need to
    reinitialize the driver with different settings.
    """
    global _input_driver
    _input_driver = None


def get_platform_name() -> str:
    """
    Get the current platform name.

    Returns:
        Platform name: "Windows", "macOS", or "Linux"
    """
    system = platform.system()
    if system == "Darwin":
        return "macOS"
    return system


def is_windows() -> bool:
    """Check if running on Windows."""
    return platform.system() == "Windows"


def is_macos() -> bool:
    """Check if running on macOS."""
    return platform.system() == "Darwin"


def is_linux() -> bool:
    """Check if running on Linux."""
    return platform.system() == "Linux"
