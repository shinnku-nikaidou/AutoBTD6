"""Input control utilities"""

from ahk import AHK

# Lazy initialization to avoid errors when AHK is not installed
_ahk_instance = None


class _AHKProxy:
    """Proxy to lazily initialize AHK."""

    def __getattr__(self, name):
        global _ahk_instance
        if _ahk_instance is None:
            _ahk_instance = AHK()
        return getattr(_ahk_instance, name)


ahk = _AHKProxy()


def keyToAHK(x):
    return "{sc" + hex(x).replace("0x", "") + "}" if type(x) == type(int()) else x


def sendKey(key):
    ahk.send(keyToAHK(key), key_delay=15, key_press_duration=30, send_mode="Event")
