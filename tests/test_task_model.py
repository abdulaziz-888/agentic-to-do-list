from sqlalchemy import inspect
from sqlalchemy.engine import create_engine

from database.base import Base
from database.task_model import TaskRecord


def test_task_model_creates_tasks_table() -> None:
    engine = create_engine("sqlite://")

    Base.metadata.create_all(engine)

    inspector = inspect(engine)
    table_name = TaskRecord.__tablename__

    assert inspector.has_table(table_name)

    columns = inspector.get_columns(table_name)
    column_names = [column["name"] for column in columns]

    assert column_names == [
        "id",
        "title",
        "description",
        "status",
        "created_at",
        "updated_at",
    ]