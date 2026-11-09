import pytest

from agent.execution_loop import ExecutionLoop
from agent.task_tool_adapters import TaskToolAdapters
from agent.tool_dispatcher import ToolDispatcher
from repositories.in_memory_task_repository import InMemoryTaskRepository
from services.task_service import TaskService


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


@pytest.fixture
def tool_dispatcher(
    task_tool_adapters: TaskToolAdapters,
) -> ToolDispatcher:
    return ToolDispatcher(task_tool_adapters)


@pytest.fixture
def execution_loop(
    tool_dispatcher: ToolDispatcher,
) -> ExecutionLoop:
    return ExecutionLoop(tool_dispatcher)
