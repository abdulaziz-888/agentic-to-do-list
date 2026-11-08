import pytest

from agent.execution_loop import execute_tool_calls
from tools.tasks import tasks


def test_execute_tool_calls_create_list() -> None:
    tool_calls = [
        {
            "name": "create_task",
            "arguments": {
                "title": "Task1",
                "description": "createdfor execute tool_calls"
            }
        },
        {
            "name": "list_tasks",
            "arguments": {}
        }
    ]
    result = execute_tool_calls(tool_calls=tool_calls)
    assert isinstance(result, list)
    assert len(result) == 2
    result_create, result_list = result
    assert result_list == [result_create]


def test_execute_tool_calls_stops_after_failure() -> None:
    tool_calls = [
        {
            "name": "create_task",
            "arguments": {
                "title": "Task1",
                "description": "task 1 description"
            }
        },
        {
            "name": "not a valid tool name",
            "arguments": {}
        },
        {
            "name": "create_task",
            "arguments": {
                "title": "Task2",
                "description": "task 2 description"
            }
        }
    ]
    with pytest.raises(ValueError) as exc_info:
        execute_tool_calls(tool_calls=tool_calls)
    assert str(exc_info.value) == "Unknown tool: not a valid tool name"
    assert len(tasks) == 1


def test_execute_tool_calls_missing_name_or_not_string() -> None:
    error_message = "tool call name is required and must be a string"
    tool_calls_missing_name = [
        {
            "arguments": {}
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        execute_tool_calls(tool_calls=tool_calls_missing_name)
    assert str(exc_info.value) == error_message

    tool_calls_invalid_name = [
        {
            "name": 1121212,
            "arguments": {}
        }
    ]
    with pytest.raises(ValueError) as exc_info:
        execute_tool_calls(tool_calls=tool_calls_invalid_name)
    assert str(exc_info.value) == error_message


def test_execute_tool_calls_missing_arguments_or_not_dict() -> None:
    error_message = "tool call arguments are required and must be a dictionary"
    tool_calls_missing_arguments = [
        {
            "name": "create_task"
        }
    ]

    with pytest.raises(ValueError) as exc_info:
        execute_tool_calls(tool_calls=tool_calls_missing_arguments)
    assert str(exc_info.value) == error_message

    tool_calls_invalid_argument = [
        {
            "name": "create_task",
            "arguments": []
        }
    ]
    with pytest.raises(ValueError) as exc_info:
        execute_tool_calls(tool_calls=tool_calls_invalid_argument)
    assert str(exc_info.value) == error_message
