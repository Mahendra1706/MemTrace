"""
MemoryFile - Generates a structured readable representation of STM/LTM.

The LLM reads this notebook directly instead of guessing key names.
Core (stm.py, ltm.py, events.py) remains completely untouched.
This is purely a read layer on top of existing memory stores.
"""


class MemoryFile:
    """Generates a structured memory notebook from STM and LTM state."""

    def __init__(self, stm, ltm):
        self.stm = stm
        self.ltm = ltm

    def get_notebook(self) -> str:
        """
        Generate a structured text representation of all memories.
        This gets injected into the LLM prompt so it can read its own memory.
        """
        lines = []

        lines.append("[SHORT-TERM MEMORY] (temporary, session-specific)")
        stm_items = dict(self.stm._store)
        if stm_items:
            for key, value in stm_items.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append("  (empty)")

        lines.append("")
        lines.append("[LONG-TERM MEMORY] (permanent facts)")
        ltm_items = dict(self.ltm._store)
        if ltm_items:
            for key, value in ltm_items.items():
                lines.append(f"  {key}: {value}")
        else:
            lines.append("  (empty)")

        return "\n".join(lines)
