"""Tower-related utilities"""
import numpy as np
from core.config.loader import towers


def getMonkeyUpgradeRequirements(monkeys):
    monkeyUpgradeRequirements = {}
    for monkey in monkeys:
        if monkeys[monkey]["type"] == "hero":
            continue
        if monkeys[monkey]["type"] not in monkeyUpgradeRequirements:
            monkeyUpgradeRequirements[monkeys[monkey]["type"]] = np.array(
                monkeys[monkey]["upgrades"]
            )
        else:
            monkeyUpgradeRequirements[monkeys[monkey]["type"]] = np.maximum(
                monkeyUpgradeRequirements[monkeys[monkey]["type"]],
                np.array(monkeys[monkey]["upgrades"]),
            )
    for monkey in monkeyUpgradeRequirements:
        monkeyUpgradeRequirements[monkey] = monkeyUpgradeRequirements[monkey].tolist()
    return monkeyUpgradeRequirements


def monkeyUpgradesToString(upgrades):
    return str(upgrades[0]) + "-" + str(upgrades[1]) + "-" + str(upgrades[2])


def checkForSingleMonkeyGroup(monkeys):
    types = list(
        filter(
            lambda x: x != "-",
            list(
                map(
                    lambda monkey: (
                        towers["monkeys"][monkeys[monkey]["type"]]["type"]
                        if monkeys[monkey]["type"] != "hero"
                        else "-"
                    ),
                    monkeys,
                )
            ),
        )
    )

    if len(set(types)) == 1:
        return types[0]
    else:
        return None


def checkForSingleMonkeyType(monkeys):
    types = list(
        filter(
            lambda x: x != "hero",
            list(map(lambda monkey: monkeys[monkey]["type"], monkeys)),
        )
    )

    if len(set(types)) == 1:
        return types[0]
    else:
        return None
