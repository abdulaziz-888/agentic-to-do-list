import datetime
from uuid import uuid4

from database.task_mapper import record_to_task, task_to_record
from database.task_model import TaskRecord
from domains.task import Task, TaskStatus


def test_task_mapper_task_to_task_record() -> None:
    timestamp_now = datetime.datetime.now(datetime.UTC)
    task_id = uuid4()
    title = "Task1"
    description = "task1 description"
    status = TaskStatus.TODO
    created_at = timestamp_now
    updated_at = timestamp_now

    task_obj = Task(
        id=task_id,
        title=title,
        description=description,
        status=status,
        created_at=created_at,
        updated_at=updated_at,
    )
    assert task_obj.id == task_id
    assert task_obj.title == title
    assert task_obj.description == description
    assert task_obj.status == status
    assert task_obj.created_at == created_at
    assert task_obj.updated_at == updated_at

    task_record_obj = task_to_record(task=task_obj)
    assert isinstance(task_record_obj, TaskRecord)
    assert task_record_obj.id == task_obj.id
    assert task_record_obj.title == task_obj.title
    assert task_record_obj.description == task_obj.description
    assert task_record_obj.status == task_obj.status
    assert task_record_obj.created_at == task_obj.created_at
    assert task_record_obj.updated_at == task_obj.updated_at

    assert task_obj.id == task_id
    assert task_obj.title == title
    assert task_obj.description == description
    assert task_obj.status == status
    assert task_obj.created_at == created_at
    assert task_obj.updated_at == updated_at


def test_task_mapper_record_to_task_restores_utc() -> None:
    timestamp = datetime.datetime(2026, 11, 11, 12, 30)
    record = TaskRecord(
        id=uuid4(),
        title="Task1",
        description="task1 description",
        status=TaskStatus.TODO,
        created_at=timestamp,
        updated_at=timestamp,
    )

    task = record_to_task(record)

    expected_timestamp = timestamp.replace(tzinfo=datetime.UTC)
    assert isinstance(task, Task)
    assert task.id == record.id
    assert task.title == record.title
    assert task.description == record.description
    assert task.status == record.status
    assert task.created_at == expected_timestamp
    assert task.updated_at == expected_timestamp
    assert task.created_at.tzinfo is datetime.UTC
    assert task.updated_at.tzinfo is datetime.UTC
    assert record.created_at.tzinfo is None
    assert record.updated_at.tzinfo is None


def test_task_mapper_record_to_task_normalizes_aware_timestamp() -> None:
    local_timezone = datetime.timezone(datetime.timedelta(hours=5, minutes=30))
    timestamp = datetime.datetime(2026, 11, 11, 12, 30, tzinfo=local_timezone)
    record = TaskRecord(
        id=uuid4(),
        title="Task1",
        description="task1 description",
        status=TaskStatus.TODO,
        created_at=timestamp,
        updated_at=timestamp,
    )

    task = record_to_task(record)

    expected_timestamp = timestamp.astimezone(datetime.UTC)
    assert task.created_at == expected_timestamp
    assert task.updated_at == expected_timestamp
    assert task.created_at.tzinfo is datetime.UTC
    assert task.updated_at.tzinfo is datetime.UTC
    assert record.created_at is timestamp
    assert record.updated_at is timestamp
