import os

from sqlalchemy.engine import Engine, create_engine


def create_database_engine() -> Engine:
    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return create_engine(url=database_url)
