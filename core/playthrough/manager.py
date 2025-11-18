"""
Playthrough management and selection module.
Handles playthrough discovery, filtering, and compatibility checking.
"""

import os
from os.path import exists
import numpy as np

from core.constants import ValidatedPlaythroughs
from core.config.loader import maps, gamemodes, userConfig, playthroughStats
from core.game.medals import canUserAccessGamemode
from core.playthrough.parser import (
    parseBTD6InstructionFileName,
    parseBTD6InstructionsFile,
)
from utils.position import getResolutionString


def getAllAvailablePlaythroughs(additionalDirs=[], considerUserConfig=False):
    """
    Scan directories and collect all available playthrough files.

    This function recursively searches for .btd6 playthrough files in the default
    'playthroughs' directory and any additional directories specified. It parses
    each file's metadata and organizes them by map and gamemode.

    Args:
        additionalDirs: List of additional directory paths to search for playthroughs
        considerUserConfig: If True, only include playthroughs that the user can
                           actually use (based on unlocked maps, heroes, etc.)

    Returns:
        Dict structured as: {mapname: {gamemode: [playthrough_objects]}}
        Each playthrough object contains:
        - filename: Path to the .btd6 file
        - fileConfig: Parsed metadata from filename
        - gamemode: The gamemode this playthrough can be used for
        - isOriginalGamemode: True if this is the original gamemode for the file
    """
    playthroughs = {}
    files = []
    for dir in ["playthroughs", *additionalDirs]:
        if exists(dir):
            files = [*files, *[dir + "/" + x for x in os.listdir(dir)]]

    for filename in files:
        # Parse the filename to extract map, gamemode, resolution, and flags
        fileConfig = parseBTD6InstructionFileName(filename)
        if fileConfig is None:
            # Skip files with invalid naming format
            continue
        # Check if user has access to this playthrough (unlocked map/hero)
        if considerUserConfig and not canUserUsePlaythrough(
            {"filename": filename, "fileConfig": fileConfig}
        ):
            continue

        # Initialize map entry if not exists
        if fileConfig["map"] not in playthroughs:
            playthroughs[fileConfig["map"]] = {}

        # Determine which gamemodes this playthrough is compatible with
        # (e.g., a CHIMPS strategy can also work for Hard, Medium, Easy)
        compatibleGamemodes = listBTD6InstructionsFileCompatability(filename)
        for gamemode in compatibleGamemodes:
            # Check if user has unlocked this gamemode for this map
            if considerUserConfig and not canUserAccessGamemode(
                fileConfig["map"], gamemode
            ):
                continue

            # Initialize gamemode entry if not exists
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
    """
    Filter playthroughs based on multiple criteria.

    This is the main filtering function that applies various restrictions to
    narrow down the list of usable playthroughs based on user preferences,
    game state, and validation status.

    Args:
        playthroughs: Dict of playthroughs from getAllAvailablePlaythroughs()
        monkeyKnowledgeEnabled: Whether Monkey Knowledge is enabled
        handlePlaythroughValidation: How to handle validated/unvalidated playthroughs
                                    (INCLUDE_ALL, EXCLUDE_NON_VALIDATED, EXCLUDE_VALIDATED)
        categoryRestriction: Only include maps from this category (e.g., 'beginner', 'expert')
        gamemodeRestriction: Only include this specific gamemode
        heroWhitelist: List of allowed hero names (None = allow all)
        requiredFlags: List of required flags in fileConfig (e.g., ['noMK', 'noLL'])
        onlyOriginalGamemodes: If True, only include playthroughs used for their
                              original gamemode (not cross-compatible ones)
        resolution: Screen resolution to check validation status against

    Returns:
        Dict with same structure as input, but filtered
    """
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
                # Skip if playthrough requires MK but MK is disabled
                if (
                    playthrough["fileConfig"]["noMK"] == False
                    and monkeyKnowledgeEnabled == False
                ):
                    continue

                # Check hero restrictions
                if heroWhitelist:
                    mapConfig = parseBTD6InstructionsFile(playthrough["filename"])
                    if "hero" in mapConfig and mapConfig["hero"] not in heroWhitelist:
                        continue

                # Check if playthrough has all required flags (e.g., noMK, noLL)
                if requiredFlags and not all(
                    [x in playthrough["fileConfig"] for x in requiredFlags]
                ):
                    continue

                # Skip cross-compatible playthroughs if only originals are wanted
                if onlyOriginalGamemodes and not playthrough["isOriginalGamemode"]:
                    continue

                # Handle validation status filtering
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
    """
    Select the best playthrough for a given map based on multiple criteria.

    This function implements a sophisticated selection algorithm that prioritizes:
    1. Playthroughs without defeats (more reliable)
    2. Higher value gamemodes (CHIMPS > Hard > Medium > Easy)
    3. Playthroughs without Monkey Knowledge (noMK) if preferNoMK is True
    4. Faster completion times (as tiebreaker)

    The algorithm maintains two separate candidates:
    - highestValueNoDefeatsPlaythrough: Best playthrough with 100% success rate
    - highestValuePlaythrough: Best playthrough overall (fallback if no perfect ones)

    Args:
        allAvailablePlaythroughs: Dict of all available playthroughs
        mapname: Name of the map to find playthrough for
        playthroughLog: Historical log of playthrough attempts and results
        preferNoMK: If True, prefer playthroughs that don't require Monkey Knowledge

    Returns:
        Best playthrough object, or None if no playthroughs available for this map
    """
    from core.playthrough.stats import getAveragePlaythroughTime, getHadDefeats

    # Track best playthrough overall (may have defeats)
    highestValuePlaythrough = None
    highestValuePlaythroughValue = 0
    highestValuePlaythroughTime = -1

    # Track best playthrough without defeats (most reliable)
    highestValueNoDefeatsPlaythrough = None
    highestValueNoDefeatsPlaythroughValue = 0
    highestValueNoDefeatsPlaythroughTime = 0

    if mapname not in allAvailablePlaythroughs:
        return None

    for gamemode in allAvailablePlaythroughs[mapname]:
        for playthrough in allAvailablePlaythroughs[mapname][gamemode]:
            averageTime = getAveragePlaythroughTime(playthrough)

            # Branch 1: Handle playthroughs with perfect record (no defeats)
            if not getHadDefeats(playthrough, playthroughLog):
                # Case 1: This gamemode has higher value than current best
                if gamemodes[gamemode]["value"] > highestValueNoDefeatsPlaythroughValue:
                    highestValueNoDefeatsPlaythroughValue = gamemodes[gamemode]["value"]
                    highestValueNoDefeatsPlaythrough = playthrough
                    highestValueNoDefeatsPlaythroughTime = averageTime
                # Case 2: Prefer noMK version if values are equal
                elif (
                    preferNoMK
                    and highestValueNoDefeatsPlaythrough is not None
                    and highestValueNoDefeatsPlaythrough["fileConfig"]["noMK"] == False
                    and playthrough["fileConfig"]["noMK"] == True
                ):
                    highestValueNoDefeatsPlaythroughValue = gamemodes[gamemode]["value"]
                    highestValueNoDefeatsPlaythrough = playthrough
                    highestValueNoDefeatsPlaythroughTime = averageTime
                # Case 3: Same value and MK preference, choose faster one
                elif (
                    highestValueNoDefeatsPlaythrough is not None
                    and (
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

            # Branch 2: Handle playthroughs that have had defeats (less reliable)
            else:
                # Same 3 cases as above, but for the fallback candidate
                if gamemodes[gamemode]["value"] > highestValuePlaythroughValue:
                    highestValuePlaythroughValue = gamemodes[gamemode]["value"]
                    highestValuePlaythrough = playthrough
                    highestValuePlaythroughTime = averageTime
                elif (
                    preferNoMK
                    and highestValuePlaythrough is not None
                    and highestValuePlaythrough["fileConfig"]["noMK"] == False
                    and playthrough["fileConfig"]["noMK"] == True
                ):
                    highestValuePlaythroughValue = gamemodes[gamemode]["value"]
                    highestValuePlaythrough = playthrough
                    highestValuePlaythroughTime = averageTime
                elif (
                    highestValuePlaythrough is not None
                    and (
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

    # Return best playthrough without defeats, or fall back to best overall
    return highestValueNoDefeatsPlaythrough or highestValuePlaythrough


def listBTD6InstructionsFileCompatability(filename):
    """
    Determine which gamemodes a playthrough file is compatible with.

    A playthrough designed for a harder gamemode can often be used for easier ones.
    For example, a CHIMPS strategy (hardest) can work for Hard, Medium, and Easy.
    Additionally, if the playthrough uses only one type of monkey (primary/military/magic),
    it can be used for the corresponding "X_only" gamemodes.

    Compatibility rules:
    - CHIMPS -> Hard, Medium, Easy
    - Hard -> Medium, Easy
    - Medium -> Easy
    - Impoppable/Half Cash/Double HP MOABs/Magic Only -> Hard, Medium, Easy
    - Military Only -> Medium, Easy
    - Primary Only -> Easy

    Plus cross-compatibility for single-monkey-type strategies:
    - Only magic monkeys -> magic_monkeys_only
    - Only military monkeys -> military_only
    - Only primary monkeys -> primary_only

    Args:
        filename: Path to the .btd6 playthrough file

    Returns:
        List of compatible gamemode names (always includes the original gamemode)
    """
    from core.game.towers import checkForSingleMonkeyGroup

    fileConfig = parseBTD6InstructionFileName(filename)
    if fileConfig is None:
        # Invalid filename format, cannot determine compatibility
        return []

    # Parse the full file to check monkey composition
    mapConfig = parseBTD6InstructionsFile(filename)
    # Detect if playthrough uses only one type of monkey (primary/military/magic)
    singleMonkeyGroup = checkForSingleMonkeyGroup(mapConfig["monkeys"])

    compatibleGamemodes = []

    # Determine base compatibility based on original gamemode
    # Harder gamemodes can be used for easier ones
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

    # Add cross-compatibility for single-monkey-type strategies
    # If the strategy only uses magic monkeys and is hard enough,
    # it can be used for magic_monkeys_only gamemode
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

    # Always include the original gamemode
    compatibleGamemodes.append(fileConfig["gamemode"])

    return compatibleGamemodes


def checkBTD6InstructionsFileCompatability(filename, gamemode):
    """
    Check if a specific playthrough file is compatible with a specific gamemode.

    This is a convenience wrapper around listBTD6InstructionsFileCompatability
    that returns a boolean instead of the full list.

    Args:
        filename: Path to the .btd6 playthrough file
        gamemode: Gamemode name to check compatibility for

    Returns:
        True if the playthrough can be used for this gamemode, False otherwise
    """
    return gamemode in listBTD6InstructionsFileCompatability(filename)


def canUserUsePlaythrough(playthrough):
    """
    Check if the user has unlocked all requirements to use this playthrough.

    A playthrough can only be used if:
    1. The user has unlocked the map it's for
    2. The user has unlocked the hero it uses (if any)

    This is used during playthrough discovery to filter out strategies
    that the user cannot execute due to game progression requirements.

    Args:
        playthrough: Playthrough object with 'filename' and 'fileConfig' keys

    Returns:
        True if user can use this playthrough, False otherwise
    """
    # Check if map is unlocked
    if (
        playthrough["fileConfig"]["map"] not in userConfig["unlocked_maps"]
        or not userConfig["unlocked_maps"][playthrough["fileConfig"]["map"]]
    ):
        return False

    # Check if required hero is unlocked
    mapConfig = parseBTD6InstructionsFile(playthrough["filename"])
    if "hero" in mapConfig and (
        mapConfig["hero"] not in userConfig["heros"]
        or not userConfig["heros"][mapConfig["hero"]]
    ):
        return False
    return True


def allPlaythroughsToList(playthroughs):
    """
    Convert nested playthrough dictionary to a flat list.

    Flattens the {mapname: {gamemode: [playthroughs]}} structure
    into a simple list of all playthrough objects.

    Args:
        playthroughs: Nested dict from getAllAvailablePlaythroughs()

    Returns:
        Flat list of all playthrough objects
    """
    playthroughList = []
    for mapname in playthroughs:
        for gamemode in playthroughs[mapname]:
            for playthrough in playthroughs[mapname][gamemode]:
                playthroughList.append(playthrough)

    return playthroughList
