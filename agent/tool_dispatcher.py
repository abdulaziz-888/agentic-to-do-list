from agent.tool_adapters import (
    complete_task_from_arguments,
    create_task_from_arguments,
    list_tasks_from_arguments,
)

TOOL_CREATE_TASK = "create_task"
TOOL_LIST_TASKS = "list_tasks"
TOOL_COMPLETE_TASK = "complete_task"
TOOL_HANDLERS = {
    TOOL_CREATE_TASK: create_task_from_arguments,
    TOOL_LIST_TASKS: list_tasks_from_arguments,
    TOOL_COMPLETE_TASK: complete_task_from_arguments,
}


def dispatch_tool(
    name: str,
    arguments: dict[str, object],
) -> dict[str, object] | list[dict[str, object]]:
    try:
        handler = TOOL_HANDLERS[name]
    except KeyError:
        raise ValueError(f"Unknown tool: {name}") from None

    return handler(arguments)
