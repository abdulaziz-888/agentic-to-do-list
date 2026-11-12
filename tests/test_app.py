import os
from pathlib import Path
from unittest.mock import Mock

import pytest
from dotenv import load_dotenv

import app


def test_load_application_environment_from_dotenv(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
) -> None:
    monkeypatch.delenv("DATABASE_URL", raising=False)
    dotenv_path = tmp_path / ".env"
    dotenv_path.write_text("DATABASE_URL=sqlite://\n")
    monkeypatch.setattr(
        app,
        "load_dotenv",
        lambda: load_dotenv(dotenv_path=dotenv_path),
    )

    app.load_application_environment()

    assert os.environ["DATABASE_URL"] == "sqlite://"


def test_create_task_service_composes_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = object()
    session_factory = object()
    repository = object()
    service = object()

    load_environment = Mock()
    create_engine = Mock(return_value=engine)
    create_sessions = Mock(return_value=session_factory)
    create_repository = Mock(return_value=repository)
    create_service = Mock(return_value=service)

    monkeypatch.setattr(app, "load_application_environment", load_environment)
    monkeypatch.setattr(app, "create_database_engine", create_engine)
    monkeypatch.setattr(app, "create_session_factory", create_sessions)
    monkeypatch.setattr(app, "SQLAlchemyTaskRepository", create_repository)
    monkeypatch.setattr(app, "TaskService", create_service)

    result = app.create_task_service()

    load_environment.assert_called_once_with()
    create_engine.assert_called_once_with()
    create_sessions.assert_called_once_with(engine)
    create_repository.assert_called_once_with(session_factory)
    create_service.assert_called_once_with(repository)
    assert result is service


def test_create_execution_loop_composes_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    service = object()
    adapters = object()
    dispatcher = object()
    execution_loop = object()

    create_service = Mock(return_value=service)
    create_adapters = Mock(return_value=adapters)
    create_dispatcher = Mock(return_value=dispatcher)
    create_loop = Mock(return_value=execution_loop)

    monkeypatch.setattr(app, "create_task_service", create_service)
    monkeypatch.setattr(app, "TaskToolAdapters", create_adapters)
    monkeypatch.setattr(app, "ToolDispatcher", create_dispatcher)
    monkeypatch.setattr(app, "ExecutionLoop", create_loop)

    result = app.create_execution_loop()

    create_service.assert_called_once_with()
    create_adapters.assert_called_once_with(service)
    create_dispatcher.assert_called_once_with(adapters)
    create_loop.assert_called_once_with(dispatcher)
    assert result is execution_loop
