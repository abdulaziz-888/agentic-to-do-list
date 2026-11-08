import datetime
from uuid import uuid4

from domains.task import Task, TaskStatus
from repositories.in_memory_task_repository import InMemoryTaskRepository


def test_in_memory_task_repository_save_and_get(task_repository: InMemoryTaskRepository) -> None:
    now = datetime.datetime.now(datetime.UTC)
    task1 = Task(
        id=uuid4(),
        title="Task1",
        description="",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )
    task_id = task1.id
    assert task_repository.get_by_id(task_id) is None
    task_repository.save(task1)
    assert task_repository.get_by_id(task_id=task_id) is task1


def test_in_memory_task_repository_list_all(task_repository: InMemoryTaskRepository) -> None:
    assert task_repository.list_all() == []

    now = datetime.datetime.now(datetime.UTC)
    task1 = Task(
        id=uuid4(),
        title="Task1",
        description="",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )
    task_repository.save(task1)

    now = datetime.datetime.now(datetime.UTC)
    task2 = Task(
        id=uuid4(),
        title="Task1",
        description="",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )
    task_repository.save(task2)
    result = task_repository.list_all()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] is task1
    assert result[1] is task2

    result.clear()
    assert result == []
    result = task_repository.list_all()
    assert isinstance(result, list)
    assert len(result) == 2
    assert result[0] is task1
    assert result[1] is task2


def test_in_memory_task_repository_save_replace(task_repository: InMemoryTaskRepository) -> None:
    now = datetime.datetime.now(datetime.UTC)
    task1 = Task(
        id=uuid4(),
        title="Task1",
        description="",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )
    task_repository.save(task1)
    assert task_repository.get_by_id(task1.id) is task1
    assert task_repository.list_all() == [task1]

    now = datetime.datetime.now(datetime.UTC)
    task2 = Task(
        id=task1.id,
        title="Task1",
        description="",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )
    task_repository.save(task2)
    assert task_repository.get_by_id(task1.id) is task2
    assert task_repository.list_all() == [task2]
