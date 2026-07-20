from PIL import Image
from pillow_heif import register_heif_opener
import numpy as np

from image.segmentation import generate_mask
from image.mask import improve_mask
from image.utils import resize_for_sam

register_heif_opener()

def remove_background(
    input_path: str,
    output_path: str
):
    image = Image.open(
        input_path
    ).convert(
        "RGBA"
    )
    original_size = image.size
    sam_image, _ = resize_for_sam(
        image
    )
    mask = generate_mask(
        sam_image
    )
    if mask is None:
        raise Exception(
            "Объект не найден"
        )
    mask = improve_mask(
        mask
    )
    mask_image = Image.fromarray(
        mask
    )
    mask_image = mask_image.resize(
        original_size,
        Image.Resampling.LANCZOS
    )
    mask = np.array(
        mask_image
    )
    result = np.array(
        image
    )
    result[:, :, 3] = mask
    output = Image.fromarray(
        result
    )
    output.save(
        output_path,
        format="PNG"
    )
    return output_path