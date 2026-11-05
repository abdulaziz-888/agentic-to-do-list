import uuid

import pytest

from domains.task import TaskStatus
from tools.tasks import complete_task, create_task, list_tasks, tasks


def test_create_task() -> None:
    task = create_task("Test Task")
    assert task is not None
    assert task.id is not None
    assert task.title == "Test Task"
    assert task.description == ""
    assert task.status == TaskStatus.TODO
    assert len(tasks) == 1
    assert tasks[task.id] == task


def test_list_tasks() -> None:
    assert len(list_tasks()) == 0
    task1 = create_task("Task 1")
    task2 = create_task("Task 2")
    task3 = create_task("Task 3")
    task_list = list_tasks()
    assert len(task_list) == 3
    assert task_list[0].id == task1.id
    assert task_list[1].id == task2.id
    assert task_list[2].id == task3.id


def test_complete_task() -> None:
    task = create_task("Task 1")
    assert task.status == TaskStatus.TODO
    last_updated = task.updated_at
    completed_task = complete_task(task.id)
    assert completed_task.status == TaskStatus.COMPLETED
    assert completed_task.updated_at > last_updated
    completed_at = completed_task.updated_at
    assert tasks[task.id].status == TaskStatus.COMPLETED
    completed_task2 = complete_task(completed_task.id)
    assert completed_task2.updated_at == completed_at
    assert completed_task2.status == TaskStatus.COMPLETED
    assert tasks[task.id].status == TaskStatus.COMPLETED
    assert tasks[task.id].updated_at == completed_at


def test_complete_task_not_found() -> None:
    task_id = uuid.uuid4()
    with pytest.raises(ValueError) as exc_info:
        complete_task(task_id)
    assert str(exc_info.value) == f"Task with id {task_id} not found"
    assert len(tasks) == 0