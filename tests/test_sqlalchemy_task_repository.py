import datetime
from uuid import UUID, uuid4

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from database.base import Base
from database.session import create_session_factory
from database.task_mapper import record_to_task
from database.task_model import TaskRecord
from domains.task import Task, TaskStatus
from repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository


@pytest.fixture
def sqlite_engine() -> Engine:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    return engine


@pytest.fixture
def sqlalchemy_session_factory(
    sqlite_engine: Engine,
) -> sessionmaker[Session]:
    return create_session_factory(sqlite_engine)


@pytest.fixture
def sqlalchemy_task_repository(
    sqlalchemy_session_factory: sessionmaker[Session],
) -> SQLAlchemyTaskRepository:
    return SQLAlchemyTaskRepository(sqlalchemy_session_factory)


def make_task(
    *,
    title: str,
    created_at: datetime.datetime,
    task_id: UUID | None = None,
    status: TaskStatus = TaskStatus.TODO,
    updated_at: datetime.datetime | None = None,
) -> Task:
    return Task(
        id=task_id or uuid4(),
        title=title,
        description=f"{title} description",
        status=status,
        created_at=created_at,
        updated_at=updated_at or created_at,
    )


def test_save_commits_task(
    sqlalchemy_task_repository: SQLAlchemyTaskRepository,
    sqlalchemy_session_factory: sessionmaker[Session],
) -> None:
    timestamp = datetime.datetime(2026, 11, 12, 10, tzinfo=datetime.UTC)
    task = make_task(title="Task 1", created_at=timestamp)

    saved_task = sqlalchemy_task_repository.save(task)

    assert saved_task == task
    with sqlalchemy_session_factory() as session:
        stored_record = session.get(TaskRecord, task.id)
        assert stored_record is not None
        assert record_to_task(stored_record) == task


def test_get_by_id(
    sqlalchemy_task_repository: SQLAlchemyTaskRepository,
) -> None:
    unknown_id = uuid4()
    assert sqlalchemy_task_repository.get_by_id(unknown_id) is None

    timestamp = datetime.datetime(2026, 11, 12, 10, tzinfo=datetime.UTC)
    task = make_task(title="Task 1", created_at=timestamp)
    sqlalchemy_task_repository.save(task)

    assert sqlalchemy_task_repository.get_by_id(task.id) == task


def test_list_all_returns_tasks_in_creation_order(
    sqlalchemy_task_repository: SQLAlchemyTaskRepository,
) -> None:
    assert sqlalchemy_task_repository.list_all() == []

    first_timestamp = datetime.datetime(2026, 11, 12, 10, tzinfo=datetime.UTC)
    second_timestamp = first_timestamp + datetime.timedelta(seconds=1)
    first_task = make_task(title="Task 1", created_at=first_timestamp)
    second_task = make_task(title="Task 2", created_at=second_timestamp)
    sqlalchemy_task_repository.save(first_task)
    sqlalchemy_task_repository.save(second_task)

    assert sqlalchemy_task_repository.list_all() == [first_task, second_task]


def test_save_replaces_task_with_same_id(
    sqlalchemy_task_repository: SQLAlchemyTaskRepository,
) -> None:
    created_at = datetime.datetime(2026, 11, 12, 10, tzinfo=datetime.UTC)
    original = make_task(title="Task 1", created_at=created_at)
    sqlalchemy_task_repository.save(original)

    completed_at = created_at + datetime.timedelta(minutes=1)
    replacement = make_task(
        task_id=original.id,
        title="Updated task",
        status=TaskStatus.COMPLETED,
        created_at=created_at,
        updated_at=completed_at,
    )

    saved_task = sqlalchemy_task_repository.save(replacement)

    assert saved_task == replacement
    assert sqlalchemy_task_repository.get_by_id(original.id) == replacement
    assert sqlalchemy_task_repository.list_all() == [replacement]
