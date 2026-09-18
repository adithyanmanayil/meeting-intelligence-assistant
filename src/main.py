from src.agent import MeetingAgent


def main():
    print("=" * 60)
    print("Meeting Intelligence & Follow-up Assistant")
    print("Type 'exit' to quit.")
    print("=" * 60)

    agent = MeetingAgent()

    while True:
        try:
            request = input("\nYou: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nGoodbye!")
            break

        if request.lower() == "exit":
            print("Goodbye!")
            break

        if not request:
            continue

        result = agent.handle(request)

        print("\nAssistant:")
        print(result["response"])

        if result["type"] == "email":
            print("\n[Email workflow selected]")
        elif result["type"] == "clarification":
            print("\n[Clarification required]")


if __name__ == "__main__":
    main()
