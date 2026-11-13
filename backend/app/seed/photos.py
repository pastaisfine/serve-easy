"""Pick a seed photo for a row from the Unsplash search cache (photo_cache.json).

Only the first REVIEWED photos of each group are used: those were checked by eye on a
contact sheet. Photos that failed review are listed in photo_rejects.json
(group -> indexes), which is kept apart from the cache so a re-fetch cannot erase it.

Rows in the same group rotate through that group's non-rejected candidates, so
repeated items (for example many textbooks) do not all show the same picture.
Returns None when a group is not cached yet, so callers can fall back.
"""

import json
from pathlib import Path

_CACHE_FILE = Path(__file__).with_name("photo_cache.json")
_cache: dict = json.loads(_CACHE_FILE.read_text()) if _CACHE_FILE.exists() else {}
_REJECTS_FILE = Path(__file__).with_name("photo_rejects.json")
_rejects: dict[str, list[int]] = json.loads(_REJECTS_FILE.read_text()) if _REJECTS_FILE.exists() else {}
_counters: dict[str, int] = {}
REVIEWED = 6


def _usable(group: str) -> list[dict]:
    entry = _cache.get(group)
    if not entry:
        return []
    rejected = set(_rejects.get(group, []))
    return [p for i, p in enumerate(entry["photos"][:REVIEWED]) if i not in rejected]


def pick(group: str, width: int = 600) -> str | None:
    photos = _usable(group)
    if not photos:
        return None
    n = _counters.get(group, 0)
    _counters[group] = n + 1
    path = photos[n % len(photos)]["path"]
    return f"https://images.unsplash.com/{path}?w={width}&q=75&auto=format&fit=crop"
