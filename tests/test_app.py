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

    create_sessions = Mock(return_value=session_factory)
    create_repository = Mock(return_value=repository)
    create_service = Mock(return_value=service)

    monkeypatch.setattr(app, "create_session_factory", create_sessions)
    monkeypatch.setattr(app, "SQLAlchemyTaskRepository", create_repository)
    monkeypatch.setattr(app, "TaskService", create_service)

    result = app.create_task_service(engine=engine)

    create_sessions.assert_called_once_with(engine)
    create_repository.assert_called_once_with(session_factory)
    create_service.assert_called_once_with(repository)
    assert result is service


def test_create_execution_loop_composes_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = object()
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

    result = app.create_execution_loop(engine=engine)

    create_service.assert_called_once_with(engine=engine)
    create_adapters.assert_called_once_with(service)
    create_dispatcher.assert_called_once_with(adapters)
    create_loop.assert_called_once_with(dispatcher)
    assert result is execution_loop


def test_create_llm_provider_composes_ollama_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("OLLAMA_HOST", "http://ollama.test:11434")
    monkeypatch.setenv("OLLAMA_MODEL", "llama3.2:3b")
    client = object()
    provider = object()
    create_client = Mock(return_value=client)
    create_provider = Mock(return_value=provider)

    monkeypatch.setattr(app, "Client", create_client, raising=False)
    monkeypatch.setattr(app, "OllamaProvider", create_provider, raising=False)

    result = app.create_llm_provider()

    create_client.assert_called_once_with(host="http://ollama.test:11434")
    create_provider.assert_called_once_with(
        client=client,
        model="llama3.2:3b",
    )
    assert result is provider


def test_create_agent_loop_composes_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = object()
    execution_loop = object()
    llm_provider = object()
    tools = object()
    agent_loop = object()
    create_execution = Mock(return_value=execution_loop)
    create_agent = Mock(return_value=agent_loop)

    monkeypatch.setattr(app, "create_execution_loop", create_execution)
    monkeypatch.setattr(app, "TASK_TOOL_DEFINITIONS", tools, raising=False)
    monkeypatch.setattr(app, "AgentLoop", create_agent, raising=False)

    result = app.create_agent_loop(
        engine=engine,
        llm_provider=llm_provider,
    )

    create_execution.assert_called_once_with(engine=engine)
    create_agent.assert_called_once_with(
        llm_provider=llm_provider,
        execution_loop=execution_loop,
        tools=tools,
    )
    assert result is agent_loop


def test_application_close_disposes_engine() -> None:
    engine = Mock()
    llm_provider = Mock()
    agent_loop = Mock()
    application = app.Application(
        engine=engine,
        llm_provider=llm_provider,
        agent_loop=agent_loop,
    )

    application.close()

    llm_provider.close.assert_called_once_with()
    engine.dispose.assert_called_once_with()


def test_application_close_disposes_engine_when_provider_close_fails() -> None:
    engine = Mock()
    llm_provider = Mock()
    llm_provider.close.side_effect = RuntimeError("provider close failed")
    application = app.Application(
        engine=engine,
        llm_provider=llm_provider,
        agent_loop=Mock(),
    )

    with pytest.raises(RuntimeError, match="provider close failed"):
        application.close()

    engine.dispose.assert_called_once_with()


def test_create_application_composes_dependencies(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = object()
    llm_provider = object()
    agent_loop = object()
    application = object()

    load_environment = Mock()
    create_engine = Mock(return_value=engine)
    create_provider = Mock(return_value=llm_provider)
    create_loop = Mock(return_value=agent_loop)
    application_class_init = Mock(return_value=application)

    monkeypatch.setattr(app, "load_application_environment", load_environment)
    monkeypatch.setattr(app, "create_database_engine", create_engine)
    monkeypatch.setattr(app, "create_llm_provider", create_provider)
    monkeypatch.setattr(app, "create_agent_loop", create_loop)
    monkeypatch.setattr(app, "Application", application_class_init)

    result = app.create_application()

    load_environment.assert_called_once_with()
    create_engine.assert_called_once_with()
    create_provider.assert_called_once_with()
    create_loop.assert_called_once_with(
        engine=engine,
        llm_provider=llm_provider,
    )
    application_class_init.assert_called_once_with(
        engine=engine,
        llm_provider=llm_provider,
        agent_loop=agent_loop,
    )
    assert result is application


def test_create_application_disposes_engine_when_composition_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()
    llm_provider = Mock()
    create_loop = Mock(side_effect=RuntimeError("composition failed"))

    monkeypatch.setattr(app, "load_application_environment", Mock())
    monkeypatch.setattr(app, "create_database_engine", Mock(return_value=engine))
    monkeypatch.setattr(
        app,
        "create_llm_provider",
        Mock(return_value=llm_provider),
    )
    monkeypatch.setattr(app, "create_agent_loop", create_loop)

    with pytest.raises(RuntimeError, match="composition failed"):
        app.create_application()

    llm_provider.close.assert_called_once_with()
    engine.dispose.assert_called_once_with()


def test_create_application_disposes_engine_when_provider_creation_fails(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    engine = Mock()

    monkeypatch.setattr(app, "load_application_environment", Mock())
    monkeypatch.setattr(app, "create_database_engine", Mock(return_value=engine))
    monkeypatch.setattr(
        app,
        "create_llm_provider",
        Mock(side_effect=RuntimeError("provider creation failed")),
    )

    with pytest.raises(RuntimeError, match="provider creation failed"):
        app.create_application()

    engine.dispose.assert_called_once_with()


def test_application_context_manager_closes_application() -> None:
    engine = Mock()
    llm_provider = Mock()
    application = app.Application(
        engine=engine,
        llm_provider=llm_provider,
        agent_loop=Mock(),
    )

    with application as entered_application:
        assert entered_application is application

    llm_provider.close.assert_called_once_with()
    engine.dispose.assert_called_once_with()
