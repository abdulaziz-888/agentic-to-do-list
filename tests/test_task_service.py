from uuid import uuid4

from domains.task import TaskStatus
from services.task_service import TaskService


def test_create_and_get_task(task_service: TaskService) -> None:
    uuid_unknown = uuid4()
    assert task_service.get_task_by_id(uuid_unknown) is None
    task1 = task_service.create_task("Task1")
    assert task1.title == "Task1"
    assert task1.status == TaskStatus.TODO
    returned_task = task_service.get_task_by_id(task1.id)
    assert returned_task is task1


def test_list_task(task_service: TaskService) -> None:
    assert task_service.list_tasks() == []
    task1 = task_service.create_task("Task1")
    task2 = task_service.create_task("Task2")
    assert task_service.list_tasks() == [task1, task2]
