# Project Status

## Goal

Build a personal task-management agent from first principles as a learning
project. The initial implementation uses plain Python and in-memory storage;
LLM integration and agent frameworks are intentionally out of scope for now.

## Current learning step

Step 6 is complete: SQLAlchemy now provides a SQLite-backed implementation of
the existing task repository contract. ORM records, session construction, and
domain mapping remain outside the domain and service layers, and the unchanged
`TaskService` has been verified against the SQL repository.

The current SQL tests use disposable in-memory SQLite databases. Durable
file-based SQLite configuration and Alembic schema versioning are intentionally
deferred until the SQL repository behavior is stable and understood.

Dedicated pytest instruction is complete. Automated tests will continue to be
added as normal development work, but unit testing is no longer a separate
learning objective.

The core operations under consideration are:

- Create a task.
- List tasks.
- Complete a task.

## Current structure

- `domains/task.py` defines the `Task` domain entity and `TaskStatus` enum.
- `repositories/task_repository.py` defines the storage contract as a
  `Protocol` with save, lookup, and ordered-list operations.
- `repositories/in_memory_task_repository.py` implements that contract with a
  private dictionary keyed by task UUID.
- `repositories/sqlalchemy_task_repository.py` implements the same contract
  with short-lived SQLAlchemy sessions and explicit list ordering.
- `database/base.py` defines the SQLAlchemy declarative base.
- `database/task_model.py` defines the database-only `TaskRecord` mapping.
- `database/task_mapper.py` translates between ORM records and domain tasks,
  including UTC normalization at the persistence boundary.
- `database/session.py` creates session factories bound to injected engines.
- `services/task_service.py` owns task creation, retrieval, listing, and
  idempotent completion behavior.
- `agent/task_tool_adapters.py` validates JSON-compatible arguments, delegates
  to `TaskService`, and serializes domain tasks into JSON-compatible values.
- `agent/tool_dispatcher.py` owns the external tool-name registry and routes
  calls through an injected `TaskToolAdapters` instance.
- `agent/execution_loop.py` validates and executes ordered calls through an
  injected `ToolDispatcher`.
- `tests/conftest.py` composes a fresh repository, service, adapter,
  dispatcher, and execution loop for each test that requests them.
- Repository, service, adapter, dispatcher, and execution-loop tests cover
  each layer through its public behavior.

## Decisions made

- `Task` is a standard-library dataclass. It no longer inherits from
  Pydantic's `BaseModel` because runtime boundary validation is not needed at
  this stage.
- The richer task model is being retained: UUID, title, description, status,
  and creation/update timestamps.
- The creation operation remains named `create_task` rather than `add_task`.
- Callers cannot select the initial status. `create_task` always creates tasks
  with `TaskStatus.TODO`, preserving the invariant that status changes happen
  through explicit status operations.
- UUID generation and timestamps are handled by `create_task`, not by the
  domain model.
- Tool functions expect actual `UUID` objects. Python type annotations do not
  convert string IDs at runtime; string validation and conversion will belong
  at the future external-input boundary.
- Repeating a status update with the current status is a no-op. In particular,
  completing an already-completed task preserves `updated_at`, making the
  operation idempotent.
- Boundary adapters keep external validation and conversion separate from the
  typed task operations.
- Task titles must be non-empty strings and cannot contain only whitespace.
- An omitted description becomes an empty string; an explicitly supplied
  description must be a string.
- External task results represent UUIDs, statuses, and timestamps as strings.
- The typed task operations and in-memory store continue to use `UUID`,
  `TaskStatus`, and `datetime` objects internally.
- All three core adapters share the same arguments-dictionary interface;
  list-task arguments are currently accepted and ignored.
- The dispatcher registry is the single source of truth for allowed tool names
  and their handlers.
- The external dispatcher contract currently recognizes `create_task`,
  `list_tasks`, and `complete_task`.
- Unknown tool names raise `ValueError` without exposing the registry's
  internal `KeyError` traceback.
- Tool calls are dictionaries with a string `name` and an `arguments`
  dictionary; `ToolCall` and `ToolResult` make those boundary shapes explicit.
- The execution loop processes calls sequentially, so later calls observe
  state changes made by earlier calls.
- Execution is fail-fast: an invalid or unsuccessful call stops the sequence,
  while effects from earlier successful calls remain applied.
- Tool-call structure is validated explicitly at runtime rather than through
  Pydantic or an agent framework.
- `TaskRepository` is a structural protocol so business logic depends on
  storage capabilities rather than a concrete database implementation.
- `InMemoryTaskRepository` returns tasks in insertion order and returns a new
  list from `list_all` so callers cannot mutate its internal collection.
- Saving an existing UUID replaces the stored task, defining the update
  behavior that future repository implementations must preserve.
