import numpy as np
from PIL import Image

MAX_SIZE = 2048


def resize_for_sam(image: Image.Image) -> tuple[np.ndarray, tuple[int, int]]:
    original_size = image.size
    image.thumbnail(
        (MAX_SIZE, MAX_SIZE),
        Image.Resampling.LANCZOS,
    )
    resized = np.array(
        image.convert("RGB"),
        dtype=np.uint8,
    )
    return resized, original_size
