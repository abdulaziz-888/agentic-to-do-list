import datetime
from uuid import UUID, uuid4

from domains.task import Task, TaskStatus
from repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self._task_repository = task_repository

    def create_task(self, title: str, description: str | None = None) -> Task:
        now = datetime.datetime.now(datetime.UTC)
        task = Task(
            id=uuid4(),
            title=title,
            description=description or "",
            status=TaskStatus.TODO,
            created_at=now,
            updated_at=now,
        )
        self._task_repository.save(task=task)
        return task

    def get_task_by_id(self, task_id: UUID) -> Task | None:
        return self._task_repository.get_by_id(task_id=task_id)

    def list_tasks(self) -> list[Task]:
        return self._task_repository.list_all()
