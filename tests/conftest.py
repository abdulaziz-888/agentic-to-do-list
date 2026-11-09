from collections.abc import Generator

import pytest

from agent.task_tool_adapters import TaskToolAdapters
from repositories.in_memory_task_repository import InMemoryTaskRepository
from services.task_service import TaskService
from tools.tasks import tasks


@pytest.fixture(autouse=True)
def setup_tasks() -> Generator[None]:
    tasks.clear()
    yield
    tasks.clear()


@pytest.fixture
def task_repository() -> InMemoryTaskRepository:
    return InMemoryTaskRepository()


@pytest.fixture
def task_service(
    task_repository: InMemoryTaskRepository,
) -> TaskService:
    return TaskService(task_repository)


@pytest.fixture
def task_tool_adapters(
    task_service: TaskService,
) -> TaskToolAdapters:
    return TaskToolAdapters(task_service)
