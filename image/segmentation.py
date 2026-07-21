from pathlib import Path

import numpy as np
import torch

from segment_anything import (
    SamPredictor,
    sam_model_registry,
)

MODEL_PATH = (
    Path(__file__)
    .parent
    .parent
    / "models"
    / "sam_vit_b_01ec64.pth"
)

DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"

sam = sam_model_registry["vit_b"](checkpoint=str(MODEL_PATH))
sam.to(device=DEVICE)

predictor = SamPredictor(sam)


def generate_mask(image: np.ndarray) -> np.ndarray:
    image = image.astype(np.uint8)
    predictor.set_image(image)

    height, width = image.shape[:2]
    box = np.array(
        [
            width * 0.1,
            height * 0.05,
            width * 0.9,
            height * 0.95,
        ]
    )
    points = np.array(
        [
            [width * 0.5, height * 0.5],
            [width * 0.35, height * 0.5],
            [width * 0.65, height * 0.5],
            [width * 0.5, height * 0.3],
            [width * 0.5, height * 0.7],
        ]
    )
    labels = np.ones(len(points), dtype=np.int64)

    masks, scores, _ = predictor.predict(
        point_coords=points,
        point_labels=labels,
        box=box,
        multimask_output=True,
    )
    return masks[np.argmax(scores)]
