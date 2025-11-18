"""
Playthrough file parsing and conversion module.
Handles .btd6 file format parsing, writing, and coordinate conversion.
"""

import re
import os
from os.path import exists
import numpy as np

from core.constants import sandboxGamemodes
from core.config.loader import maps, gamemodes, keybinds, towers, imageAreas
from core.game.costs import adjustPrice, getMonkeySellValue, upgradeRequiresConfirmation
from utils.position import getResolutionString, convertPositionsInString
from utils.file import tupleToStr


def parseBTD6InstructionFileName(filename):
    """Parse a .btd6 filename and extract metadata."""
    matches = re.search(
        r"^(?:(?:own_|unvalidated_|unsuccessful_)?playthroughs\/)?(?P<map>\w+)#(?P<gamemode>\w+)#(?P<resolution>(?P<resolution_x>\d+)x(?P<resolution_y>\d+))(?:#(?P<comment>.+))?\.btd6$",
        filename,
    )
    if not matches:
        return None
    matches = matches.groupdict()
    matches["noMK"] = False
    matches["noLL"] = False
    matches["noLLwMK"] = False
    for m in re.finditer(
        r"(?P<noMK>noMK(?:#|$))?(?:(?P<singleType>[a-z]+)Only(?:#|$))?(?P<noLL>noLL(?:#|$))?(?P<noLLwMK>noLLwMK(?:#|$))?(?P<gB>gB(?:#|$))?",
        matches["comment"] if "comment" in matches and matches["comment"] else "",
    ):
        if m.group("noMK"):
            matches["noMK"] = True
        if m.group("noLL"):
            matches["noLL"] = True
        if m.group("noLLwMK"):
            matches["noLLwMK"] = True
        if m.group("gB"):
            matches["gB"] = True
    return matches


def getBTD6InstructionsFileNameByConfig(
    thisConfig, folder="own_playthroughs", resolution=None
):
    """Generate a .btd6 filename from a playthrough config."""
    if resolution is None:
        import pyautogui

        resolution = getResolutionString(pyautogui.size())

    return (
        folder
        + "/"
        + thisConfig["map"]
        + "#"
        + thisConfig["gamemode"]
        + "#"
        + resolution
        + (
            "#" + thisConfig["comment"]
            if "comment" in thisConfig and thisConfig["comment"]
            else ""
        )
        + ".btd6"
    )


def writeBTD6InstructionsFile(thisConfig, folder="own_playthroughs", resolution=None):
    """Write a playthrough config to a .btd6 file."""
    if resolution is None:
        import pyautogui

        resolution = getResolutionString(pyautogui.size())

    filename = getBTD6InstructionsFileNameByConfig(thisConfig, folder, resolution)

    if not exists(folder):
        os.mkdir(folder)

    fp = open(filename, "w")

    for action in thisConfig["steps"]:
        if action["action"] == "place":
            fp.write(
                "place "
                + (thisConfig["hero"] if action["type"] == "hero" else action["type"])
                + " "
                + action["name"]
                + " at "
                + tupleToStr(action["pos"])
                + (
                    " with " + action["discount"] + "% discount"
                    if "discount" in action
                    else ""
                )
                + "\n"
            )
        elif action["action"] == "upgrade":
            fp.write(
                "upgrade "
                + action["name"]
                + " path "
                + str(action["path"])
                + (
                    " with " + action["discount"] + "% discount"
                    if "discount" in action
                    else ""
                )
                + "\n"
            )
        elif action["action"] == "retarget":
            fp.write(
                "retarget "
                + action["name"]
                + (" to " + tupleToStr(action["to"]) if "to" in action else "")
                + "\n"
            )
        elif action["action"] == "special":
            fp.write("special " + action["name"] + "\n")
        elif action["action"] == "sell":
            fp.write("sell " + action["name"] + "\n")
        elif action["action"] == "remove":
            cost = ""
            while True:
                print(
                    "enter cost of obstacle removal at "
                    + tupleToStr(action["pos"])
                    + " >"
                )
                cost = input()
                if len(cost) and cost.isdigit():
                    break
                else:
                    print("non integer provided!")
            fp.write(
                "remove obstacle at "
                + tupleToStr(action["pos"])
                + " for "
                + str(cost)
                + "\n"
            )
        elif action["action"] == "await_round":
            fp.write("round " + str(action["round"]) + "\n")

    fp.close()


