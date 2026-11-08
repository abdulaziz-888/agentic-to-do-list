import typing

from agent.tool_dispatcher import dispatch_tool


class ToolCall(typing.TypedDict):
    name: str
    arguments: dict[str, object]


type ToolResult = dict[str, object] | list[dict[str, object]]


def execute_tool_calls(tool_calls: list[ToolCall]) -> list[ToolResult]:
    result = []
    for tool_call in tool_calls:

        if not isinstance((tool_name := tool_call.get("name")), str):
            raise ValueError("tool call name is required and must be a string")

        if not isinstance((tool_arguments := tool_call.get("arguments")), dict):
            raise ValueError("tool call arguments are required and must be a dictionary")

        result.append(dispatch_tool(tool_name, tool_arguments))
    return result