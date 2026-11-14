from agent.llm_provider import LLMProvider, LLMResponse, LLMToolCall, LLMToolDefinition
from agent.task_tool_definitions import TASK_TOOL_DEFINITIONS


class FakeLLMProvider:
    def __init__(self, llm_response: LLMResponse) -> None:
        self.llm_response = llm_response
        self.received_messages: list[dict[str, str]]
        self.received_tools: list[LLMToolDefinition]

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[LLMToolDefinition],
    ) -> LLMResponse:
        self.received_messages = messages
        self.received_tools = tools
        return self.llm_response


def test_llm_provider_chat_contract() -> None:
    messages = [{"role": "user", "content": "Create a task to buy milk"}]

    tools = TASK_TOOL_DEFINITIONS

    response = LLMResponse(
        content="",
        tool_calls=[
            LLMToolCall(
                name="create_task",
                arguments={"title": "Buy milk"},
            )
        ],
    )

    fake_provider = FakeLLMProvider(response)
    provider: LLMProvider = fake_provider

    result = provider.chat(messages, tools)

    assert result == response
    assert fake_provider.received_messages == messages
    assert fake_provider.received_tools == tools

    assert result.tool_calls[0].name == "create_task"
    assert result.tool_calls[0].arguments == {"title": "Buy milk"}


def test_llm_provider_text_response() -> None:
    response = LLMResponse(
        content="You have no tasks.",
        tool_calls=[],
    )
    messages = [{"role": "user", "content": "What tasks do I have?"}]
    fake_provider = FakeLLMProvider(response)
    provider: LLMProvider = fake_provider

    result = provider.chat(messages, [])

    assert result.content == "You have no tasks."
    assert result.tool_calls == []
    assert fake_provider.received_messages == messages
    assert fake_provider.received_tools == []
