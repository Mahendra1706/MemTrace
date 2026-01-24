import sys
from pathlib import Path

# Add parent directory to Python path to allow imports from 'core'
sys.path.insert(0, str(Path(__file__).parent.parent))

from typing import List, Dict, Any

from core.memory import MemoryStore
from core.events import MemoryLayer, MemoryEvent

class ToyAgent:
    def __init__(self, memory: MemoryStore):
        self.memory = memory
        self.step = 0

    def _next_step(self) -> int:
        self.step += 1
        return self.step

    def observe(self, user_input: str):
        step = self._next_step()
        return {
            "type": "user_input",
            "content": user_input,
            "step": step,
        }
    
    def recall_deadline(self) -> Any:
        step = self._next_step()
        return self.memory.read(
            key="deadline",
            step=step,
            metadata={"reason": "answering_user"},
        )

    def store_deadline(self, deadline: str):
        step = self._next_step()
        self.memory.write(
            key="deadline",
            value=deadline,
            step=step,
            metadata={"source": "user"},
        )

    def store_meeting(self, meeting: str):
        step = self._next_step()
        self.memory.write(
            key="meeting",
            value=meeting,
            step=step,
            metadata={"source": "user"},
        )

    
    def run_turn(self, user_input: str) -> str:
        self.observe(user_input)

        # If user provides a deadline, store it
        if "deadline is" in user_input:
            deadline = user_input.split("deadline is")[-1].strip()
            self.store_deadline(deadline)
            return "Got it. I've noted your deadline."

        # If user provides a meeting, store it
        if "meeting is" in user_input:
            meeting = user_input.split("meeting is")[-1].strip()
            self.store_meeting(meeting)
            return "Okay."

        # Otherwise, try to recall it
        if "what is my deadline" in user_input.lower():
            value = self.recall_deadline()
            if value is None:
                return "I'm not sure about your deadline."
            return f"Your deadline is {value}."

        return "Okay."