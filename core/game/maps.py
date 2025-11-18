"""Map-related utilities"""

import math
from core.config.loader import maps, imageAreas
from core.config.manager import mapsByPos


def mapnameToKeyname(mapname):
    return (
        "".join([(x if x not in ["'", "#"] else "") for x in mapname])
        .replace(" ", "_")
        .lower()
    )


def mapsByCategoryToMaplist(mapsByCategory, maps):
    newMaps = {}
    for category in mapsByCategory:
        currentPos = 0
        currentPage = 0
        for mapname in mapsByCategory[category]:
            newMaps[mapname] = {
                "category": category,
                "name": maps[mapname]["name"],
                "page": currentPage,
                "pos": currentPos,
            }
            currentPos += 1
            if currentPos >= 6:
                currentPos = 0
                currentPage += 1
    return newMaps


def findMapForPxPos(category, page, pxpos):
    if category not in mapsByPos or page not in mapsByPos[category]:
        return None
    bestFind = None
    bestFindDist = 100000
    for iTmp in mapsByPos[category][page]:
        mapname = mapsByPos[category][page][iTmp]
        pos = imageAreas["click"]["map_positions"][maps[mapname]["pos"]]
        if pos[0] < pxpos[0] and pos[1] < pxpos[1]:
            dist = math.dist(pos, pxpos)
            if dist < bestFindDist:
                bestFind = mapname
                bestFindDist = dist
    return bestFind


def getGamemodePosition(gamemode):
    """Get the position for a gamemode, resolving aliases"""
    while not isinstance(imageAreas["click"]["gamemode_positions"][gamemode], list):
        gamemode = imageAreas["click"]["gamemode_positions"][gamemode]
    return imageAreas["click"]["gamemode_positions"][gamemode]
