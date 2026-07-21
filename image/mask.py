import cv2
import numpy as np


def improve_mask(mask: np.ndarray) -> np.ndarray:
    """
    Улучшает границы маски без добавления лишних пикселей.
    """
    mask = mask.astype(np.uint8) * 255
    kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        (3, 3),
    )

    mask = cv2.morphologyEx(
        mask,
        cv2.MORPH_CLOSE,
        kernel,
        iterations=1,
    )
    mask = cv2.GaussianBlur(
        mask,
        (5, 5),
        0,
    )
    _, mask = cv2.threshold(
        mask,
        128,
        255,
        cv2.THRESH_BINARY,
    )
    return mask
