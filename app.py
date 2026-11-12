from dataclasses import dataclass
from types import TracebackType
from typing import Self

from dotenv import load_dotenv
from sqlalchemy.engine import Engine

from agent.execution_loop import ExecutionLoop
from agent.task_tool_adapters import TaskToolAdapters
from agent.tool_dispatcher import ToolDispatcher
from database.engine import create_database_engine
from database.session import create_session_factory
from repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from services.task_service import TaskService


@dataclass
class Application:
    engine: Engine
    execution_loop: ExecutionLoop

    def close(self) -> None:
        self.engine.dispose()

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        _exception_type: type[BaseException] | None,
        _exception: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.close()


def load_application_environment() -> None:
    load_dotenv()


def create_task_service(engine: Engine) -> TaskService:
    session_factory = create_session_factory(engine)
    repository = SQLAlchemyTaskRepository(session_factory)
    return TaskService(repository)


def create_execution_loop(engine: Engine) -> ExecutionLoop:
    task_service = create_task_service(engine=engine)
    task_tool_adapters = TaskToolAdapters(task_service)
    tool_dispatcher = ToolDispatcher(task_tool_adapters)
    return ExecutionLoop(tool_dispatcher)


def create_application() -> Application:
    load_application_environment()
    engine = create_database_engine()
    try:
        execution_loop = create_execution_loop(engine=engine)
        return Application(
            engine=engine,
            execution_loop=execution_loop,
        )
    except Exception:
        engine.dispose()
        raise
