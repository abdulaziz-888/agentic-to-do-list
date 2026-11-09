from uuid import uuid4

import pytest

from domains.task import TaskStatus
from services.task_service import TaskService


def test_create_and_get_task(task_service: TaskService) -> None:
    uuid_unknown = uuid4()
    assert task_service.get_task_by_id(uuid_unknown) is None
    task1 = task_service.create_task("Task1")
    assert task1.title == "Task1"
    assert task1.status == TaskStatus.TODO
    assert task1.created_at == task1.updated_at
    returned_task = task_service.get_task_by_id(task1.id)
    assert returned_task is task1


def test_list_task(task_service: TaskService) -> None:
    assert task_service.list_tasks() == []
    task1 = task_service.create_task("Task1")
    task2 = task_service.create_task("Task2")
    assert task_service.list_tasks() == [task1, task2]


def test_complete_task(task_service: TaskService) -> None:
    random_uuid = uuid4()
    with pytest.raises(ValueError) as exc_info:
        task_service.complete_task(random_uuid)
    assert str(exc_info.value) == f"Task with id {random_uuid} not found"

    task1 = task_service.create_task(title="Task1", description="task 1 description")
    before_id = task1.id
    before_updated_at = task1.updated_at
    before_status = task1.status
    task2 = task_service.complete_task(task1.id)
    completed_at = task2.updated_at
    assert task2.id == before_id
    assert completed_at > before_updated_at
    assert task2.status == TaskStatus.COMPLETED
    assert before_status != task2.status
    task3 = task_service.complete_task(task1.id)
    assert completed_at == task3.updated_at
