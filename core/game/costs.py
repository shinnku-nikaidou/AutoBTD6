"""Cost calculation utilities"""

from core.config.loader import userConfig, towers
from core.config.manager import getMonkeyKnowledgeStatus


def userHasMonkeyKnowledge(name):
    return (
        getMonkeyKnowledgeStatus()
        and "monkey_knowledge" in userConfig
        and name in userConfig["monkey_knowledge"]
        and userConfig["monkey_knowledge"][name] == True
    )


def adjustPrice(
    price, difficulty, gamemode, action=None, monkey=None, discountPercentage=None
):
    discount = (
        int(discountPercentage) / 100
        if discountPercentage and str(discountPercentage).isdigit()
        else 0
    )
    priceReduction = 0
    if gamemode == "impoppable":
        factor = 1.2
    elif difficulty == "easy":
        factor = 0.85
    elif difficulty == "medium":
        factor = 1
    elif difficulty == "hard":
        factor = 1.08
    additionalFactor = 1

    if gamemode != "chimps":
        if (
            monkey
            and monkey["type"] == "hero"
            and action
            and action["action"] == "place"
            and userHasMonkeyKnowledge("hero_favors")
        ):
            additionalFactor = 0.9
        if (
            monkey
            and monkey["type"] == "spike"
            and monkey["name"] == "spike0"
            and action
            and action["action"] == "place"
            and userHasMonkeyKnowledge("first_last_line_of_defense")
        ):
            priceReduction += 150

    return (
        round(price * (1 - discount) * factor * additionalFactor / 5) * 5
        - priceReduction
    )


def getMonkeySellValue(cost):
    return round(cost * 0.7)


def upgradeRequiresConfirmation(monkey, path):
    if "upgrade_confirmation" not in towers["monkeys"][monkey["type"]]:
        return False
    if monkey["upgrades"][path] - 1 == -1:
        return False
    if monkey["upgrades"][path] - 1 >= 5:  # paragons
        return True
    return towers["monkeys"][monkey["type"]]["upgrade_confirmation"][path][
        monkey["upgrades"][path] - 1
    ]
