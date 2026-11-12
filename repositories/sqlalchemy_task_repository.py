from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session, sessionmaker

from database.task_mapper import record_to_task, task_to_record
from database.task_model import TaskRecord
from domains.task import Task


class SQLAlchemyTaskRepository:
    def __init__(self, session_factory: sessionmaker[Session]) -> None:
        self._session_factory = session_factory

    def save(self, task: Task) -> Task:
        task_record = task_to_record(task)

        with self._session_factory.begin() as session:
            managed_record = session.merge(task_record)
            session.flush()
            saved_task = record_to_task(managed_record)

        return saved_task

    def get_by_id(self, task_id: UUID) -> Task | None:
        with self._session_factory() as session:
            record = session.get(TaskRecord, task_id)
            return record_to_task(record) if record is not None else None

    def list_all(self) -> list[Task]:
        statement = select(TaskRecord).order_by(
            TaskRecord.created_at,
            TaskRecord.id,
        )

        with self._session_factory() as session:
            records = session.scalars(statement).all()
            return [record_to_task(record) for record in records]
