"""
Playthrough statistics and XP/MM calculation module.
Handles playthrough stats tracking, XP gain, and monkey money calculations.
"""

import json
import numpy as np

from core.constants import PlaythroughResult
from core.config.loader import playthroughStats, gamemodes, maps
from utils.position import getResolutionString

# Global version variable (imported from helper.py context)
version = None


def setVersion(v):
    """Set the version string for stats tracking."""
    global version
    version = v


def getHadDefeats(playthrough, playthroughLog):
    """Check if a playthrough has had defeats."""
    if (
        playthrough["filename"] not in playthroughLog
        or playthrough["gamemode"] not in playthroughLog[playthrough["filename"]]
    ):
        return False
    return (
        playthroughLog[playthrough["filename"]][playthrough["gamemode"]]["defeats"] > 0
    )


def getAveragePlaythroughTime(playthrough):
    """Get average time for a playthrough."""
    if playthrough["filename"] not in playthroughStats:
        return -1

    times = []
    for resolution in playthroughStats[playthrough["filename"]]:
        if not __import__("re").search(r"\d+x\d+", resolution):
            continue
        if (
            playthrough["gamemode"]
            in playthroughStats[playthrough["filename"]][resolution]
        ):
            times = [
                *times,
                *playthroughStats[playthrough["filename"]][resolution][
                    playthrough["gamemode"]
                ]["win_times"],
            ]
    return np.average(times or [-1])


def updatePlaythroughValidationStatus(
    playthroughFile, validationStatus, resolution=None
):
    """Update validation status for a playthrough."""
    global playthroughStats

    if resolution is None:
        import pyautogui

        resolution = getResolutionString(pyautogui.size())

    if playthroughFile not in playthroughStats:
        playthroughStats[playthroughFile] = {}
    if resolution not in playthroughStats[playthroughFile]:
        playthroughStats[playthroughFile][resolution] = {"validation_result": False}

    playthroughStats[playthroughFile][resolution]["validation_result"] = (
        validationStatus
    )

    fp = open("playthrough_stats.json", "w")
    fp.write(json.dumps(playthroughStats, indent=4))
    fp.close()


def updateStatsFile(playthroughFile, thisPlaythroughStats, resolution=None):
    """Update stats file with new playthrough results."""
    global playthroughStats

    if resolution is None:
        import pyautogui

        resolution = getResolutionString(pyautogui.size())

    if playthroughFile not in playthroughStats:
        playthroughStats[playthroughFile] = {}
    if resolution not in playthroughStats[playthroughFile]:
        playthroughStats[playthroughFile][resolution] = {"validation_result": False}
    if (
        thisPlaythroughStats["gamemode"]
        not in playthroughStats[playthroughFile][resolution]
    ):
        playthroughStats[playthroughFile][resolution][
            thisPlaythroughStats["gamemode"]
        ] = {"attempts": 0, "wins": 0, "win_times": []}

    if thisPlaythroughStats["result"] == PlaythroughResult.WIN:
        playthroughStats[playthroughFile][resolution][thisPlaythroughStats["gamemode"]][
            "attempts"
        ] += 1
        playthroughStats[playthroughFile][resolution][thisPlaythroughStats["gamemode"]][
            "wins"
        ] += 1
        playthroughStats[playthroughFile]["version"] = version
        totalTime = 0
        lastStart = -1
        for stateChange in thisPlaythroughStats["time"]:
            if stateChange[0] == "start" and lastStart == -1:
                lastStart = stateChange[1]
            elif stateChange[0] == "stop" and lastStart != -1:
                totalTime += stateChange[1] - lastStart
                lastStart = -1
        playthroughStats[playthroughFile][resolution][thisPlaythroughStats["gamemode"]][
            "win_times"
        ].append(totalTime)
    else:
        playthroughStats[playthroughFile][resolution][thisPlaythroughStats["gamemode"]][
            "attempts"
        ] += 1

    fp = open("playthrough_stats.json", "w")
    fp.write(json.dumps(playthroughStats, indent=4))
    fp.close()


def monkeyUpgradesToString(upgrades):
    """Convert upgrade array to string format."""
    return str(upgrades[0]) + "-" + str(upgrades[1]) + "-" + str(upgrades[2])


