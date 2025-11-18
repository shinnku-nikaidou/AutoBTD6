"""
AutoBTD6 Helper Module - Import Aggregator
This file provides backward compatibility by re-exporting all functions from the refactored modules.
"""

# Core imports
from core.constants import PlaythroughResult, ValidatedPlaythroughs, Screen, State, Mode, sandboxGamemodes
from core.config.loader import (
    maps, gamemodes, keybinds, towers, imageAreas, allImageAreas,
    playthroughStats, userConfig, version
)
from core.config.manager import (
    mapsByCategory, mapsByPos, categoryPages,
    monkeyKnowledgeEnabled, setMonkeyKnowledgeStatus, getMonkeyKnowledgeStatus,
    userHasMonkeyKnowledge, mapsByCategoryToMaplist
)
from core.game.costs import adjustPrice, getMonkeySellValue, upgradeRequiresConfirmation
from core.game.towers import getMonkeyUpgradeRequirements, checkForSingleMonkeyGroup, checkForSingleMonkeyType
from core.game.maps import mapnameToKeyname, findMapForPxPos, getGamemodePosition
from core.game.medals import getMedalStatus, updateMedalStatus, canUserAccessGamemode, getAvailableSandbox
from core.automation.image import cutImage, findImageInImage, imageAreasEqual
from core.automation.input import sendKey, keyToAHK, ahk
from core.automation.screen import recognizeScreen, isBTD6Window, getIngameOcrSegments
from core.playthrough.parser import (
    parseBTD6InstructionFileName, getBTD6InstructionsFileNameByConfig,
    writeBTD6InstructionsFile, parseBTD6InstructionsFile, convertBTD6InstructionsFile
)
from core.playthrough.manager import (
    getAllAvailablePlaythroughs, filterAllAvailablePlaythroughs,
    getHighestValuePlaythrough, listBTD6InstructionsFileCompatability,
    checkBTD6InstructionsFileCompatability, canUserUsePlaythrough,
    allPlaythroughsToList
)
from core.playthrough.stats import (
    getHadDefeats, getAveragePlaythroughTime, updatePlaythroughValidationStatus,
    updateStatsFile, monkeyUpgradesToString, getRoundTotalBaseXP,
    getPlaythroughXP, getPlaythroughMonkeyMoney, getPlaythroughXPPerHour,
    getPlaythroughMonkeyMoneyPerHour, sortPlaythroughsByGain,
    sortPlaythroughsByMonkeyMoneyGain, sortPlaythroughsByXPGain, setVersion
)

# Utils imports
from utils.display import customPrint
from utils.position import getResolutionString, convertPositionsInString
from utils.file import tupleToStr

# Set version for stats module
setVersion(version)

# Set pyautogui failsafe from automation.input
import pyautogui
pyautogui.FAILSAFE = False
