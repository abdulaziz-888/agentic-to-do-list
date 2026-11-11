import datetime

import pytest
from sqlalchemy import create_engine

from database.base import Base
from database.session import create_session_factory
from domains.task import TaskStatus
from repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from services.task_service import TaskService


def test_task_service_with_sqlalchemy_repository(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    session_factory = create_session_factory(engine)
    repository = SQLAlchemyTaskRepository(session_factory)
    service = TaskService(repository)

    created_at = datetime.datetime(2026, 11, 12, 10, tzinfo=datetime.UTC)
    completed_at = created_at + datetime.timedelta(minutes=1)
    timestamps = iter([created_at, completed_at])
    monkeypatch.setattr(
        TaskService,
        "get_now",
        staticmethod(lambda: next(timestamps)),
    )

    created_task = service.create_task("Task 1", "Task 1 description")

    assert service.get_task_by_id(created_task.id) == created_task
    assert service.list_tasks() == [created_task]

    completed_task = service.complete_task(created_task.id)
    assert completed_task.status is TaskStatus.COMPLETED
    assert completed_task.updated_at == completed_at

    repeated_task = service.complete_task(created_task.id)
    assert repeated_task == completed_task
    assert repeated_task.updated_at == completed_at

    fresh_service = TaskService(SQLAlchemyTaskRepository(session_factory))
    assert fresh_service.get_task_by_id(created_task.id) == completed_task
    assert fresh_service.list_tasks() == [completed_task]
