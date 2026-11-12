import pytest

from database.engine import create_database_engine


def test_engine_missing_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    with pytest.raises(RuntimeError) as exc_info:
        create_database_engine()
    assert str(exc_info.value) == "DATABASE_URL is not set"


def test_engine_sqlite_in_memory_url(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("DATABASE_URL", "sqlite://")
    db_engine = create_database_engine()
    try:
        assert str(db_engine.url) == "sqlite://"
    finally:
        db_engine.dispose()
