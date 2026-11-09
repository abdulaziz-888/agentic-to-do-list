import datetime
from uuid import UUID, uuid4

from domains.task import Task, TaskStatus
from repositories.task_repository import TaskRepository


class TaskService:
    def __init__(self, task_repository: TaskRepository) -> None:
        self._task_repository = task_repository

    @staticmethod
    def get_now() -> datetime.datetime:
        return datetime.datetime.now(datetime.UTC)

    def create_task(self, title: str, description: str | None = None) -> Task:
        timestamp_now = TaskService.get_now()
        task = Task(
            id=uuid4(),
            title=title,
            description=description or "",
            status=TaskStatus.TODO,
            created_at=timestamp_now,
            updated_at=timestamp_now,
        )
        self._task_repository.save(task=task)
        return task

    def get_task_by_id(self, task_id: UUID) -> Task | None:
        return self._task_repository.get_by_id(task_id=task_id)

    def list_tasks(self) -> list[Task]:
        return self._task_repository.list_all()

    def complete_task(self, task_id: UUID) -> Task:
        if not (task := self._task_repository.get_by_id(task_id=task_id)):
            raise ValueError(f"Task with id {task_id} not found")

        if task.status != TaskStatus.COMPLETED:
            task.status = TaskStatus.COMPLETED
            task.updated_at = TaskService.get_now()
            return self._task_repository.save(task=task)

        return task
