from agent.task_tool_adapters import TaskToolAdapters


TOOL_CREATE_TASK = "create_task"
TOOL_LIST_TASKS = "list_tasks"
TOOL_COMPLETE_TASK = "complete_task"


class ToolDispatcher:
    def __init__(self, task_tool_adapters: TaskToolAdapters) -> None:
        self._task_tool_adapters = task_tool_adapters
        self._tool_handlers = {
            TOOL_CREATE_TASK: self._task_tool_adapters.create_task_from_arguments,
            TOOL_LIST_TASKS: self._task_tool_adapters.list_tasks_from_arguments,
            TOOL_COMPLETE_TASK: self._task_tool_adapters.complete_task_from_arguments,
        }

    def dispatch_tool(
        self,
        name: str,
        arguments: dict[str, object],
    ) -> dict[str, object] | list[dict[str, object]]:
        try:
            handler = self._tool_handlers[name]
        except KeyError:
            raise ValueError(f"Unknown tool: {name}") from None

        return handler(arguments)
