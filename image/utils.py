from PIL import Image
import numpy as np

MAX_SIZE = 2048

def resize_for_sam(image: Image.Image):
    original_size = image.size
    image.thumbnail(
        (MAX_SIZE, MAX_SIZE),
        Image.Resampling.LANCZOS
    )
    resized = np.array(
        image.convert("RGB"),
        dtype=np.uint8
    )
    return resized, original_size