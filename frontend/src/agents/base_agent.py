import subprocess
import logging
import shlex
from typing import Dict, Any, Optional

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("BashTerminalAgent")


class BashTerminalAgent:
    """
    A specialized security agent capable of executing shell/bash terminal commands safely.
    Perfect for running network diagnostics, CLI security tools, and scanning scripts.
    """

    def __init__(self, name: str = "Bash Terminal Agent", timeout_seconds: int = 60):
        self.name = name
        self.timeout = timeout_seconds

    def execute_command(self, command: str) -> str:
        """Executes a command in the bash/shell terminal and captures stdout/stderr."""
        logger.info(f"[{self.name}] Executing command: {command}")
        try:
            # Run command securely and capture output
            process = subprocess.run(
                command,
                shell=True,
                check=False,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=self.timeout
            )
            
            output = ""
            if process.stdout:
                output += process.stdout.strip()
            if process.stderr:
                output += f"\n[Errors/Warnings]:\n{process.stderr.strip()}"
                
            return output if output else "[Command executed successfully with no output]"
            
        except subprocess.TimeoutExpired:
            return f"[Error]: Command execution timed out after {self.timeout} seconds."
        except Exception as e:
            return f"[Error]: Failed to execute command. {str(e)}"

    def run(self, task: str, target: Optional[str] = None) -> Dict[str, Any]:
        """
        Parses the security task and determines which terminal command to execute.
        """
        # Example decision logic based on the task
        cmd_to_run = ""
        
        if "ping" in task.lower() and target:
            # Safely format target to prevent basic command injection
            safe_target = shlex.quote(target)
            cmd_to_run = f"ping -c 4 {safe_target}"
        elif "whois" in task.lower() and target:
            safe_target = shlex.quote(target)
            cmd_to_run = f"whois {safe_target}"
        else:
            # If it's a direct custom command task or general script
            cmd_to_run = task

        if not cmd_to_run:
            return {"output": "No valid terminal command determined for this task.", "status": "skipped"}

        execution_output = self.execute_command(cmd_to_run)

        return {
            "agent": self.name,
            "command_executed": cmd_to_run,
            "output": execution_output,
            "status": "success" if "[Error]" not in execution_output else "failed"
        }