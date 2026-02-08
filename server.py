from agents.mcp import MCPServerStdio, MCPServerManager, MCPServer
from dotenv import load_dotenv
from os import getenv
import logging
logger = logging.getLogger("uvicorn.error")


def postgres_mcp():
    """This is is a Postgres DB on which you can run commands"""
    return MCPServerStdio(
        name="Postgres DB",
        params={
            "command": "npx",
            "args": [
                "-y",
                "@modelcontextprotocol/server-postgres",
                getenv("DB_URL")
            ]
        },
        max_retry_attempts=1
    )

def codex_mcp():
    """Codex agent that can write and execute code"""
    return MCPServerStdio(
        name="Codex agent",
        params={
            "command": "npx",
            "args": [
                "-y",
                "codex",
                "mcp-server",
                "-c ask-for-approval=never"
            ]
        },
        client_session_timeout_seconds=360000
    )



def start_mcp_manager(*mcps: list[MCPServerStdio]) -> MCPServerManager:
    return MCPServerManager(mcps)
