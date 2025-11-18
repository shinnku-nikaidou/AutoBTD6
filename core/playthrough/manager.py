"""
Playthrough management and selection module.
Handles playthrough discovery, filtering, and compatibility checking.
"""

import os
from os.path import exists
import numpy as np

from core.constants import ValidatedPlaythroughs, sandboxGamemodes
from core.config.loader import maps, gamemodes, userConfig, playthroughStats, towers
from core.game.medals import canUserAccessGamemode
from core.playthrough.parser import (
    parseBTD6InstructionFileName,
    parseBTD6InstructionsFile,
)
from utils.position import getResolutionString


def getAllAvailablePlaythroughs(additionalDirs=[], considerUserConfig=False):
    """Get all available playthroughs from directories."""
    playthroughs = {}
    files = []
    for dir in ["playthroughs", *additionalDirs]:
        if exists(dir):
            files = [*files, *[dir + "/" + x for x in os.listdir(dir)]]

    for filename in files:
        fileConfig = parseBTD6InstructionFileName(filename)
        if considerUserConfig and not canUserUsePlaythrough(
            {"filename": filename, "fileConfig": fileConfig}
        ):
            continue
        if fileConfig["map"] not in playthroughs:
            playthroughs[fileConfig["map"]] = {}
        compatibleGamemodes = listBTD6InstructionsFileCompatability(filename)
        for gamemode in compatibleGamemodes:
            if considerUserConfig and not canUserAccessGamemode(
                fileConfig["map"], gamemode
            ):
                continue
            if gamemode not in playthroughs[fileConfig["map"]]:
                playthroughs[fileConfig["map"]][gamemode] = []
            playthroughs[fileConfig["map"]][gamemode].append(
                {
                    "filename": filename,
                    "fileConfig": fileConfig,
                    "gamemode": gamemode,
                    "isOriginalGamemode": gamemode == fileConfig["gamemode"],
                }
            )

    return playthroughs


def filterAllAvailablePlaythroughs(
    playthroughs,
    monkeyKnowledgeEnabled,
    handlePlaythroughValidation,
    categoryRestriction,
    gamemodeRestriction,
    heroWhitelist=None,
    requiredFlags=None,
    onlyOriginalGamemodes=False,
    resolution=None,
):
    """Filter playthroughs based on various criteria."""
    if resolution is None:
        import pyautogui

        resolution = getResolutionString(pyautogui.size())

    filteredPlaythroughs = {}

    for mapname in playthroughs:
        if categoryRestriction and maps[mapname]["category"] != categoryRestriction:
            continue
        for gamemode in playthroughs[mapname]:
            if gamemodeRestriction and gamemode != gamemodeRestriction:
                continue
            for playthrough in playthroughs[mapname][gamemode]:
                if (
                    playthrough["fileConfig"]["noMK"] == False
                    and monkeyKnowledgeEnabled == False
                ):
                    continue
                if heroWhitelist:
                    mapConfig = parseBTD6InstructionsFile(playthrough["filename"])
                    if "hero" in mapConfig and mapConfig["hero"] not in heroWhitelist:
                        continue
                if requiredFlags and not all(
                    [x in playthrough["fileConfig"] for x in requiredFlags]
                ):
                    continue
                if onlyOriginalGamemodes and not playthrough["isOriginalGamemode"]:
                    continue
                if (
                    handlePlaythroughValidation != ValidatedPlaythroughs.INCLUDE_ALL
                    and (
                        (
                            handlePlaythroughValidation
                            == ValidatedPlaythroughs.EXCLUDE_NON_VALIDATED
                            and (
                                playthrough["filename"] not in playthroughStats
                                or resolution
                                not in playthroughStats[playthrough["filename"]]
                                or "validation_result"
                                not in playthroughStats[playthrough["filename"]][
                                    resolution
                                ]
                                or playthroughStats[playthrough["filename"]][
                                    resolution
                                ]["validation_result"]
                                == False
                            )
                        )
                        or (
                            handlePlaythroughValidation
                            == ValidatedPlaythroughs.EXCLUDE_VALIDATED
                            and (
                                playthrough["filename"] in playthroughStats
                                and resolution
                                in playthroughStats[playthrough["filename"]]
                                and "validation_result"
                                in playthroughStats[playthrough["filename"]][resolution]
                                and playthroughStats[playthrough["filename"]][
                                    resolution
                                ]["validation_result"]
                                == True
                            )
                        )
                    )
                ):
                    continue
                if mapname not in filteredPlaythroughs:
                    filteredPlaythroughs[mapname] = {}
                if gamemode not in filteredPlaythroughs[mapname]:
                    filteredPlaythroughs[mapname][gamemode] = []
                filteredPlaythroughs[mapname][gamemode].append(playthrough)

    return filteredPlaythroughs


