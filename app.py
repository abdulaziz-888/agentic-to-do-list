import os
from dataclasses import dataclass
from types import TracebackType
from typing import Self

from dotenv import load_dotenv
from ollama import Client
from sqlalchemy.engine import Engine

from agent.agent_loop import AgentLoop
from agent.execution_loop import ExecutionLoop
from agent.ollama_provider import OllamaProvider
from agent.task_tool_adapters import TaskToolAdapters
from agent.task_tool_definitions import TASK_TOOL_DEFINITIONS
from agent.tool_dispatcher import ToolDispatcher
from database.engine import create_database_engine
from database.session import create_session_factory
from repositories.sqlalchemy_task_repository import SQLAlchemyTaskRepository
from services.task_service import TaskService


@dataclass
class Application:
    engine: Engine
    llm_provider: OllamaProvider
    agent_loop: AgentLoop

    def close(self) -> None:
        try:
            self.llm_provider.close()
        finally:
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
    llm_provider = None
    try:
        llm_provider = create_llm_provider()
        agent_loop = create_agent_loop(
            engine=engine,
            llm_provider=llm_provider,
        )
        return Application(
            engine=engine,
            llm_provider=llm_provider,
            agent_loop=agent_loop,
        )
    except Exception:
        try:
            if llm_provider is not None:
                llm_provider.close()
        finally:
            engine.dispose()
        raise


def create_llm_provider() -> OllamaProvider:
    client = Client(host=os.environ["OLLAMA_HOST"])
    return OllamaProvider(
        client=client,
        model=os.environ["OLLAMA_MODEL"],
    )


def create_agent_loop(
    engine: Engine,
    llm_provider: OllamaProvider,
) -> AgentLoop:
    execution_loop = create_execution_loop(engine=engine)

    return AgentLoop(
        llm_provider=llm_provider,
        execution_loop=execution_loop,
        tools=TASK_TOOL_DEFINITIONS,
    )
