import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional

from core.memory import MemoryStore
from core.events import MemoryLayer, MemoryEvent


class StructuredAgent:
    """
    Generalized agent that processes structured JSON commands.
    
    Supported commands:
    - {"action": "write", "key": "k1", "value": "v1"}
    - {"action": "read", "key": "k1"}
    """
    
    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.step = 0

    def _next_step(self) -> int:
        """Increment and return the current step counter."""
        self.step += 1
        return self.step

    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured command and return the result.
        
        Args:
            command: Dictionary with 'action', 'key', and optionally 'value'
            
        Returns:
            Dictionary with execution result
        """
        action = command.get("action")
        key = command.get("key")
        
        if action == "write":
            value = command.get("value")
            if key is None or value is None:
                return {
                    "status": "error",
                    "message": "write action requires 'key' and 'value'"
                }
            
            step = self._next_step()
            self.memory.write(
                key=key,
                value=value,
                step=step,
                metadata={"source": "command"},
            )
            
            return {
                "status": "success",
                "action": "write",
                "key": key,
                "value": value,
                "step": step,
            }
        
        elif action == "read":
            if key is None:
                return {
                    "status": "error",
                    "message": "read action requires 'key'"
                }
            
            step = self._next_step()
            value = self.memory.read(
                key=key,
                step=step,
                metadata={"reason": "command_read"},
            )
            
            return {
                "status": "success",
                "action": "read",
                "key": key,
                "value": value,
                "step": step,
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }