import uuid

import pytest

from agent.tool_adapters import complete_task_from_arguments, create_task_from_arguments
from domains.task import TaskStatus
from tools.tasks import create_task, tasks


def test_complete_task_from_arguments() -> None:
    task = create_task("Task 1")
    task_id = task.id
    arguments = {
        "task_id": str(task_id)
    }
    completed_task = complete_task_from_arguments(arguments)
    assert completed_task.id == task_id
    assert completed_task.status == TaskStatus.COMPLETED
    assert tasks[task_id].status == TaskStatus.COMPLETED


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


def test_create_task_from_arguments_no_description() -> None:
    arguments = {
        "title": "Task 1"
    }
    task = create_task_from_arguments(arguments)
    assert task.title == "Task 1"
    assert task.description == ""
    assert task.status == TaskStatus.TODO
    assert tasks[task.id] == task
    