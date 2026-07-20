from mutagen import File


def read_metadata(file_path: str):

    audio = File(file_path)

    if not audio:
        return None

    tags = audio.tags

    if not tags:
        return {
            "title": None,
            "artist": None,
            "album": None,
            "year": None,
            "genre": None,
            "cover": False,
        }


    return {
        "title": get_tag(tags, "TIT2"),
        "artist": get_tag(tags, "TPE1"),
        "album": get_tag(tags, "TALB"),
        "year": get_tag(tags, "TDRC"),
        "genre": get_tag(tags, "TCON"),
        "cover": has_cover(tags)
    }


def get_tag(tags, key):
    value = tags.get(key)
    if value:
        return str(value.text[0])
    return None


def has_cover(tags):
    for key in tags.keys():
        if key.startswith("APIC"):
            return True
    return False