- `TaskService` receives its repository once through constructor injection and
  owns UUID generation, timestamps, initial status, and completion rules.
- The service-backed adapter, dispatcher, and execution loop also use
  constructor injection; the legacy global store and function-based path have
  been removed.
- Pytest fixtures compose fresh dependency graphs per test, replacing the old
  autouse fixture that cleared shared global storage.
- SQLAlchemy models remain separate from the domain dataclasses so the domain
  and service layers do not depend on the ORM.
- Initial SQL development uses in-memory SQLite and `MetaData.create_all` only
  for disposable test schemas; durable schemas will use Alembic migrations.
- SQL repository sessions are created by an injected `sessionmaker`, keeping
  engine configuration outside the repository.
- SQL saves use `Session.merge` so saving an existing UUID replaces its row,
  matching the in-memory repository's update behavior.
- SQL task lists are ordered by creation timestamp and then UUID, providing a
  deterministic result when timestamps are equal.
- SQLite returns naive datetime values, so the database mapper restores and
  normalizes domain timestamps to aware UTC values.
- Pydantic has been removed because no active layer uses it.

## Completed work

- Removed the mixed Pydantic/dataclass model design.
- Verified that a `Task` can be constructed as a normal dataclass.
- Removed the `status` argument from `create_task`.
- Set the initial status explicitly to `TaskStatus.TODO`.
- Simplified `list_tasks` to return a new list of the stored task objects.
- Manually verified listing with one and multiple tasks and confirmed that
  repeated calls do not modify storage.
- Verified that `complete_task` changes a task to `COMPLETED` and advances its
  update timestamp on the first call.
- Verified that repeated completion does not change the task or its timestamp.
- Verified that a missing task ID raises `ValueError`.
- Added pytest as a development dependency.
- Added an autouse fixture that isolates tests by clearing the in-memory store
  before and after each test.
- Added four automated tests covering task creation, empty and populated task
  listing, task completion, repeated completion, and unknown task IDs.
- Learned how pytest collection, assertions, fixtures, setup/teardown with
  `yield`, and expected-exception checks work.
- Confirmed the complete suite passes with `uv run python -m pytest -v`.
- Added `complete_task_from_arguments`, including string-to-UUID conversion
  and validation for missing, malformed, non-string, and unknown task IDs.
- Added `create_task_from_arguments`, including title and optional-description
  validation.
- Added `task_to_dict` and `tasks_to_dicts` to serialize typed task values at
  the output boundary.
- Updated the create and complete adapters to return JSON-compatible task
  dictionaries.
- Added `list_tasks_from_arguments`, returning a JSON-compatible task list
  while preserving task order.
- Added a registry-based dispatcher for the create, list, and complete tools.
- Added dispatcher tests covering all three successful routes and the unknown
  tool error path.
- Added a deterministic execution loop around the dispatcher.
- Added explicit validation for missing or incorrectly typed tool names and
  argument dictionaries.
- Added execution-loop tests covering ordered create/list calls and fail-fast
  behavior after a failed call.
- Added `TaskRepository` and an isolated in-memory implementation with tests
  for save/get, ordered listing, list isolation, and replacement by UUID.
- Added `TaskService` with create, get, list, and idempotent complete behavior.
- Migrated task adapters, the dispatcher, and the execution loop to injected
  service-backed classes.
- Migrated boundary-validation tests, including parametrized malformed-input
  cases, to the service-backed path.
- Removed the global task dictionary, legacy task functions, function-based
  adapters and dispatcher, and their superseded tests.
- Added SQLAlchemy as a runtime dependency and defined a typed `TaskRecord`
  mapping with UUID, text, enum, and datetime columns.
- Added in-memory SQLite schema, ORM round-trip, and session-factory tests.
- Added pure domain-to-record and record-to-domain mappers with UTC timestamp
  normalization.
- Implemented and tested SQL repository save, replacement, lookup, and ordered
  listing behavior.
- Verified create, get, list, complete, and idempotent repeated completion by
  running the unchanged `TaskService` against `SQLAlchemyTaskRepository`.
- Removed the unused Pydantic runtime dependency.
- The resulting suite has 39 passing tests across all active layers.

## Current limitations

- Both current runtime composition and SQL tests use process-local storage;
  no durable database is configured yet.
- Supporting operations beyond the three core tools have not all been fully
  reviewed.
- There is no Alembic migration environment or versioned schema yet.
- There is no LLM-driven loop that requests tools and consumes their results.

## Next learning step

Add durable file-based SQLite application composition, then introduce Alembic
to version schema changes instead of relying on `MetaData.create_all`. Follow
that with PostgreSQL configuration once the migration workflow is understood.
