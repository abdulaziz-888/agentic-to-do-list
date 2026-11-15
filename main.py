from app import create_application


def main() -> None:
    user_input = input("You: ")

    with create_application() as application:
        response = application.agent_loop.run(user_input)

    print(response)


if __name__ == "__main__":
    main()
