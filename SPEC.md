🔹 MASTER PROMPT: MemTrace (E-core) Specification

You are building MemTrace, a memory evaluation and diagnostics infrastructure for AI agents.

Your task is to implement a clean, minimal, correct codebase that satisfies the following requirements exactly.

1. Core Goal (Non-negotiable)

Build a system that can:

Explain WHY an agent failed due to memory behavior,
not just log what happened.

Specifically, it must distinguish between:

Overwrite (interference)

Eviction (capacity overflow)

Retrieval miss

Memory never written

Memory exists but ignored (future work)

No guessing. Only evidence from logged events.

2. High-Level Architecture

The system consists of four layers only:

Agent → MemoryStore → MemoryEvent → EventLog → Analysis


The agent controls behavior

MemTrace only observes

No agent logic lives in MemTrace

No ML / embeddings / LLM logic required

3. Memory Model (Strict Contract)
Memory layers

STM (short-term memory)

LTM (optional, same interface)

WEIGHT (interface only, not implemented)

MemoryStore responsibilities

Store key → value pairs

Enforce optional capacity (for STM)

Emit events for every state change

4. Memory Events (Atomic Truth)

Every memory interaction must emit a MemoryEvent.

Event types (Enum)

WRITE

READ

UPDATE

EVICT

MemoryEvent fields (minimum)

event_id (uuid)

event_type

memory_layer

step (logical step, agent-controlled)

timestamp

key

value

metadata (dict)

If it changes memory state, it MUST emit an event.

5. Eviction Rules (Critical)

STM supports a fixed capacity

When capacity is exceeded:

Evict the oldest entry (FIFO)

Emit an EVICT event with reason = "capacity_overflow"

⚠️ Eviction must ONLY occur when different keys exceed capacity.
⚠️ Writing the same key must result in UPDATE, NOT EVICT.

6. Overwrite Rules (Critical)

Writing an existing key must:

Replace the old value

Emit an UPDATE event

Include old_value in metadata

Overwrite ≠ forgetting.
This is interference, not eviction.

7. Agent (Toy but Realistic)

Implement a simple deterministic agent that:

Maintains its own step counter

Automatically increments step on every meaningful action

Decides when to:

write memory

read memory

Does NOT know about MemTrace

Example behaviors:

Store different facts under different keys (e.g. deadline, meeting)

Ask memory questions naturally

Fail when memory is missing

8. Event Log

A single shared list of MemoryEvent

Order matters

This is the ground truth timeline

9. Failure Explanation (THIS IS THE KEY OUTPUT)

Implement an analysis module that, given:

an event log

a failed READ (value is None or wrong)

Produces a human-readable diagnosis, such as:

Examples

“Failure due to STM eviction (capacity overflow)”

“Failure due to overwrite/interference”

“Failure due to retrieval miss (memory existed but not returned)”

“Failure because memory was never written”

The explanation must reference:

key

step of WRITE

step of EVICT or UPDATE (if applicable)

step of READ

No metrics yet. No UI.

10. Folder Structure (Target)
memtrace/
├── core/
│   ├── events.py
│   ├── memory.py
│
├── agent/
│   └── toy_agent.py
│
├── analysis/
│   └── explain.py
│
├── run.py

11. Explicit Non-Goals (DO NOT IMPLEMENT)

No LLM calls

No embeddings

No vector DB

No dashboards

No benchmarks

No metrics yet

No frameworks (LangChain, etc.)

12. Definition of “Done” (for now)

The system is correct if:

Running run.py produces:

agent responses

a memory event trace

The analysis module can correctly say:

whether failure was caused by UPDATE vs EVICT

Logs are deterministic and explainable

Code is simple, readable, and minimal

Final instruction to the editor agent:

Prioritize correctness, causality, and explainability over features.
If a line of code does not help explain memory failure, remove it.