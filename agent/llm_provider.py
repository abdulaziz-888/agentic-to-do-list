from dataclasses import dataclass, field
from typing import Literal, Protocol


@dataclass(frozen=True)
class LLMToolCall:
    name: str
    arguments: dict[str, object]


@dataclass(frozen=True)
class LLMMessage:
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    tool_calls: list[LLMToolCall] = field(default_factory=list)
    tool_name: str | None = None


@dataclass(frozen=True)
class LLMToolDefinition:
    name: str
    description: str
    parameters: dict[str, object]


@dataclass(frozen=True)
class LLMResponse:
    content: str
    tool_calls: list[LLMToolCall]


class LLMProvider(Protocol):
    def chat(
        self,
        messages: list[LLMMessage],
        tools: list[LLMToolDefinition],
    ) -> LLMResponse:
        ...
