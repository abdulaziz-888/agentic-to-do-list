from unittest.mock import MagicMock, Mock

import pytest

import main


def test_main_runs_single_agent_query(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    read_input = Mock(return_value="Create a task to buy milk")
    agent_loop = Mock()
    agent_loop.run.return_value = "I created the task."
    entered_application = Mock(agent_loop=agent_loop)
    application = MagicMock()
    application.__enter__.return_value = entered_application
    create_application = Mock(return_value=application)
    monkeypatch.setattr("builtins.input", read_input)
    monkeypatch.setattr(main, "create_application", create_application)

    main.main()

    create_application.assert_called_once_with()
    application.__enter__.assert_called_once_with()
    application.__exit__.assert_called_once_with(None, None, None)
    read_input.assert_called_once_with("You: ")
    agent_loop.run.assert_called_once_with("Create a task to buy milk")
    assert capsys.readouterr().out == "I created the task.\n"
