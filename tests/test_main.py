import json
from unittest.mock import MagicMock, Mock

import pytest

import main


def test_main_lists_tasks_as_json(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    tasks = [{"id": "task-id", "title": "Test task"}]
    execution_loop = Mock()
    execution_loop.execute_tool_calls.return_value = [tasks]
    entered_application = Mock(execution_loop=execution_loop)
    application = MagicMock()
    application.__enter__.return_value = entered_application
    create_application = Mock(return_value=application)
    monkeypatch.setattr(main, "create_application", create_application)

    main.main()

    create_application.assert_called_once_with()
    application.__enter__.assert_called_once_with()
    application.__exit__.assert_called_once_with(None, None, None)
    execution_loop.execute_tool_calls.assert_called_once_with(
        [{"name": "list_tasks", "arguments": {}}]
    )
    assert json.loads(capsys.readouterr().out) == tasks
