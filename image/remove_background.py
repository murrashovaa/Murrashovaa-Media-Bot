import os
import tempfile
from functools import lru_cache
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter, ImageOps
from pillow_heif import register_heif_opener

from config.settings import STORAGE_PATH

NUMBA_CACHE_DIR = Path(
    os.getenv("NUMBA_CACHE_DIR") or Path(STORAGE_PATH, "numba_cache")
).expanduser()

try:
    NUMBA_CACHE_DIR.mkdir(parents=True, exist_ok=True)
except OSError:
    NUMBA_CACHE_DIR = Path(tempfile.gettempdir(), "media_bot_numba_cache")
    NUMBA_CACHE_DIR.mkdir(parents=True, exist_ok=True)

os.environ["NUMBA_CACHE_DIR"] = str(NUMBA_CACHE_DIR.resolve())

from rembg import new_session, remove  # noqa: E402

register_heif_opener()

DEFAULT_MODEL = "isnet-general-use"
ALPHA_FOREGROUND_THRESHOLD = 240
ALPHA_BACKGROUND_THRESHOLD = 10
ALPHA_ERODE_SIZE = 8


def remove_background(
    input_path: str,
    output_path: str,
) -> str:
    image = open_image(input_path)

    try:
        result = remove_with_rembg(image)
    except Exception as rembg_error:
        try:
            result = remove_with_sam(image)
        except Exception as fallback_error:
            raise RuntimeError("Не удалось качественно удалить фон.") from (
                fallback_error or rembg_error
            )

    result.save(output_path, format="PNG", optimize=True)
    return output_path


def open_image(input_path: str) -> Image.Image:
    image = Image.open(input_path)
    image = ImageOps.exif_transpose(image)
    return image.convert("RGBA")


def remove_with_rembg(image: Image.Image) -> Image.Image:
    result = remove(
        image,
        session=get_rembg_session(),
        alpha_matting=True,
        alpha_matting_foreground_threshold=ALPHA_FOREGROUND_THRESHOLD,
        alpha_matting_background_threshold=ALPHA_BACKGROUND_THRESHOLD,
        alpha_matting_erode_size=ALPHA_ERODE_SIZE,
        post_process_mask=True,
    )
    return refine_alpha(result.convert("RGBA"))


def remove_with_sam(image: Image.Image) -> Image.Image:
    from image.mask import improve_mask
    from image.segmentation import generate_mask
    from image.utils import resize_for_sam

    original_size = image.size
    sam_image, _ = resize_for_sam(image)
    mask = generate_mask(sam_image)

    if mask is None:
        raise ValueError("Объект не найден")

    mask = improve_mask(mask)
    mask_image = Image.fromarray(mask).resize(
        original_size,
        Image.Resampling.LANCZOS,
    )
    result = np.array(image)
    result[:, :, 3] = np.array(mask_image)
    return refine_alpha(Image.fromarray(result))


def refine_alpha(image: Image.Image) -> Image.Image:
    red, green, blue, alpha = image.split()

    alpha = alpha.filter(ImageFilter.MedianFilter(size=3))
    alpha = alpha.filter(ImageFilter.GaussianBlur(radius=0.35))
    alpha = alpha.point(clean_alpha_value)

    return Image.merge("RGBA", (red, green, blue, alpha))


def clean_alpha_value(value: int) -> int:
    if value <= 6:
        return 0

    if value >= 249:
        return 255

    return value


@lru_cache(maxsize=1)
def get_rembg_session():
    model_name = os.getenv("REMBG_MODEL", DEFAULT_MODEL)
    return new_session(model_name)
