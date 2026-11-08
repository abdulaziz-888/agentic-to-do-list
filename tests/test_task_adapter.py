import json
import uuid

import pytest

from agent.tool_adapters import (
    complete_task_from_arguments,
    create_task_from_arguments,
    list_tasks_from_arguments,
    task_to_dict,
    tasks_to_dicts,
)
from domains.task import TaskStatus
from tools.tasks import create_task, tasks


def test_complete_task_from_arguments() -> None:
    task = create_task("Task 1")
    task_id = task.id
    arguments = {
        "task_id": str(task_id)
    }
    completed_task = complete_task_from_arguments(arguments)
    assert completed_task["id"] == str(task_id)
    assert completed_task["status"] == TaskStatus.COMPLETED.value
    json.dumps(completed_task)
    stored_task = tasks[task_id]
    assert stored_task.status == TaskStatus.COMPLETED
    assert stored_task.status.value == completed_task["status"]


def test_complete_task_from_arguments_invalid_uuid() -> None:
    arguments_bad = {
        "task_id": "not a valid UUID"
    }
    with pytest.raises(ValueError) as exc_info:
        complete_task_from_arguments(arguments_bad)
    assert str(exc_info.value) == "task_id must be a valid UUID"


def test_complete_task_from_arguments_task_id_none() -> None:
    arguments_task_id_none = {
        "task_id": None
    }
    with pytest.raises(ValueError) as exc_info:
        complete_task_from_arguments(arguments_task_id_none)
    assert str(exc_info.value) == "task_id is required and must be a string"


def test_complete_task_from_arguments_task_id_missing() -> None:
    arguments_task_id_missing = {
        "not_task_id": "123e4567-e89b-12d3-a456-426614174000"
    }
    with pytest.raises(ValueError) as exc_info:
        complete_task_from_arguments(arguments_task_id_missing)
    assert str(exc_info.value) == "task_id is required and must be a string"


def test_complete_task_from_arguments_task_id_not_found() -> None:
    task_id = uuid.uuid4()
    arguments_task_id_not_found = {
        "task_id": str(task_id)
    }
    with pytest.raises(ValueError) as exc_info:
        complete_task_from_arguments(arguments_task_id_not_found)
    assert str(exc_info.value) == f"Task with id {task_id} not found"


def test_complete_task_from_arguments_task_id_not_string() -> None:
    task_id = 122232
    arguments_task_id_not_string = {
        "task_id": task_id
    }
    with pytest.raises(ValueError) as exc_info:
        complete_task_from_arguments(arguments_task_id_not_string)
    assert str(exc_info.value) == "task_id is required and must be a string"


def test_create_task_from_arguments_no_title() -> None:
    arguments = {
        "description": "Description 1"
    }
    with pytest.raises(ValueError) as exc_info:
        create_task_from_arguments(arguments)
    assert tasks == {}
    assert str(exc_info.value) == "title is required and must be a non-empty string"


def test_create_task_from_arguments_title_empty() -> None:
    arguments = {
        "title": " ",
        "description": "Description 1"
    }
    with pytest.raises(ValueError) as exc_info:
        create_task_from_arguments(arguments)
    assert tasks == {}
    assert str(exc_info.value) == "title is required and must be a non-empty string"


def test_create_task_from_arguments_title_not_string() -> None:
    arguments = {
        "title": 123,
        "description": "Description 1"
    }
    with pytest.raises(ValueError) as exc_info:
        create_task_from_arguments(arguments)
    assert tasks == {}
    assert str(exc_info.value) == "title is required and must be a non-empty string"


def test_create_task_from_arguments_no_description() -> None:
    arguments = {
        "title": "Task 1"
    }
    task_dict = create_task_from_arguments(arguments)
    assert task_dict["title"] == "Task 1"
    assert task_dict["description"] == ""
    assert task_dict["status"] == TaskStatus.TODO.value
    stored_task = tasks[uuid.UUID(task_dict["id"])]
    assert str(stored_task.id) == task_dict["id"]
    assert stored_task.title == task_dict["title"]
    assert stored_task.description == task_dict["description"]
    assert stored_task.status.value == task_dict["status"]
    assert stored_task.created_at.isoformat() == task_dict["created_at"]
    assert stored_task.updated_at.isoformat() == task_dict["updated_at"]
    json.dumps(task_dict)


def test_create_task_from_arguments_description_not_string() -> None:
    arguments = {
        "title": "Task 1",
        "description": 123
    }
    with pytest.raises(ValueError) as exc_info:
        create_task_from_arguments(arguments)
    assert tasks == {}
    assert str(exc_info.value) == "description must be a string"


def test_create_task_from_arguments_description_none() -> None:
    arguments = {
        "title": "Task 1",
        "description": None
    }
    with pytest.raises(ValueError) as exc_info:
        create_task_from_arguments(arguments)
    assert tasks == {}
    assert str(exc_info.value) == "description must be a string"


def test_create_task_from_arguments_valid() -> None:
    arguments = {
        "title": "Task 1",
        "description": "Description 1"
    }
    task_dict = create_task_from_arguments(arguments)
    assert task_dict["title"] == "Task 1"
    assert task_dict["description"] == "Description 1"
    assert task_dict["status"] == TaskStatus.TODO.value
    stored_task = tasks[uuid.UUID(task_dict["id"])]
    assert str(stored_task.id) == task_dict["id"]
    assert stored_task.title == task_dict["title"]
    assert stored_task.description == task_dict["description"]
    assert stored_task.status.value == task_dict["status"]
    assert stored_task.created_at.isoformat() == task_dict["created_at"]
    assert stored_task.updated_at.isoformat() == task_dict["updated_at"]
    json.dumps(task_dict)
    assert len(tasks) == 1


def test_task_to_dict() -> None:
    task = create_task("Task 1")
    task_dict = task_to_dict(task)
    assert task_dict["id"] == str(task.id)
    assert task_dict["title"] == task.title
    assert task_dict["description"] == task.description
    assert task_dict["status"] == task.status.value
    assert task_dict["created_at"] == task.created_at.isoformat()
    assert task_dict["updated_at"] == task.updated_at.isoformat()
    json.dumps(task_dict)


def test_tasks_to_dicts() -> None:
    task_dicts_empty = tasks_to_dicts([])
    assert isinstance(task_dicts_empty, list)
    assert len(task_dicts_empty) == 0
    task1 = create_task("Task 1")
    task_dicts_single = tasks_to_dicts([task1])
    assert len(task_dicts_single) == 1
    assert task_dicts_single[0] == task_to_dict(task1)
    task2 = create_task("Task2")
    task_dicts_multiple = tasks_to_dicts([task1, task2])
    assert len(task_dicts_multiple) == 2
    assert task_dicts_multiple[0] == task_to_dict(task1)
    assert task_dicts_multiple[1] == task_to_dict(task2)
    task_dicts_multiple2 = tasks_to_dicts([task2, task1])
    assert len(task_dicts_multiple2) == 2
    assert task_dicts_multiple2[0] == task_to_dict(task2)
    assert task_dicts_multiple2[1] == task_to_dict(task1)


def test_list_tasks_from_arguments() -> None:
    assert list_tasks_from_arguments({}) == []
    task1 = create_task("Task1")
    task2 = create_task("Task2")
    list_tasks_dict = list_tasks_from_arguments({"ignored": True})
    assert len(list_tasks_dict) == 2
    task1_dict = list_tasks_dict[0]
    task2_dict = list_tasks_dict[1]
    assert task1_dict == task_to_dict(task1)
    assert task2_dict == task_to_dict(task2)
    json.dumps(list_tasks_dict)