# XP and Monkey Money calculation functions


def getRoundTotalBaseXP(round):
    """Calculate total base XP for completing up to a given round."""
    if round < 0:
        return 0
    xp = (min(round + 1, 21) ** 2 + min(round + 1, 21)) / 2 * 20
    if round > 20:
        xp += (min(round - 20, 30)) * 21 * 20 + (
            min(round - 20, 30) ** 2 + min(round - 20, 30)
        ) / 2 * 40
        if round > 50:
            xp += (min(round - 50, 50)) * (21 * 20 + 30 * 40) + (
                min(round - 50, 50) ** 2 + min(round - 50, 50)
            ) / 2 * 90
    return xp


def getPlaythroughXP(gamemode, mapcategory):
    """Calculate XP gained from completing a playthrough."""
    xp = 0

    if gamemode in ["easy", "primary_only"]:
        xp = getRoundTotalBaseXP(40) - getRoundTotalBaseXP(0)
    elif gamemode in ["deflation"]:
        xp = getRoundTotalBaseXP(60) - getRoundTotalBaseXP(30)
    elif gamemode in ["medium", "military_only", "reverse", "apopalypse"]:
        xp = getRoundTotalBaseXP(60) - getRoundTotalBaseXP(0)
    elif gamemode in [
        "hard",
        "magic_monkeys_only",
        "double_hp_moabs",
        "half_cash",
        "alternate_bloons_rounds",
    ]:
        xp = getRoundTotalBaseXP(80) - getRoundTotalBaseXP(2)
    elif gamemode in ["impoppable", "chimps"]:
        xp = getRoundTotalBaseXP(100) - getRoundTotalBaseXP(5)

    if mapcategory == "intermediate":
        xp = xp * 1.1
    elif mapcategory == "advanced":
        xp = xp * 1.2
    elif mapcategory == "expert":
        xp = xp * 1.3
    return xp


def getPlaythroughMonkeyMoney(gamemode, mapcategory):
    """Calculate Monkey Money gained from completing a playthrough."""
    if gamemode not in gamemodes:
        return 0

    replayMonkeyMoney = {
        "easy": {"beginner": 15, "intermediate": 30, "advanced": 45, "expert": 60},
        "medium": {"beginner": 25, "intermediate": 50, "advanced": 75, "expert": 100},
        "hard": {"beginner": 40, "intermediate": 80, "advanced": 120, "expert": 160},
        "impoppable": {
            "beginner": 60,
            "intermediate": 120,
            "advanced": 180,
            "expert": 240,
        },
    }

    if mapcategory not in replayMonkeyMoney["easy"]:
        return 0

    return replayMonkeyMoney[gamemodes[gamemode]["cash_group"]][mapcategory]


def getPlaythroughXPPerHour(playthrough):
    """Calculate XP gain per hour for a playthrough."""
    averageTime = getAveragePlaythroughTime(playthrough)
    if averageTime == -1:
        return 0
    return (
        3600
        / averageTime
        * getPlaythroughXP(
            playthrough["gamemode"], maps[playthrough["fileConfig"]["map"]]["category"]
        )
    )


def getPlaythroughMonkeyMoneyPerHour(playthrough):
    """Calculate Monkey Money gain per hour for a playthrough."""
    averageTime = getAveragePlaythroughTime(playthrough)
    if averageTime == -1:
        return 0
    return (
        3600
        / averageTime
        * getPlaythroughMonkeyMoney(
            playthrough["gamemode"], maps[playthrough["fileConfig"]["map"]]["category"]
        )
    )


def sortPlaythroughsByGain(playthroughs, gainFunc):
    """Sort playthroughs by a gain function."""
    return sorted(
        map(lambda x: {**x, "value": gainFunc(x)}, playthroughs),
        key=lambda x: x["value"],
        reverse=True,
    )


def sortPlaythroughsByMonkeyMoneyGain(playthroughs):
    """Sort playthroughs by Monkey Money gain per hour."""
    return sortPlaythroughsByGain(playthroughs, getPlaythroughMonkeyMoneyPerHour)


def sortPlaythroughsByXPGain(playthroughs):
    """Sort playthroughs by XP gain per hour."""
    return sortPlaythroughsByGain(playthroughs, getPlaythroughXPPerHour)
