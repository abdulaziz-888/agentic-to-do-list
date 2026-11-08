from uuid import UUID

from domains.task import Task
from tools.tasks import complete_task, create_task, list_tasks


def complete_task_from_arguments(arguments: dict[str, object]) -> dict[str, object]:
    raw_task_id = arguments.get("task_id")
    if not raw_task_id or not isinstance(raw_task_id, str):
        raise ValueError("task_id is required and must be a string")
    try:
        task_id = UUID(raw_task_id)
    except ValueError as exc:
        raise ValueError("task_id must be a valid UUID") from exc
    return task_to_dict(complete_task(task_id))


def create_task_from_arguments(arguments: dict[str, object]) -> dict[str, object]:
    title = arguments.get("title")
    if not isinstance(title, str) or not title.strip():
        raise ValueError("title is required and must be a non-empty string")
    try:
        description = arguments["description"]
    except KeyError:
        description = ""
    if description is None or not isinstance(description, str):
        raise ValueError("description must be a string")
    return task_to_dict(create_task(title, description))


def list_tasks_from_arguments(arguments: dict[str, object]) -> list[dict[str, object]]:
    return tasks_to_dicts(list_tasks())


def task_to_dict(task: Task) -> dict[str, object]:
    return {
        "id": str(task.id),
        "title": task.title,
        "description": task.description,
        "status": task.status.value,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


def tasks_to_dicts(tasks: list[Task]) -> list[dict[str, object]]:
    return list(map(task_to_dict, tasks))
