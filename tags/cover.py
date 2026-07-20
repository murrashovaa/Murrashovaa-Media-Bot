from mutagen.id3 import ID3, APIC
from PIL import Image
import io

def crop_square(image: Image.Image):
    width, height = image.size
    size = min(
        width,
        height
    )
    left = (width - size) // 2
    top = (height - size) // 2
    right = left + size
    bottom = top + size
    return image.crop(
        (
            left,
            top,
            right,
            bottom
        )
    )

def add_cover(
    audio_path: str,
    image_path: str
):
    try:
        tags = ID3(audio_path)
    except:
        tags = ID3()
    image = Image.open(
        image_path
    )
    image = image.convert(
        "RGB"
    )
    image = crop_square(
        image
    )
    max_size = 1500
    image.thumbnail(
        (max_size, max_size)
    )
    buffer = io.BytesIO()
    image.save(
        buffer,
        format="JPEG",
        quality=95
    )
    image_data = buffer.getvalue()
    tags.delall(
        "APIC"
    )
    tags.add(
        APIC(
            encoding=3,
            mime="image/jpeg",
            type=3,
            desc="Cover",
            data=image_data
        )
    )
    tags.save(
        audio_path
    )


def extract_cover(
    audio_path: str
):
    try:
        tags = ID3(audio_path)
    except:
        return None
    for key in tags.keys():
        if key.startswith("APIC"):
            return tags[key].data
    return None