import json

from app import create_application


def main() -> None:
    with create_application() as application:
        results = application.execution_loop.execute_tool_calls(
            [{"name": "list_tasks", "arguments": {}}]
        )

    print(json.dumps(results[0], indent=2))


if __name__ == "__main__":
    main()
