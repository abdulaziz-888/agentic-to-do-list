import datetime
from uuid import uuid4

from sqlalchemy import inspect
from sqlalchemy.engine import create_engine
from sqlalchemy.orm import Session

from database.base import Base
from database.task_model import TaskRecord
from domains.task import TaskStatus


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


def test_task_model_create_task_record() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    timestamp_now = datetime.datetime.now(datetime.UTC)
    task_record = TaskRecord(
        id=uuid4(),
        title="Task 1",
        description="task 1 description",
        status=TaskStatus.TODO,
        created_at=timestamp_now,
        updated_at=timestamp_now,
    )
    created_record_id = task_record.id
    created_record_title = task_record.title
    created_record_description = task_record.description
    created_record_status = task_record.status
    created_record_created_at = task_record.created_at
    created_record_updated_at = task_record.updated_at
    expected_created_at = created_record_created_at.replace(tzinfo=None)
    expected_updated_at = created_record_updated_at.replace(tzinfo=None)

    with Session(engine) as session:
        session.add(task_record)
        session.commit()

    with Session(engine) as session2:
        loaded_record = session2.get(TaskRecord, created_record_id)
        assert loaded_record is not None
        assert loaded_record.id == created_record_id
        assert loaded_record.title == created_record_title
        assert loaded_record.description == created_record_description
        assert loaded_record.status == created_record_status
        assert loaded_record.created_at == expected_created_at
        assert loaded_record.updated_at == expected_updated_at
        assert loaded_record.created_at.tzinfo is None
        assert loaded_record.updated_at.tzinfo is None
