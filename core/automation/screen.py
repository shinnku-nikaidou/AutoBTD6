"""Screen recognition utilities"""

import cv2
import copy
from core.constants import Screen
from core.config.loader import imageAreas
from core.automation.image import cutImage
from core.automation.input import ahk


def isBTD6Window(name):
    return name in ["BloonsTD6", "BloonsTD6-Epic"]


def getIngameOcrSegments(mapConfig):
    segmentCoordinates = copy.deepcopy(imageAreas["ocr_segments"])

    if mapConfig["gamemode"] in ["impoppable", "chimps"]:
        segmentCoordinates["round"] = segmentCoordinates["round_ge100_rounds"]

    return {
        "lives": segmentCoordinates["lives"],
        "mana_lives": segmentCoordinates["mana_lives"],
        "money": segmentCoordinates["money"],
        "round": segmentCoordinates["round"],
    }


def recognizeScreen(img, comparisonImages, ignoreFocus=False):
    screen = Screen.UNKNOWN
    activeWindow = ahk.get_active_window()
    if not ignoreFocus and (not activeWindow or not isBTD6Window(activeWindow.title)):
        screen = Screen.BTD6_UNFOCUSED
    else:
        bestMatchDiff = None
        for screenCfg in [
            (
                Screen.STARTMENU,
                comparisonImages["screens"]["startmenu"],
                imageAreas["compare"]["screens"]["startmenu"],
            ),
            (
                Screen.MAP_SELECTION,
                comparisonImages["screens"]["map_selection"],
                imageAreas["compare"]["screens"]["map_selection"],
            ),
            (
                Screen.DIFFICULTY_SELECTION,
                comparisonImages["screens"]["difficulty_selection"],
                imageAreas["compare"]["screens"]["difficulty_selection"],
            ),
            (
                Screen.GAMEMODE_SELECTION,
                comparisonImages["screens"]["gamemode_selection"],
                imageAreas["compare"]["screens"]["gamemode_selection"],
            ),
            (
                Screen.HERO_SELECTION,
                comparisonImages["screens"]["hero_selection"],
                imageAreas["compare"]["screens"]["hero_selection"],
            ),
            (
                Screen.INGAME,
                comparisonImages["screens"]["ingame"],
                imageAreas["compare"]["screens"]["ingame"],
            ),
            (
                Screen.INGAME_PAUSED,
                comparisonImages["screens"]["ingame_paused"],
                imageAreas["compare"]["screens"]["ingame_paused"],
            ),
            (
                Screen.VICTORY_SUMMARY,
                comparisonImages["screens"]["victory_summary"],
                imageAreas["compare"]["screens"]["victory_summary"],
            ),
            (
                Screen.VICTORY,
                comparisonImages["screens"]["victory"],
                imageAreas["compare"]["screens"]["victory"],
            ),
            (
                Screen.DEFEAT,
                comparisonImages["screens"]["defeat"],
                imageAreas["compare"]["screens"]["defeat"],
            ),
            (
                Screen.OVERWRITE_SAVE,
                comparisonImages["screens"]["overwrite_save"],
                imageAreas["compare"]["screens"]["overwrite_save"],
            ),
            (
                Screen.LEVELUP,
                comparisonImages["screens"]["levelup"],
                imageAreas["compare"]["screens"]["levelup"],
            ),
            (
                Screen.APOPALYPSE_HINT,
                comparisonImages["screens"]["apopalypse_hint"],
                imageAreas["compare"]["screens"]["apopalypse_hint"],
            ),
            (
                Screen.INSTA_GRANTED,
                comparisonImages["screens"]["insta_granted"],
                imageAreas["compare"]["screens"]["insta_granted"],
            ),
            (
                Screen.INSTA_CLAIMED,
                comparisonImages["screens"]["insta_claimed"],
                imageAreas["compare"]["screens"]["insta_claimed"],
            ),
            (
                Screen.COLLECTION_CLAIM_CHEST,
                comparisonImages["screens"]["collection_claim_chest"],
                imageAreas["compare"]["screens"]["collection_claim_chest"],
            ),
        ]:
            diff = cv2.matchTemplate(
                cutImage(img, screenCfg[2]),
                cutImage(screenCfg[1], screenCfg[2]),
                cv2.TM_SQDIFF_NORMED,
            )[0][0]
            if diff < 0.05 and (bestMatchDiff is None or diff < bestMatchDiff):
                bestMatchDiff = diff
                screen = screenCfg[0]
    return screen
