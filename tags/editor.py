from mutagen.id3 import (
    ID3,
    TIT2,
    TPE1,
    TALB,
    TDRC,
    TCON
)

def update_metadata(
    file_path: str,
    field: str,
    value: str
):
    
    tags = ID3(file_path)

    if field == "title":
        tags["TIT2"] = TIT2(
            encoding=3,
            text=value
        )
    elif field == "artist":
        tags["TPE1"] = TPE1(
            encoding=3,
            text=value
        )
    elif field == "album":
        tags["TALB"] = TALB(
            encoding=3,
            text=value
        )
    elif field == "year":
        tags["TDRC"] = TDRC(
            encoding=3,
            text=value
        )
    elif field == "genre":
        tags["TCON"] = TCON(
            encoding=3,
            text=value
        )

    tags.save(file_path)