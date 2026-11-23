"""Idempotent seeding: upsert every row by its stable id, parents first."""

from sqlalchemy import Connection, func, select, text
from sqlalchemy.dialects.postgresql import insert

from app.models import Base
from app.seed.data import TABLES


def reset(conn: Connection) -> None:
    """Empty only the application tables (never neon_auth or alembic_version)."""
    names = ", ".join(f'"{name}"' for name, _ in TABLES)
    conn.execute(text(f"TRUNCATE TABLE {names} RESTART IDENTITY CASCADE"))


def seed(conn: Connection) -> dict[str, int]:
    """Upsert all seed rows on `conn`. The caller owns the transaction.

    Returns the number of seeded rows present in each table afterwards.
    """
    result: dict[str, int] = {}
    for name, rows in TABLES:
        if not rows:
            result[name] = 0
            continue
        table = Base.metadata.tables[name]
        stmt = insert(table)
        update_cols = {c: stmt.excluded[c] for c in rows[0] if c != "id"}
        conn.execute(
            stmt.on_conflict_do_update(index_elements=["id"], set_=update_cols),
            rows,
        )
        ids = [r["id"] for r in rows]
        result[name] = conn.execute(
            select(func.count()).select_from(table).where(table.c.id.in_(ids))
        ).scalar_one()
    return result
