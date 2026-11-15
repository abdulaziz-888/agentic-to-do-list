import json

from agent.execution_loop import ExecutionLoop
from agent.llm_provider import (
    LLMMessage,
    LLMProvider,
    LLMToolDefinition,
)

DEFAULT_MAX_AGENT_TURNS = 10


class AgentLoop:
    def __init__(
        self,
        llm_provider: LLMProvider,
        execution_loop: ExecutionLoop,
        tools: list[LLMToolDefinition],
        max_turns: int = DEFAULT_MAX_AGENT_TURNS,
    ) -> None:
        self._llm_provider = llm_provider
        self._execution_loop = execution_loop
        self._tools = tools
        self._max_turns = max_turns

    def run(self, user_input: str) -> str:
        messages = [
            LLMMessage(
                role="user",
                content=user_input,
            )
        ]

        for _ in range(self._max_turns):
            response = self._llm_provider.chat(
                messages=messages,
                tools=self._tools,
            )

            messages.append(
                LLMMessage(
                    role="assistant",
                    content=response.content,
                    tool_calls=response.tool_calls,
                )
            )

            if not response.tool_calls:
                return response.content

            execution_calls = [
                {
                    "name": tool_call.name,
                    "arguments": tool_call.arguments,
                }
                for tool_call in response.tool_calls
            ]

            tool_results = self._execution_loop.execute_tool_calls(
                execution_calls
            )

            for tool_call, tool_result in zip(
                response.tool_calls,
                tool_results,
                strict=True,
            ):
                messages.append(
                    LLMMessage(
                        role="tool",
                        content=json.dumps(tool_result),
                        tool_name=tool_call.name,
                    )
                )

        raise RuntimeError(
            f"Agent exceeded the maximum of {self._max_turns} turns"
        )
