import json
import uuid

import pytest

from agent.task_tool_adapters import TaskToolAdapters
from domains.task import TaskStatus


def test_create_task_from_arguments_valid(task_tool_adapters: TaskToolAdapters) -> None:
    arguments = {
        "title": "Task 1",
        "description": "Description 1"
    }
    task_dict = task_tool_adapters.create_task_from_arguments(arguments)
    assert task_dict["title"] == "Task 1"
    assert task_dict["description"] == "Description 1"
    assert task_dict["status"] == TaskStatus.TODO.value
    stored_tasks = task_tool_adapters.list_tasks_from_arguments({})
    assert len(stored_tasks) == 1
    stored_task = stored_tasks[0]
    assert str(stored_task["id"]) == task_dict["id"]
    assert stored_task["title"] == task_dict["title"]
    assert stored_task["description"] == task_dict["description"]
    assert stored_task["status"] == task_dict["status"]
    assert stored_task["created_at"] == task_dict["created_at"]
    assert stored_task["updated_at"] == task_dict["updated_at"]
    json.dumps(task_dict)


def test_list_tasks_from_arguments(task_tool_adapters: TaskToolAdapters) -> None:
    assert task_tool_adapters.list_tasks_from_arguments({}) == []
    task1_dict = task_tool_adapters.create_task_from_arguments(
        {
            "title": "Task1",
            "description": "task 1 description"
        }
    )
    assert task_tool_adapters.list_tasks_from_arguments({}) == [task1_dict]


def test_complete_task_from_arguments(task_tool_adapters: TaskToolAdapters) -> None:
    task1_dict = task_tool_adapters.create_task_from_arguments({
        "title": "Task1",
        "description": "description for task1"
    })
    assert task1_dict["status"] == TaskStatus.TODO.value
    assert task_tool_adapters.list_tasks_from_arguments({}) == [task1_dict]
    task1_id = task1_dict["id"]
    complete_task_dict = task_tool_adapters.complete_task_from_arguments({
        "task_id": task1_id
    })
    assert task1_id == complete_task_dict["id"]
    assert complete_task_dict["status"] == TaskStatus.COMPLETED.value

    assert task_tool_adapters.list_tasks_from_arguments({}) == [complete_task_dict]


@pytest.mark.parametrize(
    "arguments",
    [
        {},
        {"task_id": None},
        {"task_id": 122232},
    ],
)
def test_complete_task_from_arguments_requires_string_task_id(
    task_tool_adapters: TaskToolAdapters,
    arguments: dict[str, object],
) -> None:
    with pytest.raises(ValueError) as exc_info:
        task_tool_adapters.complete_task_from_arguments(arguments)

    assert str(exc_info.value) == "task_id is required and must be a string"


def test_complete_task_from_arguments_rejects_invalid_uuid(
    task_tool_adapters: TaskToolAdapters,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        task_tool_adapters.complete_task_from_arguments(
            {"task_id": "not a valid UUID"}
        )

    assert str(exc_info.value) == "task_id must be a valid UUID"


def test_complete_task_from_arguments_rejects_unknown_task(
    task_tool_adapters: TaskToolAdapters,
) -> None:
    task_id = uuid.uuid4()

    with pytest.raises(ValueError) as exc_info:
        task_tool_adapters.complete_task_from_arguments(
            {"task_id": str(task_id)}
        )

    assert str(exc_info.value) == f"Task with id {task_id} not found"


@pytest.mark.parametrize(
    "arguments",
    [
        {"description": "Description 1"},
        {"title": " ", "description": "Description 1"},
        {"title": 123, "description": "Description 1"},
    ],
)
def test_create_task_from_arguments_requires_non_empty_string_title(
    task_tool_adapters: TaskToolAdapters,
    arguments: dict[str, object],
) -> None:
    with pytest.raises(ValueError) as exc_info:
        task_tool_adapters.create_task_from_arguments(arguments)

    assert str(exc_info.value) == "title is required and must be a non-empty string"
    assert task_tool_adapters.list_tasks_from_arguments({}) == []


@pytest.mark.parametrize("description", [None, 123])
def test_create_task_from_arguments_requires_string_description(
    task_tool_adapters: TaskToolAdapters,
    description: object,
) -> None:
    with pytest.raises(ValueError) as exc_info:
        task_tool_adapters.create_task_from_arguments(
            {"title": "Task 1", "description": description}
        )

    assert str(exc_info.value) == "description must be a string"
    assert task_tool_adapters.list_tasks_from_arguments({}) == []


def test_create_task_from_arguments_defaults_description(
    task_tool_adapters: TaskToolAdapters,
) -> None:
    task_dict = task_tool_adapters.create_task_from_arguments(
        {"title": "Task 1"}
    )

    assert task_dict["description"] == ""
    assert task_tool_adapters.list_tasks_from_arguments({}) == [task_dict]
