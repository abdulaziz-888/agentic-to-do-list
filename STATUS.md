# Project Status

## Goal

Build a personal task-management agent from first principles as a learning
project. The initial implementation uses plain Python and in-memory storage;
LLM integration and agent frameworks are intentionally out of scope for now.

## Current learning step

Step 2 is complete: the task-management tools have been implemented,
understood, manually exercised, and covered by automated tests without LLM
integration.

The core operations under consideration are:

- Create a task.
- List tasks.
- Complete a task.

## Current structure

- `domains/task.py` defines the `Task` domain entity and `TaskStatus` enum.
- `tools/tasks.py` owns the in-memory task store and task operations.
- `tests/test_tasks.py` contains the automated contract for the three core
  operations.
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

## Current limitations

- Storage is process-local and disappears when the program exits.
- Supporting operations beyond the three core tools have not all been fully
  reviewed.
- There is no LLM or agent execution loop.

## Next learning step

Begin Step 3 by defining the boundary between external, JSON-compatible tool
arguments and the typed Python task operations. Start with the conceptual
contract and one small conversion exercise before introducing an LLM or the
OpenAI SDK.
