# Project Status

## Goal

Build a personal task-management agent from first principles as a learning
project. The application has explicit domain, persistence, tool, LLM, and
lifecycle boundaries, with Ollama providing local inference without an agent
framework.

## Current learning step

The provider-independent local LLM integration milestone is complete. Neutral
message, response, tool-call, and tool-definition contracts isolate the agent
loop from Ollama. The Ollama adapter translates provider-specific values at its
boundary, while the agent loop coordinates model responses, sequential tool
execution, and tool-result messages.

`main.py` accepts one natural-language query and runs the complete Ollama,
agent-loop, dispatcher, service, and PostgreSQL graph within a context-managed
application. The application owns and closes both the Ollama client and the
SQLAlchemy engine, including cleanup during failed composition.

The live graph has been verified by creating a persisted task and, in separate
CLI invocations, listing it with its UUID, completing it, and listing it again
with `COMPLETED` status. Automated tests remain isolated from local Ollama and
PostgreSQL through fake providers, mocks, and disposable SQLite databases.

## Current structure

- `domains/task.py` defines the `Task` entity and `TaskStatus` enum.
- `repositories/task_repository.py` defines the storage protocol.
- `repositories/in_memory_task_repository.py` and
  `repositories/sqlalchemy_task_repository.py` implement that protocol.
- `database/` owns SQLAlchemy configuration, mapping, and sessions.
- `migrations/` contains the Alembic environment and PostgreSQL migrations.
- `services/task_service.py` owns task creation, listing, lookup, and
  idempotent completion behavior.
- `agent/task_tool_adapters.py` validates JSON-compatible arguments and
  translates task results to JSON-compatible values.
- `agent/tool_dispatcher.py` registers and routes the three task tools.
- `agent/execution_loop.py` validates and executes ordered tool calls.
- `agent/llm_provider.py` defines provider-neutral messages, responses, tool
  calls, tool definitions, and the `LLMProvider` protocol.
- `agent/task_tool_definitions.py` defines the neutral JSON schemas advertised
  for create, list, and complete operations.
- `agent/ollama_provider.py` translates neutral contracts to and from the
  Ollama client and owns client shutdown.
- `agent/agent_loop.py` runs a bounded, single-query model/tool conversation
  until the model returns a response without tool calls.
- `app.py` composes the PostgreSQL execution loop, Ollama provider, and agent
  loop into a lifecycle-owning `Application`.
- `main.py` is the one-query natural-language CLI entry point.
- `.env.example` documents the required database and Ollama settings while the
  real `.env` remains ignored and untracked.

## Key decisions

- Domain objects remain standard-library dataclasses and do not depend on the
  ORM or an external validation framework.
- Business logic depends on a structural repository protocol; database details
  remain behind the repository and mapper boundaries.
- External tool inputs are validated by adapters before reaching typed service
  operations.
- The dispatcher registry is the source of truth for the supported
  `create_task`, `list_tasks`, and `complete_task` names.
- Tool execution is sequential and fail-fast, so later calls observe earlier
  effects and earlier successful effects are not rolled back automatically.
- LLM-facing messages, responses, calls, and tool definitions are neutral
  dataclasses behind an `LLMProvider` protocol. Ollama-specific translation is
  contained in `OllamaProvider`.
- A run is intentionally a single-query operation. Its in-memory messages only
  coordinate tool calls for that query; conversation history and memory are
  not persisted.
- The agent loop stops on a response without tool calls and has a ten-turn
  limit to prevent an unbounded model/tool cycle.
- The `Application` owns the database engine, Ollama provider, and agent loop.
  Shutdown closes the Ollama client and disposes the engine, including during
  partial-composition failures.
- Local configuration comes from `.env`; credentials remain untracked.
- The project CLI is used alongside manually maintained `STATUS.md` to persist,
  list, and complete actionable project work items when local services are
  available.

## Completed milestones

- Built and tested the task domain, in-memory repository, task service, input
  adapters, dispatcher, and deterministic execution loop.
- Added SQLAlchemy persistence while keeping domain and ORM models separate.
- Added Alembic migrations and verified the service/repository graph against
  PostgreSQL.
- Added environment-driven composition and context-managed engine ownership.
- Installed and verified Ollama 0.40.16 and `llama3.2:3b` on the local CPU-only
  development machine, including native structured tool selection.
- Added provider-neutral LLM contracts and fake-provider contract tests.
- Added neutral JSON-schema definitions for all three task operations.
- Added and tested the Ollama adapter, including tool/message translation,
  response conversion, and client cleanup.
- Added and tested the agent loop for direct responses, tool calls, sequential
  results, multiple turns, and the maximum-turn failure path.
- Composed Ollama and the agent loop into the application and changed the CLI
  to accept one natural-language query.
- Verified the real application against Ollama and PostgreSQL by creating,
  listing, and completing a persisted task.

## Current limitations

- Each CLI process handles one user query; there is no interactive session,
  persisted conversation history, or memory.
- The agent exposes only create, list, and complete task operations.
- Small local models may produce inconsistent prose or omit useful identifiers
  unless the user explicitly requests them.

## Next learning step

Choose the next milestone. A useful next step is to improve the single-query
CLI's reliability with a focused system instruction and tests for consistent,
actionable task summaries before considering multi-query sessions or memory.
