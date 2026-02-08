from collections.abc import Sequence
# from agents.items import ToolApprovalItem
from agents.run_context import RunContextWrapper
# from agents.tool import ShellOnApprovalFunctionResult
import asyncio
import os
from agents import ShellCallOutcome, ShellCommandOutput, ShellCommandRequest, ShellResult
from pathlib import Path

SHELL_AUTO_APPROVE = os.environ.get("SHELL_AUTO_APPROVE") == "1"


class ShellExecutor:
    """Executes shell commands; approval is handled via ShellTool."""

    def __init__(self, cwd: Path | None = None):
        self.cwd = Path(cwd or Path.cwd())

    async def __call__(self, request: ShellCommandRequest) -> ShellResult:
        action = request.data.action

        outputs: list[ShellCommandOutput] = []
        for command in action.commands:
            proc = await asyncio.create_subprocess_shell(
                command,
                cwd=self.cwd,
                env=os.environ.copy(),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )
            
            timed_out = False
            try:
                timeout = (action.timeout_ms or 0) / 1000 or None
                stdout_bytes, stderr_bytes = await asyncio.wait_for(
                    proc.communicate(), timeout=timeout
                )
            except asyncio.TimeoutError:
                proc.kill()
                stdout_bytes, stderr_bytes = await proc.communicate()
                timed_out = True

            stdout = stdout_bytes.decode("utf-8", errors="ignore")
            stderr = stderr_bytes.decode("utf-8", errors="ignore")
            outputs.append(
                ShellCommandOutput(
                    command=command,
                    stdout=stdout,
                    stderr=stderr,
                    outcome=ShellCallOutcome(
                        type="timeout" if timed_out else "exit",
                        exit_code=getattr(proc, "returncode", None),
                    ),
                )
            )

            if timed_out:
                break

        return ShellResult(
            output=outputs,
            provider_data={"working_directory": str(self.cwd)},
        )


# async def on_shell_approval(
#     _context: RunContextWrapper, approval_item: ToolApprovalItem
# ) -> ShellOnApprovalFunctionResult:
#     raw = approval_item.raw_item
#     commands: Sequence[str] = ()
#     if isinstance(raw, dict):
#         action = raw.get("action", {})
#         if isinstance(action, dict):
#             commands = action.get("commands", [])
#     else:
#         action_obj = getattr(raw, "action", None)
#         if action_obj and hasattr(action_obj, "commands"):
#             commands = action_obj.commands
#     approved = await prompt_shell_approval(commands)
#     return {"approve": approved, "reason": "user rejected" if not approved else "approved"}


# async def prompt_shell_approval(commands: Sequence[str]) -> bool:
#     """Simple CLI prompt for shell approvals."""
#     if SHELL_AUTO_APPROVE:
#         return True
#     print("Shell command approval required:")
#     for entry in commands:
#         print(" ", entry)
#     response = input("Proceed? [y/N] ").strip().lower()
#     return response in {"y", "yes"}
