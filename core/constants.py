"""Constants and enumerations"""

from enum import Enum


class PlaythroughResult(Enum):
    UNDEFINED = 0
    WIN = 1
    DEFEAT = 2


class ValidatedPlaythroughs(Enum):
    EXCLUDE_NON_VALIDATED = 0
    INCLUDE_ALL = 1
    EXCLUDE_VALIDATED = 2


class Screen(Enum):
    UNKNOWN = 0
    STARTMENU = 1
    MAP_SELECTION = 3
    DIFFICULTY_SELECTION = 4
    GAMEMODE_SELECTION = 5
    HERO_SELECTION = 6
    INGAME = 7
    INGAME_PAUSED = 8
    VICTORY_SUMMARY = 9
    VICTORY = 10
    DEFEAT = 11
    OVERWRITE_SAVE = 12
    LEVELUP = 13
    APOPALYPSE_HINT = 14
    INSTA_GRANTED = 15
    INSTA_CLAIMED = 16
    COLLECTION_CLAIM_CHEST = 17
    BTD6_UNFOCUSED = 18


class State(Enum):
    UNDEFINED = 0
    IDLE = 1
    INGAME = 2
    GOTO_HOME = 3
    GOTO_INGAME = 4
    SELECT_HERO = 5
    FIND_HARDEST_INCREASED_REWARDS_MAP = 6
    MANAGE_OBJECTIVES = 7
    EXIT = 8


class Mode(Enum):
    ERROR = 0
    SINGLE_MAP = 1
    RANDOM_MAP = 2
    CHASE_REWARDS = 3
    DO_ACHIEVEMENTS = 4
    MISSING_MAPS = 5
    XP_FARMING = 6
    MM_FARMING = 7
    MISSING_STATS = 8
    VALIDATE_PLAYTHROUGHS = 9
    VALIDATE_COSTS = 10


# Sandbox game modes
sandboxGamemodes = {
    "easy_sandbox": {"group": "easy"},
    "medium_sandbox": {"group": "medium"},
    "hard_sandbox": {"group": "hard"},
}
