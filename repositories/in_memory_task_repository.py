from uuid import UUID

from domains.task import Task


class InMemoryTaskRepository:
    def __init__(self) -> None:
        self._tasks: dict[UUID, Task] = {}

    def save(self, task: Task) -> Task:
        task_id = task.id
        self._tasks[task_id] = task
        return self._tasks[task_id]

    def get_by_id(self, task_id: UUID) -> Task | None:
        return self._tasks.get(task_id)

    def list_all(self) -> list[Task]:
        return list(self._tasks.values())
