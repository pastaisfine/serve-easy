"""Usage: uv run python -m app.seed [--reset --yes]"""

import argparse

from sqlalchemy import create_engine

from app.config import settings, to_sqlalchemy_url
from app.seed.runner import reset, seed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m app.seed", description="Seed demo UTM data.")
    parser.add_argument("--reset", action="store_true", help="Delete all rows from the app tables first.")
    parser.add_argument("--yes", action="store_true", help="Confirm a destructive --reset.")
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.reset and not args.yes:
        parser.error("--reset deletes all app data; pass --yes to confirm.")

    # Seeding uses the direct (non-pooled) connection, like migrations.
    engine = create_engine(to_sqlalchemy_url(settings.migration_url))
    with engine.begin() as conn:  # one transaction: all-or-nothing
        if args.reset:
            reset(conn)
            print("Reset: app tables emptied.")
        counts = seed(conn)
    for name, count in counts.items():
        print(f"{name:20} {count}")


if __name__ == "__main__":
    main()
