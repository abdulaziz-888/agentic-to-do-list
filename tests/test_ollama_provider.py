from unittest.mock import Mock

import pytest
from ollama import ChatResponse, Client

from agent.llm_provider import LLMResponse, LLMToolCall, LLMToolDefinition
from agent.ollama_provider import OllamaProvider
from agent.task_tool_definitions import (
    COMPLETE_TASK_DEFINITION,
    CREATE_TASK_DEFINITION,
    LIST_TASKS_DEFINITION,
    TASK_TOOL_DEFINITIONS,
)


@pytest.mark.parametrize(
    "definition",
    [
        CREATE_TASK_DEFINITION,
        LIST_TASKS_DEFINITION,
        COMPLETE_TASK_DEFINITION,
    ],
)
def test_tool_definition_to_ollama(definition: LLMToolDefinition) -> None:
    result = OllamaProvider.tool_definition_to_ollama(definition)

    assert result == {
        "type": "function",
        "function": {
            "name": definition.name,
            "description": definition.description,
            "parameters": definition.parameters,
        },
    }


def test_chat_returns_text_response() -> None:
    client = Mock(spec=Client)
    client.chat.return_value = ChatResponse(
        message={
            "role": "assistant",
            "content": "You have no tasks.",
        }
    )
    provider = OllamaProvider(client=client, model="llama3.2:3b")
    messages = [{"role": "user", "content": "What tasks do I have?"}]

    result = provider.chat(messages, TASK_TOOL_DEFINITIONS)

    assert result == LLMResponse(
        content="You have no tasks.",
        tool_calls=[],
    )
    client.chat.assert_called_once_with(
        model="llama3.2:3b",
        messages=messages,
        tools=OllamaProvider.tool_definitions_to_ollama(TASK_TOOL_DEFINITIONS),
    )


def test_chat_returns_tool_response() -> None:
    client = Mock(spec=Client)
    client.chat.return_value = ChatResponse(
        message={
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "create_task",
                        "arguments": {"title": "Buy milk"},
                    }
                }
            ],
        }
    )
    provider = OllamaProvider(client=client, model="llama3.2:3b")
    messages = [{"role": "user", "content": "What tasks do I have?"}]

    result = provider.chat(messages, TASK_TOOL_DEFINITIONS)

    assert result == LLMResponse(
        content="",
        tool_calls=[
            LLMToolCall(
                name="create_task",
                arguments={"title": "Buy milk"},
            )
        ],
    )
    client.chat.assert_called_once_with(
        model="llama3.2:3b",
        messages=messages,
        tools=OllamaProvider.tool_definitions_to_ollama(TASK_TOOL_DEFINITIONS),
    )
