import typing

from agent.tool_dispatcher import ToolDispatcher


class ToolCall(typing.TypedDict):
    name: str
    arguments: dict[str, object]


type ToolResult = dict[str, object] | list[dict[str, object]]


class ExecutionLoop:
    def __init__(self, tool_dispatcher: ToolDispatcher) -> None:
        self._tool_dispatcher = tool_dispatcher

    def execute_tool_calls(self, tool_calls: list[ToolCall]) -> list[ToolResult]:
        result = []
        for tool_call in tool_calls:
            if not isinstance((tool_name := tool_call.get("name")), str):
                raise ValueError("tool call name is required and must be a string")

            if not isinstance((tool_arguments := tool_call.get("arguments")), dict):
                raise ValueError("tool call arguments are required and must be a dictionary")

            result.append(self._tool_dispatcher.dispatch_tool(tool_name, tool_arguments))
        return result
