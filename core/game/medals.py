"""Medal and game access management"""

import json
from core.config.loader import userConfig
from core.constants import sandboxGamemodes


def getMedalStatus(mapname, gamemode):
    return (
        mapname in userConfig["medals"]
        and gamemode in userConfig["medals"][mapname]
        and userConfig["medals"][mapname][gamemode] == True
    )


def updateMedalStatus(mapname, gamemode, status=True):
    if getMedalStatus(mapname, gamemode) == status:
        return
    if mapname not in userConfig["medals"]:
        userConfig["medals"][mapname] = {}
    if gamemode not in userConfig["medals"][mapname]:
        userConfig["medals"][mapname][gamemode] = False
    userConfig["medals"][mapname][gamemode] = status
    fp = open("userconfig.json", "w")
    fp.write(json.dumps(userConfig, indent=4))
    fp.close()


def canUserAccessGamemode(mapname, gamemode):
    if mapname not in userConfig["medals"]:
        return False
    if gamemode in ["easy", "medium", "hard"]:
        return True
    if getMedalStatus(mapname, gamemode):
        return True
    if (
        (gamemode == "primary_only" and getMedalStatus(mapname, "easy"))
        or (gamemode == "deflation" and getMedalStatus(mapname, "primary_only"))
        or (gamemode == "easy_sandbox" and getMedalStatus(mapname, "easy"))
        or (gamemode == "military_only" and getMedalStatus(mapname, "medium"))
        or (gamemode == "apopalypse" and getMedalStatus(mapname, "military_only"))
        or (gamemode == "reverse" and getMedalStatus(mapname, "medium"))
        or (gamemode == "medium_sandbox" and getMedalStatus(mapname, "reverse"))
        or (gamemode == "hard_sandbox" and getMedalStatus(mapname, "hard"))
        or (gamemode == "magic_monkeys_only" and getMedalStatus(mapname, "hard"))
        or (
            gamemode == "double_hp_moabs"
            and getMedalStatus(mapname, "magic_monkeys_only")
        )
        or (gamemode == "half_cash" and getMedalStatus(mapname, "double_hp_moabs"))
        or (gamemode == "alternate_bloons_rounds" and getMedalStatus(mapname, "hard"))
        or (
            gamemode == "impoppable"
            and getMedalStatus(mapname, "alternate_bloons_rounds")
        )
        or (gamemode == "chimps" and getMedalStatus(mapname, "impoppable"))
    ):
        return True
    return False


def getAvailableSandbox(mapname, restricted_to=None):
    for gamemode in restricted_to if restricted_to is not None else sandboxGamemodes:
        if canUserAccessGamemode(mapname, gamemode):
            return gamemode
    return None
