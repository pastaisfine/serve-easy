"""Idempotently seed the three prototype meal providers and their sample menus."""

from sqlalchemy import create_engine
from sqlalchemy.dialects.postgresql import insert

from app.config import settings, to_sqlalchemy_url
from app.models import Base
from app.seed import data


def seed_meals() -> dict[str, int]:
    engine = create_engine(to_sqlalchemy_url(settings.migration_url), pool_pre_ping=True)
    rows_by_table = {
        "food_providers": data.FOOD_PROVIDERS,
        "food_items": [
            item for item in data.FOOD_ITEMS if item.get("provider_id") is not None
        ],
    }
    result: dict[str, int] = {}
    with engine.begin() as connection:
        for name, rows in rows_by_table.items():
            table = Base.metadata.tables[name]
            statement = insert(table)
            updates = {column: statement.excluded[column] for column in rows[0] if column != "id"}
            connection.execute(
                statement.on_conflict_do_update(index_elements=["id"], set_=updates), rows
            )
            result[name] = len(rows)
    engine.dispose()
    return result


if __name__ == "__main__":
    for table, count in seed_meals().items():
        print(f"{table}: {count} prototype rows")
