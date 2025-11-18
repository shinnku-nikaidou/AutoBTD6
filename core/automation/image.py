"""Image processing utilities"""

import cv2
import numpy as np


def cutImage(image, area):
    return np.array(image[area[1] : (area[3] + 1), area[0] : (area[2]) + 1])


def imageAreasEqual(imageA, imageB, area):
    return (cutImage(imageA, area) == cutImage(imageB, area)).all()


def subImgEqualImgArea(img, subImg, area):
    return (cutImage(img, area) == subImg).all()


def findImageInImage(img, subImg):
    result = cv2.matchTemplate(img, subImg, cv2.TM_SQDIFF_NORMED)
    return [cv2.minMaxLoc(result)[i] for i in [0, 2]]
