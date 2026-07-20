from pathlib import Path

import torch
import numpy as np

from segment_anything import (
    sam_model_registry,
    SamPredictor
)

MODEL_PATH = (
    Path(__file__)
    .parent
    .parent
    / "models"
    / "sam_vit_b_01ec64.pth"
)

if torch.backends.mps.is_available():
    device = "mps"
else:
    device = "cpu"

sam = sam_model_registry["vit_b"](
    checkpoint=str(MODEL_PATH)
)

sam.to(
    device=device
)

predictor = SamPredictor(
    sam
)

def generate_mask(image):
    image = image.astype(
        np.uint8
    )
    predictor.set_image(
        image
    )
    h, w = image.shape[:2]
    box = np.array(
        [
            w * 0.1,
            h * 0.05,
            w * 0.9,
            h * 0.95
        ]
    )
    points = np.array([
        [w * 0.5, h * 0.5],
        [w * 0.35, h * 0.5],
        [w * 0.65, h * 0.5],
        [w * 0.5, h * 0.3],
        [w * 0.5, h * 0.7],
    ])
    labels = np.array([
        1,
        1,
        1,
        1,
        1
    ])
    masks, scores, logits = predictor.predict(
        point_coords=points,
        point_labels=labels,
        box=box,
        multimask_output=True
    )
    best_mask = masks[
        np.argmax(scores)
    ]
    return best_mask