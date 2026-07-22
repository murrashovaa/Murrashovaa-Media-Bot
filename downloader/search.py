import html
import json
import os
import re
import uuid
from dataclasses import asdict, dataclass
from urllib.parse import quote_plus

import requests
import yt_dlp

from config.settings import STORAGE_PATH
from downloader.errors import raise_friendly_ytdlp_error
from downloader.music import (
    build_audio_filename,
    download_music,
    get_unique_path,
)
from downloader.options import add_ytdlp_auth_options

HITMO_DOMAINS = (
    "https://ru.hitmoz.org",
    "https://rus.hitmos.fm",
    "https://rus.hitmotop.com",
)
SEARCH_LIMIT = 10
REQUEST_TIMEOUT = 15
CHUNK_SIZE = 1024 * 256

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/126.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

TRACK_PATTERN = re.compile(
    r'\{"id":(?P<id>\d+),'
    r'"artist":"(?P<artist>(?:\\.|[^"])*)",'
    r'"title":"(?P<title>(?:\\.|[^"])*)".*?'
    r'"duration":(?P<duration>\d+),'
    r'"bitrate":(?P<bitrate>\d+),'
    r'"size":(?P<size>\d+),'
    r'"play":"(?P<play>https://[^"]+)",'
    r'"download":"(?P<download>https://[^"]+)"',
    re.S,
)


class TrackSearchError(Exception):
    """Не удалось найти или скачать трек из поиска."""


@dataclass
class TrackSearchResult:
    source: str
    artist: str
    title: str
    url: str
    duration: int | None = None
    bitrate: int | None = None
    size: int | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> "TrackSearchResult":
        return cls(**data)

    @property
    def display_name(self) -> str:
        if self.artist:
            return f"{self.artist} - {self.title}"

        return self.title


def search_tracks(
    query: str,
    limit: int = SEARCH_LIMIT,
) -> list[TrackSearchResult]:
    normalized_query = query.strip()
    if len(normalized_query) < 2:
        raise ValueError("Введите название песни минимум из 2 символов.")

    hitmo_results = search_hitmo_tracks(normalized_query, limit)
    if hitmo_results:
        return hitmo_results

    youtube_results = search_youtube_tracks(normalized_query, limit)
    if youtube_results:
        return youtube_results

    raise TrackSearchError("Не удалось найти треки по этому запросу.")


def download_search_result(result_data: dict) -> str:
    result = TrackSearchResult.from_dict(result_data)

    if result.source == "YouTube":
        return download_music(result.url)

    return download_hitmo_track(result)


def search_hitmo_tracks(
    query: str,
    limit: int,
) -> list[TrackSearchResult]:
    for domain in HITMO_DOMAINS:
        try:
            response = requests.get(
                f"{domain}/search?q={quote_plus(query)}",
                headers=HEADERS,
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code != 200:
                continue

            results = parse_hitmo_tracks(response.text, limit)
            if results:
                return results
        except requests.RequestException:
            continue

    return []


def parse_hitmo_tracks(
    page_text: str,
    limit: int,
) -> list[TrackSearchResult]:
    normalized_text = html.unescape(page_text).replace('\\"', '"')
    results: list[TrackSearchResult] = []
    seen_urls: set[str] = set()

    for match in TRACK_PATTERN.finditer(normalized_text):
        download_url = unescape_js_string(match.group("download"))
        if download_url in seen_urls:
            continue

        seen_urls.add(download_url)
        results.append(
            TrackSearchResult(
                source="Hitmo",
                artist=unescape_js_string(match.group("artist")),
                title=unescape_js_string(match.group("title")),
                url=download_url,
                duration=int(match.group("duration")),
                bitrate=int(match.group("bitrate")),
                size=int(match.group("size")),
            )
        )

        if len(results) >= limit:
            break

    return results


def search_youtube_tracks(
    query: str,
    limit: int,
) -> list[TrackSearchResult]:
    options = {
        "extract_flat": True,
        "quiet": True,
        "skip_download": True,
        "noplaylist": True,
    }
    add_ytdlp_auth_options(options)

    try:
        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(
                f"ytsearch{limit}:{query}",
                download=False,
            )
    except Exception as error:
        try:
            raise_friendly_ytdlp_error(error)
        except Exception:
            return []

    results: list[TrackSearchResult] = []
    for entry in info.get("entries", []):
        if not entry:
            continue

        title = entry.get("title") or "audio"
        artist = entry.get("uploader") or entry.get("channel") or "YouTube"
        url = entry.get("webpage_url") or entry.get("url")
        if not url:
            continue

        results.append(
            TrackSearchResult(
                source="YouTube",
                artist=str(artist),
                title=str(title),
                url=str(url),
                duration=entry.get("duration"),
            )
        )

    return results


def download_hitmo_track(result: TrackSearchResult) -> str:
    os.makedirs(STORAGE_PATH, exist_ok=True)

    filename = build_audio_filename(result.artist, result.title)
    file_path = get_unique_path(os.path.join(STORAGE_PATH, filename))
    temp_path = f"{file_path}.{uuid.uuid4().hex}.part"

    try:
        with requests.get(
            result.url,
            headers=HEADERS,
            stream=True,
            timeout=REQUEST_TIMEOUT,
        ) as response:
            response.raise_for_status()

            with open(temp_path, "wb") as file:
                for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                    if chunk:
                        file.write(chunk)

        os.replace(temp_path, file_path)
        return file_path
    except requests.RequestException as error:
        raise TrackSearchError("Не удалось скачать выбранный трек.") from error
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def unescape_js_string(value: str) -> str:
    try:
        return json.loads(f'"{value}"')
    except json.JSONDecodeError:
        return value


def format_track_duration(seconds: int | None) -> str:
    if not seconds:
        return "?:??"

    minutes, seconds = divmod(seconds, 60)
    return f"{minutes}:{seconds:02d}"


def format_track_size(size: int | None) -> str:
    if not size:
        return ""

    return f"{size / 1024 / 1024:.1f} MB"
