from uuid import UUID

from domains.task import Task


class SQLAlchemyTaskRepository:
    def save(self, task: Task) -> Task:
        ...

    def get_by_id(self, task_id: UUID) -> Task | None:
        ...

    def list_all(self) -> list[Task]:
        ...