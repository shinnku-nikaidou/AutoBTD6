"""Position and resolution utilities"""
import re
import pyautogui


def getResolutionString(resolution=pyautogui.size()):
    return str(resolution[0]) + "x" + str(resolution[1])


def convertPositionsInString(rawStr, nativeResolution, resolution):
    return re.sub(
        r"(?P<x>\d+), (?P<y>\d+)",
        lambda match: str(
            round(int(match.group("x")) * resolution[0] / nativeResolution[0])
        )
        + ", "
        + str(round(int(match.group("y")) * resolution[1] / nativeResolution[1])),
        rawStr,
    )
