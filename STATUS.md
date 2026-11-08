# Project Status

## Goal

Build a personal task-management agent from first principles as a learning
project. The initial implementation uses plain Python and in-memory storage;
LLM integration and agent frameworks are intentionally out of scope for now.

## Current learning step

Step 3 is complete: the project now has a JSON-compatible adapter boundary and
a minimal dispatcher that selects an adapter by its external tool name.

The next learning step is to define the smallest execution-loop boundary that
can accept a tool name and arguments, dispatch the call, and return a result
without introducing an LLM or agent framework yet.

Dedicated pytest instruction is complete. Automated tests will continue to be
added as normal development work, but unit testing is no longer a separate
learning objective.

The core operations under consideration are:

- Create a task.
- List tasks.
- Complete a task.

## Current structure

- `domains/task.py` defines the `Task` domain entity and `TaskStatus` enum.
- `tools/tasks.py` owns the in-memory task store and task operations.
- `agent/tool_adapters.py` validates JSON-compatible arguments, converts them
  to typed values, delegates to the task operations, and serializes returned
  tasks into JSON-compatible values.
- `agent/tool_dispatcher.py` maps external tool names to the three core
  adapters and invokes the selected adapter with the supplied arguments.
- `tests/test_tasks.py` contains the automated contract for the three core
  operations.
- `tests/test_task_adapter.py` covers the external-input adapters.
- `tests/test_tool_dispatcher.py` covers successful routing for the three core
  tools and rejection of unknown tool names.
- `tests/conftest.py` provides shared in-memory storage isolation.
- The in-memory store is a dictionary keyed by task UUID.

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
- Expanded the suite to 24 passing tests covering the core operations,
  input/output adapters, and dispatcher.

## Current limitations

- Storage is process-local and disappears when the program exits.
- Supporting operations beyond the three core tools have not all been fully
  reviewed.
- There is no LLM or agent execution loop.

## Next learning step

Define a minimal execution-loop boundary around the dispatcher. Keep the first
version deterministic and framework-free so the request/result flow is clear
before considering an LLM or SDK integration.
