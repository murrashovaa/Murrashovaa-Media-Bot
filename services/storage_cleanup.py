import logging
import time
from pathlib import Path

from config.settings import STORAGE_CLEANUP_MAX_AGE_HOURS, STORAGE_PATH

logger = logging.getLogger(__name__)

CACHE_DIR_NAMES = {"numba_cache"}


def cleanup_storage() -> int:
    storage_root = get_storage_root()

    if not storage_root.exists():
        return 0

    cutoff_time = time.time() - STORAGE_CLEANUP_MAX_AGE_HOURS * 60 * 60
    removed_files = 0

    for file_path in storage_root.rglob("*"):
        if should_skip_path(file_path) or not file_path.is_file():
            continue

        if file_path.stat().st_mtime > cutoff_time:
            continue

        file_path.unlink(missing_ok=True)
        removed_files += 1

    remove_empty_dirs(storage_root)

    if removed_files:
        logger.info("Cleaned %s old storage files", removed_files)

    return removed_files


def get_storage_root() -> Path:
    storage_path = Path(STORAGE_PATH)

    if storage_path.name == "temp":
        return storage_path.parent

    return storage_path


def should_skip_path(path: Path) -> bool:
    return any(part in CACHE_DIR_NAMES for part in path.parts)


def remove_empty_dirs(storage_root: Path) -> None:
    for directory in sorted(storage_root.rglob("*"), reverse=True):
        if should_skip_path(directory) or not directory.is_dir():
            continue

        try:
            directory.rmdir()
        except OSError:
            continue
