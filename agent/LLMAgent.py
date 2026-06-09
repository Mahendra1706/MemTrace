"""
LLMAgent - Real LLM agent that uses Groq API
Connects to the SAME core memory system (STM/LTM) as StructuredAgent
"""

import json
import os
from typing import Dict, Any, List, Optional

from groq import Groq

from core.events import MemoryLayer, MemoryEvent
from core.stm import ShortTermMemory
from core.ltm import LongTermMemory
from core.memory_file import MemoryFile


SYSTEM_PROMPT = """You are a memory-augmented AI assistant. You have two memory stores:

SHORT-TERM MEMORY (STM): For temporary, time-bound, or session-specific information.
  Examples: today's meeting time, a one-time code, current task status, temporary reminders.
  Rule: If it won't matter in a week, it goes in STM.

LONG-TERM MEMORY (LTM): For permanent facts, identity, and persistent preferences.
  Examples: user's name, blood type, favorite language, emergency contacts, passwords.
  Rule: If it's a fact about the user or something they'd expect you to always know, it goes in LTM.

You can see your FULL MEMORY NOTEBOOK in each message. Use it to answer questions directly.

RESPOND ONLY with valid JSON in this exact format:
{
    "memory_ops": [
        {"action": "write", "key": "key_name", "value": "the_value", "layer": "STM", "importance": 0.5}
    ],
    "keys_accessed": ["key1", "key2"],
    "response": "Your natural language reply to the user"
}

FIELD DEFINITIONS:
- "memory_ops": List of WRITE operations for new information. Only use "write" action.
- "keys_accessed": List of keys you checked or attempted to check in the notebook to answer the user's question.
  If the user asks about something (like a parking spot) and you look at the notebook but it is NOT there,
  you MUST still list the key you were looking for (e.g. "parking_spot") in this list so the system knows you tried to find it.
  If you didn't need to look up anything, use an empty list: []
- "response": Your natural language reply to the user.

KEY NAMING RULES:
- Use snake_case: "meeting_time", "blood_type", "wifi_password"
- Be SPECIFIC: "project_meeting_time" NOT just "meeting"
- NEVER reuse a key for different concepts. "standup_status" and "project_meeting_time" are DIFFERENT keys.
  If user says "meeting is at 3pm" and later says "standup is cancelled", these are TWO separate keys.

IMPORTANCE SCORING (be precise, do NOT default everything to the same score):
  0.95 - 1.0 : LIFE-CRITICAL — medical info, emergency contacts, allergies
  0.85 - 0.94: IDENTITY — user's name, profession, core preferences
  0.70 - 0.84: HIGH — deadlines, passwords, important appointments
  0.50 - 0.69: MODERATE — meeting times, order numbers, room numbers
  0.30 - 0.49: LOW — parking spots, temporary codes, today's schedule items
  0.10 - 0.29: TRIVIAL — small talk, easily re-askable info
  Each memory MUST have a DIFFERENT score based on its actual importance.

CRITICAL RULES:
1. When answering a question, ALWAYS check the notebook and list keys you used in "keys_accessed".
2. Do NOT invent values. If it's not in the notebook, say you don't know.
3. Do NOT overwrite unrelated data. Different topics = different keys.
4. If no memory ops needed, use: "memory_ops": []
5. Output ONLY valid JSON. No markdown, no explanation, no extra text.
6. most important that is not neccessory to store key value pair from every sentence. as example if user send a text that has no need to store then dont force to store KV pair
"""


class LLMAgent:
    def __init__(
        self,
        stm_capacity: int,
        event_log: List[MemoryEvent],
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
    ):
        self.step = 0
        self.event_log = event_log

        self.stm = ShortTermMemory(capacity=stm_capacity, event_log=event_log)
        self.ltm = LongTermMemory(event_log=event_log)
        self.memory_file = MemoryFile(stm=self.stm, ltm=self.ltm)

        self.client = Groq(api_key=api_key)
        self.model = model
        self.conversation_history = []

    def _next_step(self) -> int:
        self.step += 1
        return self.step

    def _call_llm(self, messages: list) -> str:
        """Call Groq API and return response text."""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=0.3,
            max_tokens=1024,
        )
        return response.choices[0].message.content

    def _parse_response(self, text: str) -> Dict[str, Any]:
        """Parse LLM JSON response, handling markdown fences."""
        text = text.strip()
        if text.startswith("```"):
            lines = text.split("\n")
            end = -1 if lines[-1].strip().startswith("```") else len(lines)
            text = "\n".join(lines[1:end])

        try:
            return json.loads(text.strip())
        except json.JSONDecodeError:
            # Try extracting JSON object
            start = text.find("{")
            end = text.rfind("}") + 1
            if start != -1 and end > start:
                try:
                    return json.loads(text[start:end])
                except json.JSONDecodeError:
                    pass
            return {"memory_ops": [], "keys_accessed": [], "response": f"[Parse error] {text[:200]}"}

    def _execute_writes(self, ops: list):
        """Execute WRITE memory operations."""
        for op in ops:
            action = op.get("action")
            key = op.get("key")
            if not action or not key or action != "write":
                continue

            value = op.get("value")
            layer_str = op.get("layer", "STM")
            importance = op.get("importance", 0.5)
            step = self._next_step()

            if layer_str.upper() == "LTM":
                self.ltm.ltm_write(
                    key=key, value=value, step=step,
                    layer=MemoryLayer.LTM, importance=importance,
                    metadata={"source": "llm_agent"},
                )
            else:
                self.stm.stm_write(
                    key=key, value=value, step=step,
                    layer=MemoryLayer.STM, importance=importance,
                    metadata={"source": "llm_agent"},
                )

    def _log_reads(self, keys_accessed: list):
        """Log READ events for keys the LLM accessed from the notebook."""
        for key in keys_accessed:
            step = self._next_step()
            # Try STM first, then LTM (same as before — both log events)
            value = self.stm.stm_read(
                key=key, step=step, metadata={"reason": "llm_recall"},
            )
            if value is None:
                value = self.ltm.ltm_read(
                    key=key, step=step, metadata={"reason": "llm_recall"},
                )

    def process(self, user_message: str) -> str:
        """
        Process user message through the LLM agent.

        Flow:
        1. Inject full memory notebook + user message
        2. LLM reads notebook directly, decides writes, answers question
        3. Execute writes + log reads
  
        """
        notebook = self.memory_file.get_notebook()

        # Build messages
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]

        # Add recent conversation history (last 3 turns)
        for msg in self.conversation_history[-6:]:
            messages.append(msg)

        user_prompt = (
            f"YOUR MEMORY NOTEBOOK:\n{notebook}\n\n"
            f"User message: {user_message}\n"
            f"Respond with JSON only."
        )
        messages.append({"role": "user", "content": user_prompt})

        # Single LLM call 
        raw = self._call_llm(messages)
        parsed = self._parse_response(raw)

        memory_ops = parsed.get("memory_ops", [])
        keys_accessed = parsed.get("keys_accessed", [])
        response_text = parsed.get("response", "I couldn't process that.")
         
        # execute read and write operation
        self._log_reads(keys_accessed)

        self._execute_writes(memory_ops)

        # Store conversation history
        self.conversation_history.append({"role": "user", "content": user_message})
        self.conversation_history.append({"role": "assistant", "content": response_text})

        return response_text
