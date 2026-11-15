from agent.llm_provider import LLMToolDefinition
from agent.tool_dispatcher import TOOL_COMPLETE_TASK, TOOL_CREATE_TASK, TOOL_LIST_TASKS

CREATE_TASK_DEFINITION = LLMToolDefinition(
    name=TOOL_CREATE_TASK,
    description="Create a new task",
    parameters={
        "type": "object",
        "properties": {
            "title": {"type": "string"},
            "description": {"type": "string"},
        },
        "required": ["title"],
    },
)


LIST_TASKS_DEFINITION = LLMToolDefinition(
    name=TOOL_LIST_TASKS,
    description="List all tasks",
    parameters={
        "type": "object",
        "properties": {},
    },
)


COMPLETE_TASK_DEFINITION = LLMToolDefinition(
    name=TOOL_COMPLETE_TASK,
    description="Mark a task as completed",
    parameters={
        "type": "object",
        "properties": {
            "task_id": {
                "type": "string",
                "format": "uuid",
                "description": "The ID of the task to complete",
            },
        },
        "required": ["task_id"],
    },
)


TASK_TOOL_DEFINITIONS: list[LLMToolDefinition] = [
    CREATE_TASK_DEFINITION,
    LIST_TASKS_DEFINITION,
    COMPLETE_TASK_DEFINITION,
]
