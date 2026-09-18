import asyncio
import re

from src.agent import MeetingAgent
from src.mcp_email.client import send_email


def parse_email(response: str) -> tuple[str, str]:
    """Extract subject and body from generated email text."""

    subject_match = re.search(
        r"Subject:\s*(.+)",
        response,
        re.IGNORECASE,
    )

    body_match = re.search(
        r"Body:\s*(.*)",
        response,
        re.IGNORECASE | re.DOTALL,
    )

    subject = subject_match.group(1).strip() if subject_match else "Meeting Follow-up"
    body = body_match.group(1).strip() if body_match else response

    return subject, body


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

        if result["type"] == "clarification":
            continue

        if result["type"] == "email":
            recipient = input("\nRecipient email: ").strip()

            if not recipient:
                print("No recipient provided. Email cancelled.")
                continue

            confirm = input("Send this email? [y/N]: ").strip().lower()

            if confirm != "y":
                print("Email cancelled.")
                continue

            subject, body = parse_email(result["response"])

            print("\nSending email through MCP...")

            try:
                message = asyncio.run(
                    send_email(
                        to=recipient,
                        subject=subject,
                        body=body,
                    )
                )
                print(message)
            except Exception as exc:
                print(f"MCP email error: {exc}")


if __name__ == "__main__":
    main()
