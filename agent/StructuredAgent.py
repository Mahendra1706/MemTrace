import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import Dict, Any, Optional, List

from core.memory import MemoryStore
from core.events import MemoryLayer, MemoryEvent
from core.ltm import LongTermMemory
from core.stm import ShortTermMemory


class StructuredAgent:
    """
    Generalized agent that processes structured JSON commands.
    
    Supported commands:
    - {"action": "write", "key": "k1", "value": "v1", "layer": "LTM" or "STM", "importance": 0.8}
    - {"action": "read", "key": "k1"}
    """
    
    def __init__(self, stm_capacity: int, event_log: List[MemoryEvent]):
        """
        Initialize agent with both STM and LTM.
        
        Args:
            stm_capacity: Capacity for short-term memory
            event_log: Shared event log for both STM and LTM
        """
        self.step = 0
        
        # centralized event log
        self.stm = ShortTermMemory(
            capacity=stm_capacity,
            event_log=event_log  
        )
        self.ltm = LongTermMemory(
            event_log=event_log  
        )
        
        # Keep reference for backward compatibility
        self.memory = self.stm

    def _next_step(self) -> int:
        """Increment and return the current step counter."""
        self.step += 1
        return self.step

    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute a structured command and return the result.
        
        Args:
            command: Dictionary with 'action', 'key', and optionally 'value', 'layer', 'importance'
            
        Returns:
            Dictionary with execution result
        """
        action = command.get("action")
        key = command.get("key")
        
        if action == "write":
            value = command.get("value")
            layer_str = command.get("layer", "STM")  
            importance = command.get("importance", 0.5)
            
            if key is None or value is None:
                return {
                    "status": "error",
                    "message": "write action requires 'key' and 'value'"
                }
            
            # Convert layer string to MemoryLayer enum
            layer = None
            if layer_str:
                if layer_str.upper() == "LTM" or layer_str == "long_term":
                    layer = MemoryLayer.LTM
                elif layer_str.upper() == "STM" or layer_str == "short_term":
                    layer = MemoryLayer.STM

            step = self._next_step()

            # Route to appropriate memory layer
            if layer == MemoryLayer.LTM:
                self.ltm.ltm_write(
                    key=key,
                    value=value,
                    step=step,
                    layer=layer,
                    importance=importance,
                    metadata={"source": "command"},
                )
            else:  # Default to STM
                self.stm.stm_write(
                    key=key,
                    value=value,
                    step=step,
                    layer=layer,
                    importance=importance,
                    metadata={"source": "command"},
                )
            
            return {
                "status": "success",
                "action": "write",
                "key": key,
                "value": value,
                "layer": layer.name if layer else "STM",
                "step": step,
                "importance": importance,
            }
        
        elif action == "read":
            if key is None:
                return {
                    "status": "error",
                    "message": "read action requires 'key'"
                }
            
            step = self._next_step()
            importance = command.get("importance", 0.5)
            
            # Try STM first, then LTM
            returned_value = self.stm.stm_read(
                key=key,
                step=step,
                metadata={"reason": "command_read"},
            )
            
            if returned_value is None:
                # Try LTM
                returned_value = self.ltm.ltm_read(
                    key=key,
                    step=step,
                    metadata={"reason": "command_read"},
                )
            
            return {
                "status": "success",
                "action": "read",
                "key": key,
                "value": returned_value,
                "step": step,
            }
        
        else:
            return {
                "status": "error",
                "message": f"Unknown action: {action}"
            }