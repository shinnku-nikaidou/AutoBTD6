"""Configuration manager - processes and provides access to configs"""

from core.config.loader import maps, monkeyKnowledgeEnabled, userConfig

# Derived configuration data
mapsByCategory = {}
mapsByPos = {}
categoryPages = {}


def generate_derived_configs():
    """Generate derived configuration data structures"""
    global mapsByCategory, mapsByPos, categoryPages

    # Generate mapsByCategory
    for mapname in maps:
        if maps[mapname]["category"] not in mapsByCategory:
            mapsByCategory[maps[mapname]["category"]] = []
        mapsByCategory[maps[mapname]["category"]].append(mapname)

    # Generate mapsByPos
    for mapname in maps:
        if maps[mapname]["category"] not in mapsByPos:
            mapsByPos[maps[mapname]["category"]] = {}
        if maps[mapname]["page"] not in mapsByPos[maps[mapname]["category"]]:
            mapsByPos[maps[mapname]["category"]][maps[mapname]["page"]] = {}
        mapsByPos[maps[mapname]["category"]][maps[mapname]["page"]][
            maps[mapname]["pos"]
        ] = mapname

    # Generate categoryPages
    for category in mapsByCategory:
        categoryPages[category] = (
            max(map(lambda x: maps[x]["page"], mapsByCategory[category])) + 1
        )


def getMonkeyKnowledgeStatus():
    return monkeyKnowledgeEnabled


def setMonkeyKnowledgeStatus(status):
    global monkeyKnowledgeEnabled
    from core.config import loader

    loader.monkeyKnowledgeEnabled = status
    monkeyKnowledgeEnabled = status


def userHasMonkeyKnowledge(name):
    """Check if user has a specific monkey knowledge unlocked."""
    return (
        monkeyKnowledgeEnabled
        and "monkey_knowledge" in userConfig
        and name in userConfig["monkey_knowledge"]
        and userConfig["monkey_knowledge"][name] == True
    )


def mapsByCategoryToMaplist(mapsByCategory, maps):
    """Convert mapsByCategory to a flat map list with positions."""
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


# Generate derived configs on import
generate_derived_configs()
