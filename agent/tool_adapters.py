from uuid import UUID

from domains.task import Task
from tools.tasks import complete_task, create_task


def complete_task_from_arguments(arguments: dict[str, object]) -> Task:
    raw_task_id = arguments.get("task_id")
    if not raw_task_id or not isinstance(raw_task_id, str):
        raise ValueError("task_id is required and must be a string")
    try:
        task_id = UUID(raw_task_id)
    except ValueError as exc:
        raise ValueError("task_id must be a valid UUID") from exc
    return complete_task(task_id)


def create_task_from_arguments(arguments: dict[str, object]) -> Task:
    title = arguments.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title is required and must be a non-empty string")
    try:
        description = arguments["description"]
    except KeyError:
        description = ""
    if description is None or not isinstance(description, str):
        raise ValueError("description must be a string")
    return create_task(title, description)