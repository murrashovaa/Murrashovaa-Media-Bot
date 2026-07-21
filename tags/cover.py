import io

from mutagen.id3 import APIC, ID3, ID3NoHeaderError
from PIL import Image

MAX_COVER_SIZE = 1500


def crop_square(image: Image.Image) -> Image.Image:
    width, height = image.size
    size = min(width, height)
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    return image.crop((left, top, right, bottom))


def add_cover(
    audio_path: str,
    image_path: str,
) -> None:
    try:
        tags = ID3(audio_path)
    except ID3NoHeaderError:
        tags = ID3()

    image = Image.open(image_path).convert("RGB")
    image = crop_square(image)
    image.thumbnail((MAX_COVER_SIZE, MAX_COVER_SIZE))

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG", quality=95)
    image_data = buffer.getvalue()

    tags.delall("APIC")
    tags.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=image_data,
        )
    )
    tags.save(audio_path)


def extract_cover(audio_path: str) -> bytes | None:
    try:
        tags = ID3(audio_path)
    except ID3NoHeaderError:
        return None

    for key in tags.keys():
        if key.startswith("APIC"):
            return tags[key].data

    return None
