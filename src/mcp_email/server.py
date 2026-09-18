import os
import smtplib
from email.message import EmailMessage

from dotenv import load_dotenv
from mcp.server.mcpserver import MCPServer

load_dotenv()

mcp = MCPServer("meeting-email-server")


@mcp.tool()
def send_email(to: str, subject: str, body: str) -> str:
    """Send an email using the configured SMTP server."""

    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    username = os.getenv("SMTP_USERNAME")
    password = os.getenv("SMTP_PASSWORD")
    sender = os.getenv("EMAIL_FROM", username)

    if not all([host, username, password, sender]):
        return "Email configuration is missing."

    message = EmailMessage()
    message["From"] = sender
    message["To"] = to
    message["Subject"] = subject
    message.set_content(body)

    try:
        with smtplib.SMTP(host, port) as smtp:
            smtp.starttls()
            smtp.login(username, password)
            smtp.send_message(message)

        return f"Email successfully sent to {to}."

    except Exception as exc:
        return f"Failed to send email: {exc}"


if __name__ == "__main__":
    mcp.run()
