from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class LLMToolCall:
    name: str
    arguments: dict[str, object]


@dataclass(frozen=True)
class LLMResponse:
    content: str
    tool_calls: list[LLMToolCall]


class LLMProvider(Protocol):
    def chat(
        self,
        messages: list[dict[str, str]],
        tools: list[dict[str, object]],
    ) -> LLMResponse:
        ...