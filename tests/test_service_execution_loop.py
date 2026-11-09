import pytest

from agent.execution_loop import ExecutionLoop


def test_execute_tool_calls_create_list(execution_loop: ExecutionLoop) -> None:
    tool_calls = [
        {
            "name": "create_task",
            "arguments": {
                "title": "Task1",
                "description": "createdfor execute tool_calls"
            }
        },
        {
            "name": "create_task",
            "arguments": {
                "title": "Task2",
                "description": "task 2 description"
            }
        },
        {
            "name": "list_tasks",
            "arguments": {}
        }
    ]
    result = execution_loop.execute_tool_calls(tool_calls=tool_calls)
    assert isinstance(result, list)
    assert len(result) == 3
    result_create1, result_create2, result_list = result
    assert result_list == [result_create1, result_create2]


def test_execute_tool_calls_stops_after_failure(execution_loop: ExecutionLoop) -> None:
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
        execution_loop.execute_tool_calls(tool_calls=tool_calls)
    assert str(exc_info.value) == "Unknown tool: not a valid tool name"
    tool_calls_list = [
        {
            "name": "list_tasks",
            "arguments": {}
        }
    ]
    result_list_after_error = execution_loop.execute_tool_calls(tool_calls=tool_calls_list)
    assert len(result_list_after_error[0]) == 1


@pytest.mark.parametrize(
    ("tool_calls", "error_message"),
    [
        (
            [{"arguments": {}}],
            "tool call name is required and must be a string",
        ),
        (
            [{"name": 1121212, "arguments": {}}],
            "tool call name is required and must be a string",
        ),
        (
            [{"name": "create_task"}],
            "tool call arguments are required and must be a dictionary",
        ),
        (
            [{"name": "create_task", "arguments": []}],
            "tool call arguments are required and must be a dictionary",
        ),
    ],
)
def test_execute_tool_calls_bad_arguments(
    execution_loop: ExecutionLoop,
    tool_calls: list[dict[str, object]],
    error_message: str,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        execution_loop.execute_tool_calls(tool_calls=tool_calls)
    assert str(exc_info.value) == error_message
