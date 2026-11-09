import pytest

from agent.tool_dispatcher import ToolDispatcher
from domains.task import TaskStatus


def test_dispatch_tool_unknown_name(tool_dispatcher: ToolDispatcher) -> None:
    tool_name = "random"
    with pytest.raises(ValueError) as exc_info:
        tool_dispatcher.dispatch_tool(tool_name, {})
    assert str(exc_info.value) == f"Unknown tool: {tool_name}"


def test_dispatch_tool_valid(tool_dispatcher: ToolDispatcher) -> None:
    result_created = tool_dispatcher.dispatch_tool(
        "create_task",
        {
            "title": "Task1",
            "description": "Created_through dispatcher"
        }
    )
    result_created_id = result_created["id"]
    assert result_created["title"] == "Task1"
    assert result_created["description"] == "Created_through dispatcher"
    assert result_created["status"] == TaskStatus.TODO.value

    result_list = tool_dispatcher.dispatch_tool(
        "list_tasks",
        {}
    )
    assert len(result_list) == 1
    assert result_list == [result_created]

    result_completed = tool_dispatcher.dispatch_tool(
        "complete_task",
        {
            "task_id": result_created_id
        }
    )
    assert result_completed["id"] == result_created_id
    assert result_completed["status"] == TaskStatus.COMPLETED.value

    result_list_2 = tool_dispatcher.dispatch_tool(
        "list_tasks",
        {}
    )
    assert len(result_list_2) == 1
    assert result_list_2 == [result_completed]