def getHighestValuePlaythrough(
    allAvailablePlaythroughs, mapname, playthroughLog, preferNoMK=True
):
    """Find the highest value playthrough for a map."""
    from core.playthrough.stats import getAveragePlaythroughTime, getHadDefeats

    highestValuePlaythrough = None
    highestValuePlaythroughValue = 0
    highestValuePlaythroughTime = -1
    highestValueNoDefeatsPlaythrough = None
    highestValueNoDefeatsPlaythroughValue = 0
    highestValueNoDefeatsPlaythroughTime = 0

    if mapname not in allAvailablePlaythroughs:
        return None

    for gamemode in allAvailablePlaythroughs[mapname]:
        for playthrough in allAvailablePlaythroughs[mapname][gamemode]:
            averageTime = getAveragePlaythroughTime(playthrough)
            if not getHadDefeats(playthrough, playthroughLog):
                if gamemodes[gamemode]["value"] > highestValueNoDefeatsPlaythroughValue:
                    highestValueNoDefeatsPlaythroughValue = gamemodes[gamemode]["value"]
                    highestValueNoDefeatsPlaythrough = playthrough
                    highestValueNoDefeatsPlaythroughTime = averageTime
                elif (
                    preferNoMK
                    and highestValueNoDefeatsPlaythrough["fileConfig"]["noMK"] == False
                    and playthrough["fileConfig"]["noMK"] == True
                ):
                    highestValueNoDefeatsPlaythroughValue = gamemodes[gamemode]["value"]
                    highestValueNoDefeatsPlaythrough = playthrough
                    highestValueNoDefeatsPlaythroughTime = averageTime
                elif (
                    (
                        not preferNoMK
                        or highestValueNoDefeatsPlaythrough["fileConfig"]["noMK"]
                        == playthrough["fileConfig"]["noMK"]
                        or playthrough["fileConfig"]["noMK"] == True
                    )
                    and gamemodes[gamemode]["value"]
                    == highestValueNoDefeatsPlaythroughValue
                    and averageTime != -1
                    and (
                        averageTime < highestValueNoDefeatsPlaythroughTime
                        or highestValueNoDefeatsPlaythroughTime == -1
                    )
                ):
                    highestValueNoDefeatsPlaythroughValue = gamemodes[gamemode]["value"]
                    highestValueNoDefeatsPlaythrough = playthrough
                    highestValueNoDefeatsPlaythroughTime = averageTime
            else:
                if gamemodes[gamemode]["value"] > highestValuePlaythroughValue:
                    highestValuePlaythroughValue = gamemodes[gamemode]["value"]
                    highestValuePlaythrough = playthrough
                    highestValuePlaythroughTime = averageTime
                elif (
                    preferNoMK
                    and highestValuePlaythrough["fileConfig"]["noMK"] == False
                    and playthrough["fileConfig"]["noMK"] == True
                ):
                    highestValuePlaythroughValue = gamemodes[gamemode]["value"]
                    highestValuePlaythrough = playthrough
                    highestValuePlaythroughTime = averageTime
                elif (
                    (
                        not preferNoMK
                        or highestValuePlaythrough["fileConfig"]["noMK"]
                        == playthrough["fileConfig"]["noMK"]
                        or playthrough["fileConfig"]["noMK"] == True
                    )
                    and gamemodes[gamemode]["value"] == highestValuePlaythroughValue
                    and averageTime != -1
                    and (
                        averageTime < highestValuePlaythroughTime
                        or highestValuePlaythroughTime == -1
                    )
                ):
                    highestValuePlaythroughValue = gamemodes[gamemode]["value"]
                    highestValuePlaythrough = playthrough
                    highestValuePlaythroughTime = averageTime

    return highestValueNoDefeatsPlaythrough or highestValuePlaythrough


