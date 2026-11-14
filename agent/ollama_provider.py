from ollama import Client

from agent.llm_provider import (
    LLMResponse,
    LLMToolCall,
    LLMToolDefinition,
)


class OllamaProvider:
    def __init__(self, client: Client, model: str) -> None:
        self._client = client
        self._model = model

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

    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[LLMToolDefinition],
    ) -> LLMResponse:
        ollama_tools = self.tool_definitions_to_ollama(tools)

        response = self._client.chat(
            model=self._model,
            messages=messages,
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
