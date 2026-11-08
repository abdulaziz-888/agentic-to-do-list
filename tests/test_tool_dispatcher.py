import uuid

import pytest

from agent.tool_dispatcher import dispatch_tool
from domains.task import TaskStatus
from tools.tasks import create_task, tasks


def test_dispatch_tool_unknown_name() -> None:
    tool_name = "random"
    with pytest.raises(ValueError) as exc_info:
        dispatch_tool(tool_name, {})
    assert str(exc_info.value) == f"Unknown tool: {tool_name}"


def test_dispatch_tool_create_task() -> None:
    tool_name = "create_task"
    result = dispatch_tool(
        tool_name,
        {
            "title": "Task1",
            "description": "Created_through dispatcher"
        }
    )
    assert uuid.UUID(result["id"]) in tasks
    assert result["title"] == "Task1"
    assert result["description"] == "Created_through dispatcher"
    assert result["status"] == TaskStatus.TODO.value
    assert len(tasks) == 1


def test_dispatch_tool_list_tasks() -> None:
    tool_name = "list_tasks"
    result = dispatch_tool(
        tool_name,
        {}
    )
    assert result == []
    create_task("Task1", "Created from dispatcher first")
    create_task("Task2", "Created from dispatcher second")
    result_multiple = dispatch_tool(
        tool_name,
        {}
    )
    assert len(result_multiple) == 2
    assert isinstance(result_multiple, list)


def test_dispatch_tool_complete_task() -> None:
    tool_name = "complete_task"
    task = create_task("Title")
    task_id = str(task.id)
    result = dispatch_tool(
        tool_name,
        {
            "task_id": task_id
        }
    )

    assert result["id"] == task_id
    assert result["title"] == "Title"
    assert result["description"] == ""
    assert result["status"] == TaskStatus.COMPLETED.value
    assert task.status == TaskStatus.COMPLETED
