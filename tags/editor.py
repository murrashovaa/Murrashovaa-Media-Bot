from mutagen.id3 import (
    ID3,
    ID3NoHeaderError,
    TALB,
    TCON,
    TIT2,
    TPE1,
    TDRC,
)

TAG_FRAMES = {
    "title": ("TIT2", TIT2),
    "artist": ("TPE1", TPE1),
    "album": ("TALB", TALB),
    "year": ("TDRC", TDRC),
    "genre": ("TCON", TCON),
}


def update_metadata(
    file_path: str,
    field: str,
    value: str,
) -> None:
    try:
        tags = ID3(file_path)
    except ID3NoHeaderError:
        tags = ID3()

    frame_data = TAG_FRAMES.get(field)
    if frame_data is None:
        raise ValueError(f"Неизвестное поле тега: {field}")

    frame_key, frame_class = frame_data
    tags[frame_key] = frame_class(encoding=3, text=value)

    tags.save(file_path)
