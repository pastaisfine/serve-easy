import pytest
from sqlalchemy import create_engine, func, select

from app.config import settings, to_sqlalchemy_url
from app.models import Base
from app.seed import data
from app.seed.__main__ import main
from app.seed.runner import seed


def test_reset_without_yes_is_rejected_before_touching_the_database(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--reset"])
    assert exc.value.code == 2
    assert "--yes" in capsys.readouterr().err


def test_seeding_twice_gives_identical_counts_and_leaves_no_trace():
    engine = create_engine(to_sqlalchemy_url(settings.migration_url))
    expected = data.summary()
    with engine.connect() as conn:
        trans = conn.begin()  # rolled back at the end, so the test writes nothing
        try:
            first = seed(conn)
            totals_first = {
                n: conn.scalar(select(func.count()).select_from(Base.metadata.tables[n]))
                for n in expected
            }
            second = seed(conn)
            totals_second = {
                n: conn.scalar(select(func.count()).select_from(Base.metadata.tables[n]))
                for n in expected
            }
        finally:
            trans.rollback()
    assert first == second == expected
    assert totals_first == totals_second