def parseBTD6InstructionsFile(filename, targetResolution=None, gamemode=None):
    """Parse a .btd6 file and return the playthrough config."""
    import pyautogui

    if targetResolution is None:
        targetResolution = pyautogui.size()

    fileConfig = parseBTD6InstructionFileName(filename)

    if not fileConfig:
        return None

    sandboxMode = False

    mapname = fileConfig["map"]
    if mapname not in maps:
        print("unknown map: " + str(mapname))
        return None
    gamemode = gamemode if gamemode else fileConfig["gamemode"]
    if gamemode not in gamemodes and gamemode not in sandboxGamemodes:
        print("unknown gamemode: " + str(gamemode))
        return None
    if gamemode in sandboxGamemodes:
        sandboxMode = True
    if not exists(filename):
        print("unknown file: " + str(filename))
        return None

    fp = open(filename, "r")
    rawInputFile = fp.read()
    fp.close()

    if not targetResolution and fileConfig["resolution"] != getResolutionString():
        from utils.display import customPrint

        customPrint(
            "tried parsing playthrough for non native resolution with rescaling disabled!"
        )
        return None
    elif fileConfig["resolution"] != getResolutionString(targetResolution):
        rawInputFile = convertPositionsInString(
            rawInputFile,
            [int(x) for x in fileConfig["resolution"].split("x")],
            targetResolution,
        )

    configLines = rawInputFile.splitlines()

    monkeys = {}

    newMapConfig = {
        "category": maps[mapname]["category"],
        "map": mapname,
        "page": maps[mapname]["page"],
        "pos": maps[mapname]["pos"],
        "difficulty": (
            gamemodes[gamemode]["group"]
            if not sandboxMode
            else sandboxGamemodes[gamemode]["group"]
        ),
        "gamemode": gamemode,
        "steps": [],
        "extrainstructions": 0,
        "filename": filename,
    }

    if (
        gamemode == "deflation"
        or gamemode == "half_cash"
        or gamemode == "impoppable"
        or gamemode == "chimps"
        or gamemode in sandboxGamemodes
    ):
        newMapConfig["steps"].append(
            {
                "action": "click",
                "pos": imageAreas["click"]["gamemode_deflation_message_confirmation"],
                "cost": 0,
            }
        )
        newMapConfig["extrainstructions"] = 1

    for line in configLines:
        matches = re.search(
            r"^(?P<action>place|upgrade|retarget|special|sell|remove|round|speed) ?(?P<type>[a-z_]+)? (?P<name>\w+)(?: (?:(?:at|to) (?P<x>\d+), (?P<y>\d+))?(?:path (?P<path>[0-2]))?)?(?: for (?P<price>\d+|\?\?\?))?(?: with (?P<discount>\d{1,2}|100)% discount)?$",
            line,
        )
        if not matches:
            continue

        newStep = None
        newSteps = []

        if matches.group("action") == "place":
            if monkeys.get(matches.group("name")):
                print(
                    filename
                    + ": monkey "
                    + matches.group("name")
                    + " placed twice! skipping!"
                )
                continue
            if matches.group("type") in towers["monkeys"]:
                newStep = {
                    "action": "place",
                    "type": matches.group("type"),
                    "name": matches.group("name"),
                    "key": keybinds["monkeys"][matches.group("type")],
                    "pos": (int(matches.group("x")), int(matches.group("y"))),
                    "cost": adjustPrice(
                        towers["monkeys"][matches.group("type")]["base"],
                        newMapConfig["difficulty"],
                        gamemode,
                        {"action": "place"},
                        {
                            "type": matches.group("type"),
                            "name": matches.group("name"),
                            "upgrades": [0, 0, 0],
                        },
                        matches.group("discount"),
                    ),
                }
                if matches.group("discount"):
                    newStep["discount"] = matches.group("discount")
                monkeys[matches.group("name")] = {
                    "type": matches.group("type"),
                    "name": matches.group("name"),
                    "upgrades": [0, 0, 0],
                    "pos": (int(matches.group("x")), int(matches.group("y"))),
                    "value": adjustPrice(
                        towers["monkeys"][matches.group("type")]["base"],
                        newMapConfig["difficulty"],
                        gamemode,
                        {"action": "place"},
                        {
                            "type": matches.group("type"),
                            "name": matches.group("name"),
                            "upgrades": [0, 0, 0],
                        },
                        matches.group("discount"),
                    ),
                }
                newSteps.append(newStep)
            elif matches.group("type") in towers["heros"]:
                newStep = {
                    "action": "place",
                    "type": "hero",
                    "name": matches.group("name"),
                    "key": keybinds["monkeys"]["hero"],
                    "pos": (int(matches.group("x")), int(matches.group("y"))),
                    "cost": adjustPrice(
                        towers["heros"][matches.group("type")]["base"],
                        newMapConfig["difficulty"],
                        gamemode,
                        {"action": "place"},
                        {
                            "type": "hero",
                            "name": matches.group("name"),
                            "upgrades": [0, 0, 0],
                        },
                        matches.group("discount"),
                    ),
                }
                if matches.group("discount"):
                    newStep["discount"] = matches.group("discount")
                newMapConfig["hero"] = matches.group("type")
                monkeys[matches.group("name")] = {
                    "type": "hero",
                    "name": matches.group("name"),
                    "upgrades": [0, 0, 0],
                    "pos": (int(matches.group("x")), int(matches.group("y"))),
                    "value": adjustPrice(
                        towers["heros"][matches.group("type")]["base"],
                        newMapConfig["difficulty"],
                        gamemode,
                        {"action": "place"},
                        {
                            "type": "hero",
                            "name": matches.group("name"),
                            "upgrades": [0, 0, 0],
                        },
                        matches.group("discount"),
                    ),
                }
                newSteps.append(newStep)
            else:
                print(
                    filename
                    + ": monkey/hero "
                    + matches.group("name")
                    + " has unknown type: "
                    + matches.group("type")
                    + "! skipping!"
                )
                continue
        elif matches.group("action") == "upgrade":
            if not monkeys.get(matches.group("name")):
                print(
                    filename
                    + ": monkey "
                    + matches.group("name")
                    + " unplaced! skipping!"
                )
                continue
            if monkeys[matches.group("name")]["type"] == "hero":
                print(
                    filename
                    + ": tried to upgrade hero "
                    + matches.group("name")
                    + "! skipping instruction!"
                )
                continue
            monkeyUpgrades = monkeys[matches.group("name")]["upgrades"]
            monkeyUpgrades[int(matches.group("path"))] += 1
            if (
                sum(map(lambda x: x > 2, monkeyUpgrades)) > 1
                or sum(map(lambda x: x > 0, monkeyUpgrades)) > 2
                or monkeyUpgrades[int(matches.group("path"))] > 5
            ):
                print(
                    filename
                    + ": monkey "
                    + matches.group("name")
                    + " has invalid upgrade path! skipping!"
                )
                monkeyUpgrades[int(matches.group("path"))] -= 1
                continue
            newStep = {
                "action": "upgrade",
                "name": matches.group("name"),
                "key": keybinds["path"][str(matches.group("path"))],
                "pos": monkeys[matches.group("name")]["pos"],
                "path": int(matches.group("path")),
                "cost": adjustPrice(
                    towers["monkeys"][monkeys[matches.group("name")]["type"]][
                        "upgrades"
                    ][int(matches.group("path"))][
                        monkeyUpgrades[int(matches.group("path"))] - 1
                    ],
                    newMapConfig["difficulty"],
                    gamemode,
                    {"action": "upgrade", "path": int(matches.group("path"))},
                    monkeys[matches.group("name")],
                    matches.group("discount"),
                ),
            }
            if matches.group("discount"):
                newStep["discount"] = matches.group("discount")
            monkeys[matches.group("name")]["value"] += adjustPrice(
                towers["monkeys"][monkeys[matches.group("name")]["type"]]["upgrades"][
                    int(matches.group("path"))
                ][monkeyUpgrades[int(matches.group("path"))] - 1],
                newMapConfig["difficulty"],
                gamemode,
                {"action": "upgrade", "path": int(matches.group("path"))},
                monkeys[matches.group("name")],
                matches.group("discount"),
            )
            newSteps.append(newStep)
            if upgradeRequiresConfirmation(
                monkeys[matches.group("name")], int(matches.group("path"))
            ):
                newSteps.append(
                    {
                        "action": "click",
                        "name": matches.group("name"),
                        "pos": imageAreas["click"]["paragon_message_confirmation"],
                        "cost": 0,
                    }
                )
        elif matches.group("action") == "retarget":
            if not monkeys.get(matches.group("name")):
                print(
                    filename
                    + ": monkey "
                    + matches.group("name")
                    + " unplaced! skipping!"
                )
                continue
            newStep = {
                "action": "retarget",
                "name": matches.group("name"),
                "key": keybinds["others"]["retarget"],
                "pos": monkeys[matches.group("name")]["pos"],
                "cost": 0,
            }
            if matches.group("x"):
                newStep["to"] = (int(matches.group("x")), int(matches.group("y")))
            elif monkeys[matches.group("name")]["type"] == "mortar":
                print("mortar can only be retargeted to a position! skipping!")
                continue
            newSteps.append(newStep)
        elif matches.group("action") == "special":
            if not monkeys.get(matches.group("name")):
                print(
                    filename
                    + ": monkey "
                    + matches.group("name")
                    + " unplaced! skipping!"
                )
                continue
            newStep = {
                "action": "special",
                "name": matches.group("name"),
                "key": keybinds["others"]["special"],
                "pos": monkeys[matches.group("name")]["pos"],
                "cost": 0,
            }
            newSteps.append(newStep)
        elif matches.group("action") == "sell":
            if not monkeys.get(matches.group("name")):
                print(
                    filename
                    + ": monkey "
                    + matches.group("name")
                    + " unplaced! skipping!"
                )
                continue
            newStep = {
                "action": "sell",
                "name": matches.group("name"),
                "key": keybinds["others"]["sell"],
                "pos": monkeys[matches.group("name")]["pos"],
                "cost": -getMonkeySellValue(monkeys[matches.group("name")]["value"]),
            }
            newSteps.append(newStep)
        elif matches.group("action") == "remove":
            if matches.group("price") == "???":
                print("remove obstacle without price specified: " + line)
                continue
            newStep = {
                "action": "remove",
                "pos": (int(matches.group("x")), int(matches.group("y"))),
                "cost": int(matches.group("price")),
            }
            newSteps.append(newStep)
        elif matches.group("action") == "round":
            try:
                if int(matches.group("name")) < 1:
                    print(f"Invalid round {matches.group('name')}, skipping!")
                    continue
            except ValueError:
                print(f"NaN round {matches.group('name')}, skipping!")
            newStep = {
                "action": "await_round",
                "round": int(matches.group("name")),
                "cost": 0,
            }
            newSteps.append(newStep)
        elif matches.group("action") == "speed":
            newStep = {
                "action": "speed",
                "speed": matches.group("name"),
                "cost": 0,
            }
            newSteps.append(newStep)

        if len(newSteps):
            newMapConfig["steps"] += newSteps

    newMapConfig["monkeys"] = monkeys
    return newMapConfig


def convertBTD6InstructionsFile(filename, targetResolution):
    """Read a playthrough file, convert it, and save under the same name (except resolution)."""
    fileConfig = parseBTD6InstructionFileName(filename)
    if not fileConfig:
        return False
    if not exists(filename):
        return False

    newFileName = getBTD6InstructionsFileNameByConfig(
        fileConfig, resolution=getResolutionString(targetResolution)
    )

    if exists(newFileName):
        return False

    fp = open(filename, "r")
    rawInputFile = fp.read()
    fp.close()

    output = convertPositionsInString(
        rawInputFile,
        [int(x) for x in fileConfig["resolution"].split("x")],
        targetResolution,
    )

    fp = open(newFileName, "w")
    fp.write(output)
    fp.close()

    return True
