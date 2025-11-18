"""Input control utilities - now using platform abstraction layer"""

from core.platform.factory import get_input_driver

# Get the platform-specific input driver (singleton)
_driver = get_input_driver()


def sendKey(key):
    """
    Send a keyboard key using the platform-specific driver.

    This function maintains backward compatibility with the old API
    while using the new platform abstraction layer underneath.

    Args:
        key: Key to send (string or int scancode)
    """
    _driver.send_key(key)


# Backward compatibility: expose the driver as 'ahk' for existing code
# that accesses it directly (e.g., ahk.get_active_window())
class _DriverProxy:
    """
    Proxy to maintain backward compatibility with code that uses 'ahk' directly.

    This allows existing code like:
        ahk.get_active_window()
        ahk.send(...)

    to continue working without modification.
    """

    def get_active_window(self):
        """Get active window (backward compatibility)."""

        class WindowInfo:
            def __init__(self, title):
                self.title = title

        title = _driver.get_active_window_title()
        return WindowInfo(title) if title else None

    def send(self, key, key_delay=15, key_press_duration=30, send_mode="Event"):
        """Send key (backward compatibility)."""
        _driver.send_key(key, delay=key_delay, duration=key_press_duration)


ahk = _DriverProxy()
