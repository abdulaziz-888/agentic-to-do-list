from dotenv import load_dotenv

from agent.execution_loop import ExecutionLoop
from agent.task_tool_adapters import TaskToolAdapters
from agent.tool_dispatcher import ToolDispatcher
from database.engine import create_database_engine
from database.session import create_session_factory
from repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from services.task_service import TaskService


def load_application_environment() -> None:
    load_dotenv()


def create_task_service() -> TaskService:
    load_application_environment()
    engine = create_database_engine()
    session_factory = create_session_factory(engine)
    repository = SQLAlchemyTaskRepository(session_factory)
    return TaskService(repository)


def create_execution_loop() -> ExecutionLoop:
    task_service = create_task_service()
    task_tool_adapters = TaskToolAdapters(task_service)
    tool_dispatcher = ToolDispatcher(task_tool_adapters)
    return ExecutionLoop(tool_dispatcher)
