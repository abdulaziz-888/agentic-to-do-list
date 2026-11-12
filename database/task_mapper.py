import datetime

from database.task_model import TaskRecord
from domains.task import Task


def task_to_record(task: Task) -> TaskRecord:
    return TaskRecord(
        id=task.id,
        title=task.title,
        description=task.description,
        status=task.status,
        created_at=task.created_at,
        updated_at=task.updated_at,
    )


def record_to_task(record: TaskRecord) -> Task:
    return Task(
        id=record.id,
        title=record.title,
        description=record.description,
        status=record.status,
        created_at=_as_utc(record.created_at),
        updated_at=_as_utc(record.updated_at),
    )


def _as_utc(value: datetime.datetime) -> datetime.datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=datetime.UTC)

    return value.astimezone(datetime.UTC)
