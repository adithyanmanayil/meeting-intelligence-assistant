from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def send_email(to: str, subject: str, body: str) -> str:
    """Call the MCP send_email tool."""

    project_root = Path(__file__).resolve().parents[2]

    server_params = StdioServerParameters(
        command=str(project_root / ".venv" / "bin" / "python"),
        args=["-m", "src.mcp_email.server"],
        cwd=str(project_root),
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            result = await session.call_tool(
                "send_email",
                arguments={
                    "to": to,
                    "subject": subject,
                    "body": body,
                },
            )

            if not result.content:
                return "MCP returned no response."

            return result.content[0].text
