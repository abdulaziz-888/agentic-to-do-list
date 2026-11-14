from unittest.mock import Mock

import pytest
from ollama import ChatResponse, Client

from agent.llm_provider import LLMMessage, LLMResponse, LLMToolCall, LLMToolDefinition
from agent.ollama_provider import OllamaProvider
from agent.task_tool_definitions import (
    COMPLETE_TASK_DEFINITION,
    CREATE_TASK_DEFINITION,
    LIST_TASKS_DEFINITION,
    TASK_TOOL_DEFINITIONS,
)


@pytest.mark.parametrize(
    ("message", "converted_message"),
    [
        (
            LLMMessage(
                role="user",
                content="What tasks do I have?",
            ),
            {
                "role": "user",
                "content": "What tasks do I have?",
            },
        ),
        (
            LLMMessage(
                role="assistant",
                content="",
                tool_calls=[
                    LLMToolCall(
                        name="create_task",
                        arguments={"title": "Buy milk"},
                    )
                ],
            ),
            {
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
            },
        ),
        (
            LLMMessage(
                role="tool",
                content='{"title": "Buy milk", "status": "todo"}',
                tool_name="create_task",
            ),
            {
                "role": "tool",
                "content": '{"title": "Buy milk", "status": "todo"}',
                "tool_name": "create_task",
            },
        ),
    ]
)
def test_message_to_ollama(message: LLMMessage, converted_message: dict[str, object]) -> None:
    assert OllamaProvider.llm_message_to_ollama(message) == converted_message


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
    messages = [
        LLMMessage(
            role="user",
            content="What tasks do I have?",
        )
    ]

    result = provider.chat(messages, TASK_TOOL_DEFINITIONS)

    assert result == LLMResponse(
        content="You have no tasks.",
        tool_calls=[],
    )
    client.chat.assert_called_once_with(
        model="llama3.2:3b",
        messages=OllamaProvider.llm_messages_to_ollama(messages),
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
    messages = [
        LLMMessage(
            role="user",
            content="What tasks do I have?",
        )
    ]

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
        messages=OllamaProvider.llm_messages_to_ollama(messages),
        tools=OllamaProvider.tool_definitions_to_ollama(TASK_TOOL_DEFINITIONS),
    )
