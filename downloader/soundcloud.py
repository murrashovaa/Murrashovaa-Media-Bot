import os
import yt_dlp


DOWNLOAD_PATH = "storage/temp"


def download_soundcloud_audio(url: str):

    os.makedirs(
        DOWNLOAD_PATH,
        exist_ok=True
    )


    options = {
        "format": "bestaudio/best",

        "outtmpl": f"{DOWNLOAD_PATH}/%(title)s.%(ext)s",

        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            }
        ],

        "noplaylist": True,
    }


    with yt_dlp.YoutubeDL(options) as ydl:

        info = ydl.extract_info(
            url,
            download=True
        )

        filename = ydl.prepare_filename(info)

        filename = (
            os.path.splitext(filename)[0]
            + ".mp3"
        )


    return filename