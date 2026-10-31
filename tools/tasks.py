
import datetime
from uuid import UUID, uuid4

from domains.task import Task, TaskStatus

tasks: dict[UUID, Task] = {}



def create_task(
    title: str,
    description: str | None = None,
) -> Task:
    now = datetime.datetime.now(datetime.UTC)
    task = Task(
        id=uuid4(),
        title=title,
        description=description or "",
        status=TaskStatus.TODO,
        created_at=now,
        updated_at=now,
    )
    tasks[task.id] = task
    return task

def list_tasks() -> list[Task]:
    return list(tasks.values())

def get_task(id: UUID) -> Task | None:
    return tasks.get(id)

# only update title and description, status is not allowed to be updated
def update_task(id: UUID, title: str | None = None, description: str | None = None, status: TaskStatus | None = None) -> Task | None:
    task = tasks.get(id)
    if not task:
        raise ValueError(f"Task with id {id} not found")
    if title:
        task.title = title
    if description:
        task.description = description
    task.updated_at = datetime.datetime.now(datetime.UTC)
    tasks[id] = task
    return task


def update_task_status(id: UUID, status: TaskStatus) -> Task | None:
    task = tasks.get(id)
    if not task:
        raise ValueError(f"Task with id {id} not found")
    if status != task.status:
        task.status = status
        task.updated_at = datetime.datetime.now(datetime.UTC)
        tasks[id] = task
    return task

def complete_task(id: UUID) -> Task | None:
    return update_task_status(id, TaskStatus.COMPLETED)

def start_task(id: UUID) -> Task | None:
    return update_task_status(id, TaskStatus.IN_PROGRESS)

def cancel_task(id: UUID) -> Task | None:
    return update_task_status(id, TaskStatus.CANCELLED)

def delete_task(id: UUID) -> None:
    tasks.pop(id, None)
