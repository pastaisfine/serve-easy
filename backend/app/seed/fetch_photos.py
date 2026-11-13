"""Fetch Unsplash search results for every photo group into photo_cache.json.

Usage (from backend/):  uv run python -m app.seed.fetch_photos [--fresh]

Needs UNSPLASH_ACCESS_KEY in backend/.env. Demo-tier keys allow 50 requests an
hour, so this stops and waits when the limit is hit and resumes by itself. It
skips groups already in the cache, so it is safe to stop and rerun.

After a visual review, list bad candidates in photo_rejects.json (group -> indexes).
Do not edit the cache by hand: this script rewrites it.
"""

import json
import sys
import time
from pathlib import Path

import httpx

from app.config import settings
from app.seed.photo_groups import GROUPS

CACHE = Path(__file__).with_name("photo_cache.json")
API = "https://api.unsplash.com/search/photos"
PER_PAGE = 10


def _load() -> dict:
    return json.loads(CACHE.read_text()) if CACHE.exists() else {}


def _save(cache: dict) -> None:
    CACHE.write_text(json.dumps(cache, indent=1, ensure_ascii=False) + "\n")


def _candidates(results: list[dict]) -> list[dict]:
    """Keep only plain images.unsplash.com photos (the frontend allows only that host)."""
    out = []
    for r in results:
        path = r["urls"]["raw"].split("?")[0].removeprefix("https://images.unsplash.com/")
        if not path.startswith("photo-"):  # skips plus.unsplash.com / premium_photo-
            continue
        out.append(
            {
                "path": path,
                "photographer": r["user"]["name"],
                "link": r["links"]["html"],
                "alt": r.get("alt_description") or r.get("description") or "",
            }
        )
    return out


def main(argv: list[str] | None = None) -> None:
    key = settings.unsplash_access_key
    if not key:
        sys.exit("Set UNSPLASH_ACCESS_KEY in backend/.env")
    cache = {} if "--fresh" in (argv or sys.argv[1:]) else _load()
    # Fetch what is missing, empty, or was searched with an older query.
    todo = [g for g in GROUPS if g not in cache or not cache[g]["photos"] or cache[g]["query"] != GROUPS[g]]
    print(f"{len(cache)} cached, {len(todo)} to fetch", flush=True)

    with httpx.Client(headers={"Authorization": f"Client-ID {key}"}, timeout=30) as client:
        for n, group in enumerate(todo, start=1):
            query = GROUPS[group]
            while True:
                res = client.get(API, params={"query": query, "per_page": PER_PAGE, "content_filter": "high"})
                if res.status_code == 403 and "rate limit" in res.text.lower():
                    print("  rate limit reached, waiting 5 min ...", flush=True)
                    time.sleep(300)
                    continue
                res.raise_for_status()
                break
            cache[group] = {"query": query, "photos": _candidates(res.json()["results"])}
            _save(cache)
            print(f"[{n}/{len(todo)}] {group}: {len(cache[group]['photos'])} photos "
                  f"(remaining this hour: {res.headers.get('x-ratelimit-remaining')})", flush=True)
    print("done", flush=True)


if __name__ == "__main__":
    main()
