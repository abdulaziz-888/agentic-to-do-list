import json
from unittest.mock import Mock

import pytest

from agent.agent_loop import AgentLoop
from agent.execution_loop import ExecutionLoop
from agent.llm_provider import (
    LLMMessage,
    LLMResponse,
    LLMToolCall,
    LLMToolDefinition,
)
from agent.task_tool_definitions import TASK_TOOL_DEFINITIONS


class FakeLLMProvider:
    def __init__(self, responses: list[LLMResponse]) -> None:
        self._responses = iter(responses)
        self.received_calls: list[
            tuple[list[LLMMessage], list[LLMToolDefinition]]
        ] = []

    def chat(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition],
    ) -> LLMResponse:
        self.received_calls.append((list(messages), list(tools)))
        return next(self._responses)


def test_agent_loop_run() -> None:
    llm_response = LLMResponse(
        content="You have no tasks.",
        tool_calls=[],
    )
    fake_provider = FakeLLMProvider([llm_response])
    execution_loop = Mock(spec=ExecutionLoop)
    agent_loop = AgentLoop(
        llm_provider=fake_provider,
        execution_loop=execution_loop,
        tools=TASK_TOOL_DEFINITIONS,
    )

    result = agent_loop.run("What tasks do I have?")

    assert result == "You have no tasks."
    assert fake_provider.received_calls == [
        (
            [
                LLMMessage(
                    role="user",
                    content="What tasks do I have?",
                )
            ],
            TASK_TOOL_DEFINITIONS,
        )
    ]
    execution_loop.execute_tool_calls.assert_not_called()


def test_agent_loop_executes_tool_and_returns_final_response() -> None:
    tool_call = LLMToolCall(
        name="create_task",
        arguments={"title": "Buy milk"},
    )
    fake_provider = FakeLLMProvider(
        [
            LLMResponse(
                content="",
                tool_calls=[tool_call],
            ),
            LLMResponse(
                content="I created the task.",
                tool_calls=[],
            ),
        ]
    )
    tool_result = {
        "id": "task-id",
        "title": "Buy milk",
        "status": "todo",
    }
    execution_loop = Mock(spec=ExecutionLoop)
    execution_loop.execute_tool_calls.return_value = [tool_result]
    agent_loop = AgentLoop(
        llm_provider=fake_provider,
        execution_loop=execution_loop,
        tools=TASK_TOOL_DEFINITIONS,
    )

    result = agent_loop.run("Create a task to buy milk")

    assert result == "I created the task."
    execution_loop.execute_tool_calls.assert_called_once_with(
        [
            {
                "name": "create_task",
                "arguments": {"title": "Buy milk"},
            }
        ]
    )
    assert len(fake_provider.received_calls) == 2
    second_messages, second_tools = fake_provider.received_calls[1]
    assert second_messages == [
        LLMMessage(
            role="user",
            content="Create a task to buy milk",
        ),
        LLMMessage(
            role="assistant",
            content="",
            tool_calls=[tool_call],
        ),
        LLMMessage(
            role="tool",
            content=json.dumps(tool_result),
            tool_name="create_task",
        ),
    ]
    assert second_tools == TASK_TOOL_DEFINITIONS


def test_agent_loop_stops_at_maximum_turns() -> None:
    tool_call = LLMToolCall(
        name="list_tasks",
        arguments={},
    )
    tool_response = LLMResponse(
        content="",
        tool_calls=[tool_call],
    )
    fake_provider = FakeLLMProvider(
        [tool_response, tool_response]
    )
    execution_loop = Mock(spec=ExecutionLoop)
    execution_loop.execute_tool_calls.return_value = [[]]
    agent_loop = AgentLoop(
        llm_provider=fake_provider,
        execution_loop=execution_loop,
        tools=TASK_TOOL_DEFINITIONS,
        max_turns=2,
    )

    with pytest.raises(
        RuntimeError,
        match="Agent exceeded the maximum of 2 turns",
    ):
        agent_loop.run("Keep calling tools")

    assert len(fake_provider.received_calls) == 2
    assert execution_loop.execute_tool_calls.call_count == 2
