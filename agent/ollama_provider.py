from ollama import Client

from agent.llm_provider import (
    LLMMessage,
    LLMResponse,
    LLMToolCall,
    LLMToolDefinition,
)


class OllamaProvider:
    def __init__(self, client: Client, model: str) -> None:
        self._client = client
        self._model = model

    @staticmethod
    def llm_message_to_ollama(
        message: LLMMessage,
    ) -> dict[str, object]:
        result: dict[str, object] = {
            "role": message.role,
            "content": message.content,
        }

        if message.tool_calls:
            result["tool_calls"] = OllamaProvider.llm_tool_calls_to_ollama(
                message.tool_calls
            )

        if message.tool_name is not None:
            result["tool_name"] = message.tool_name

        return result

    @staticmethod
    def llm_messages_to_ollama(
        messages: list[LLMMessage],
    ) -> list[dict[str, object]]:
        return [
            OllamaProvider.llm_message_to_ollama(message)
            for message in messages
        ]

    @staticmethod
    def tool_definition_to_ollama(
        definition: LLMToolDefinition,
    ) -> dict[str, object]:
        return {
            "type": "function",
            "function": {
                "name": definition.name,
                "description": definition.description,
                "parameters": definition.parameters,
            },
        }

    @staticmethod
    def tool_definitions_to_ollama(
        definitions: list[LLMToolDefinition],
    ) -> list[dict[str, object]]:
        return [
            OllamaProvider.tool_definition_to_ollama(definition)
            for definition in definitions
        ]

    @staticmethod
    def llm_tool_call_to_ollama(
        tool_call: LLMToolCall,
    ) -> dict[str, object]:
        return {
            "function": {
                "name": tool_call.name,
                "arguments": tool_call.arguments,
            }
        }

    @staticmethod
    def llm_tool_calls_to_ollama(
        tool_calls: list[LLMToolCall],
    ) -> list[dict[str, object]]:
        return [
            OllamaProvider.llm_tool_call_to_ollama(tool_call)
            for tool_call in tool_calls
        ]

    def chat(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition],
    ) -> LLMResponse:
        ollama_messages = self.llm_messages_to_ollama(messages)
        ollama_tools = self.tool_definitions_to_ollama(tools)

        response = self._client.chat(
            model=self._model,
            messages=ollama_messages,
            tools=ollama_tools,
        )

        return LLMResponse(
            content=response.message.content or "",
            tool_calls=[
                LLMToolCall(
                    name=tool_call.function.name,
                    arguments=tool_call.function.arguments,
                )
                for tool_call in response.message.tool_calls or []
            ],
        )
