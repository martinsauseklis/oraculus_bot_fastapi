import asyncio
from agents import function_tool

@function_tool
async def start_server(cmd: str):
    """Here you can run long running scripts like running servers. For example npm run dev, which
    keeps running until you kill the process with the PID you get returned from this tool."""
    proc = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    return proc.pid