def listBTD6InstructionsFileCompatability(filename):
    """List all gamemodes compatible with a playthrough file."""
    from core.game.towers import checkForSingleMonkeyGroup

    fileConfig = parseBTD6InstructionFileName(filename)
    mapConfig = parseBTD6InstructionsFile(filename)
    singleMonkeyGroup = checkForSingleMonkeyGroup(mapConfig["monkeys"])

    compatibleGamemodes = []
    if fileConfig["gamemode"] == "chimps":
        compatibleGamemodes = ["hard", "medium", "easy"]
    elif fileConfig["gamemode"] == "hard":
        compatibleGamemodes = ["medium", "easy"]
    elif fileConfig["gamemode"] == "medium":
        compatibleGamemodes = ["easy"]
    elif fileConfig["gamemode"] == "magic_monkeys_only":
        compatibleGamemodes = ["hard", "medium", "easy"]
    elif fileConfig["gamemode"] == "double_hp_moabs":
        compatibleGamemodes = ["hard", "medium", "easy"]
    elif fileConfig["gamemode"] == "half_cash":
        compatibleGamemodes = ["hard", "medium", "easy"]
    elif fileConfig["gamemode"] == "impoppable":
        compatibleGamemodes = ["hard", "medium", "easy"]
    elif fileConfig["gamemode"] == "military_only":
        compatibleGamemodes = ["medium", "easy"]
    elif fileConfig["gamemode"] == "primary_only":
        compatibleGamemodes = ["easy"]

    if (
        fileConfig["gamemode"]
        in ["hard", "double_hp_moabs", "half_cash", "impoppable", "chimps"]
        and singleMonkeyGroup
        and singleMonkeyGroup == "magic"
    ):
        compatibleGamemodes.append("magic_monkeys_only")
    elif (
        fileConfig["gamemode"]
        in ["medium", "hard", "double_hp_moabs", "half_cash", "impoppable", "chimps"]
        and singleMonkeyGroup
        and singleMonkeyGroup == "military"
    ):
        compatibleGamemodes.append("military_only")
    elif (
        fileConfig["gamemode"]
        in [
            "easy",
            "medium",
            "hard",
            "double_hp_moabs",
            "half_cash",
            "impoppable",
            "chimps",
        ]
        and singleMonkeyGroup
        and singleMonkeyGroup == "primary"
    ):
        compatibleGamemodes.append("primary_only")

    compatibleGamemodes.append(fileConfig["gamemode"])

    return compatibleGamemodes


def checkBTD6InstructionsFileCompatability(filename, gamemode):
    """Check if a playthrough file is compatible with a gamemode."""
    return gamemode in listBTD6InstructionsFileCompatability(filename)


def canUserUsePlaythrough(playthrough):
    """Check if user can use a playthrough (unlocked map, hero, etc)."""
    if (
        playthrough["fileConfig"]["map"] not in userConfig["unlocked_maps"]
        or not userConfig["unlocked_maps"][playthrough["fileConfig"]["map"]]
    ):
        return False
    mapConfig = parseBTD6InstructionsFile(playthrough["filename"])
    if "hero" in mapConfig and (
        mapConfig["hero"] not in userConfig["heros"]
        or not userConfig["heros"][mapConfig["hero"]]
    ):
        return False
    return True


def allPlaythroughsToList(playthroughs):
    """Convert playthrough dict to flat list."""
    playthroughList = []
    for mapname in playthroughs:
        for gamemode in playthroughs[mapname]:
            for playthrough in playthroughs[mapname][gamemode]:
                playthroughList.append(playthrough)

    return playthroughList
