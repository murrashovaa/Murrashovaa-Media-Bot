from mutagen import File

EMPTY_METADATA = {
    "title": None,
    "artist": None,
    "album": None,
    "year": None,
    "genre": None,
    "cover": False,
}


def read_metadata(file_path: str) -> dict:
    audio = File(file_path)

    if not audio:
        return EMPTY_METADATA.copy()

    tags = audio.tags

    if not tags:
        return EMPTY_METADATA.copy()

    return {
        "title": get_tag(tags, "TIT2"),
        "artist": get_tag(tags, "TPE1"),
        "album": get_tag(tags, "TALB"),
        "year": get_tag(tags, "TDRC"),
        "genre": get_tag(tags, "TCON"),
        "cover": has_cover(tags),
    }


def get_tag(tags, key: str) -> str | None:
    value = tags.get(key)

    if value:
        return str(value.text[0])

    return None


def has_cover(tags) -> bool:
    for key in tags.keys():
        if key.startswith("APIC"):
            return True

    return False
