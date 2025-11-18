"""Configuration loader - loads all JSON files"""
import json
import pyautogui
from os.path import exists
from utils.position import getResolutionString, convertPositionsInString

# Global configuration storage
maps = {}
gamemodes = {}
keybinds = {}
towers = {}
allImageAreas = {}
imageAreas = {}
playthroughStats = {}
userConfig = {}
version = 0.0

# Monkey knowledge status
monkeyKnowledgeEnabled = False


def load_all_configs():
    """Load all configuration files"""
    global maps, gamemodes, keybinds, towers, allImageAreas, imageAreas
    global playthroughStats, userConfig, version
    
    # Load version
    with open("version.txt") as fp:
        version = float(fp.read())
    
    # Load JSON configs
    maps = json.load(open("maps.json"))
    gamemodes = json.load(open("gamemodes.json"))
    keybinds = json.load(open("keybinds.json"))
    towers = json.load(open("towers.json"))
    allImageAreas = json.load(open("image_areas.json"))
    
    # Load resolution-specific image areas
    if getResolutionString() in allImageAreas:
        imageAreas = allImageAreas[getResolutionString()]
    else:
        imageAreas = json.loads(
            convertPositionsInString(
                json.dumps(allImageAreas["2560x1440"]), (2560, 1440), pyautogui.size()
            )
        )
    
    # Load playthrough stats
    if exists("playthrough_stats.json"):
        playthroughStats = json.load(open("playthrough_stats.json"))
    
    # Load user config with defaults
    userConfig = {
        "monkey_knowledge": {},
        "heros": {},
        "unlocked_maps": {},
        "unlocked_monkey_upgrades": {},
    }
    if exists("userconfig.json"):
        userConfig = json.load(open("userconfig.json"))


# Load configs on import
load_all_configs()
