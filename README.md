# MemTrace

**Memory Diagnosis Library for LLM Agents**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Backend: Groq](https://img.shields.io/badge/backend-Groq-orange.svg)](https://console.groq.com)

---

## What is MemTrace?

MemTrace is a diagnostic framework that watches how an LLM agent uses its memory and tells you exactly when and why it failed.

It logs every `WRITE`, `READ`, `UPDATE`, and `EVICT` event, then runs a root-cause analysis after the conversation to tell you **which step broke and why**.

---

## Quick Start

```bash
git clone https://github.com/Mahendra1706/MemTrace.git
cd MemTrace
pip install -r requirements.txt
export GROQ_API_KEY='gsk_...'

# interactive CLI
python3 memtrace.py   
```

**Or use as a library:**

```python
from memtrace import MemTrace

mt = MemTrace(api_key="gsk_...", stm_capacity=5)

# Batch mode
mt.run([
    "My meeting is at 3pm.",
    "The wifi password is guest99.",
    "What time is my meeting?",
])

# Live chat mode
mt.chat()
```

---

## Architecture

```
memtrace.py          ← entry point (CLI + library)
core/
  events.py          ← MemoryEvent, MemoryEventType, MemoryLayer
  stm.py             ← Short-term memory (capacity-limited, FIFO eviction)
  ltm.py             ← Long-term memory (unlimited, no eviction)
  memory_file.py     ← Generates readable "notebook" from STM+LTM state
agent/
  LLMAgent.py        ← Groq-powered agent that reads notebook, writes memory
analysis/
  diagnose.py        ← Root cause analysis engine
  semantic.py        ← Semantic similarity checker (diagnosis only)
tasks/
  recall_task.py     ← Evaluates every READ against its original WRITE
cookbook/
  batch_example.py   ← Example usage
```

---

## Why a Memory File (Notebook) Instead of Full Retrieval?

Most agent memory systems work like this:
> LLM guesses a key → system fetches it → LLM uses the result

The problem: **the LLM has no visibility into what keys exist.** If it stored `project_meeting_time` but later asks for `meeting_time`, retrieval returns nothing. The LLM has no way to self-correct — it doesn't know the key even exists.

MemTrace uses a different approach: **inject the entire memory state as a structured text notebook into the prompt.**

```
YOUR MEMORY NOTEBOOK:
[SHORT-TERM MEMORY]
  project_meeting_time: 3pm
  wifi_password: guest99

[LONG-TERM MEMORY]
  user_name: Mahendra
```

The LLM can now *read* its memory like a file. If it stored `project_meeting_time` but thinks of it as `meeting time`, it can still find it — because it sees all keys at once and reasons over them natively.

**Trade-off**: This scales with memory size. For very large LTM, you'd need to summarize or page the notebook. For the agent memory sizes MemTrace targets (tens to low hundreds of entries), a full notebook is the right call — it gives the LLM total control with zero black-box retrieval.

---

## Why Semantic Search Only in Diagnosis — Not in Retrieval?

This is the key design decision.

If you add semantic search to the retrieval layer:
```
LLM asks for "gathering" → semantic finds "meeting_time" → returns "3pm"
Event log shows: READ meeting_time → "3pm" ← looks like a success
```

The failure is now **invisible**. The LLM used the wrong concept, the system silently corrected it, and no event was logged. You've hidden the bug.

MemTrace keeps semantic search **strictly in the diagnosis layer**:
- During conversation: if a READ returns `None`, log it as-is. Don't fix it.
- After conversation: `diagnose_failure()` uses semantic similarity to *explain* why the failure happened — "LLM searched for `gathering_time`, similar key `project_meeting_time` exists (score 0.79)."

This gives you **full observability**. The failure is caught, logged, and explained — not silently patched.

---

## Failure Types

| Type | Cause | Critical? |
|------|-------|-----------|
| `memory_evicted` | Key removed due to STM capacity overflow | If importance ≥ 0.7 |
| `memory_overwritten` | Key updated with a different value | If old importance ≥ 0.7 |
| `retrieval_miss` | LLM used wrong key name (typo/synonym) | Yes |
| `llm_hallucination` | Value returned doesn't match what was stored | Yes |
| `invalid_read` | Key was never written | No |

### Diagnosis Priority Chain (no conflicts)

```
Key never written? → check semantic → retrieval_miss or invalid_read
Key evicted?       → memory_evicted
Key overwritten?   → memory_overwritten
Read returned None?→ memory_evicted (indirect)
Wrong value?       → check semantic → retrieval_miss or llm_hallucination
```

Each case returns immediately — first match wins, no ambiguity.

---

## Event Log

Every operation is logged automatically:

```
[STM] [step=1] WRITE key=parking_spot value=B-14
[STM] [step=2] WRITE key=lunch_order  value=#1234
[STM] [step=3] EVICT key=parking_spot  reason=capacity_overflow
[STM] [step=3] WRITE key=wifi_password value=guest99
[STM] [step=4] READ  key=lunch_order   value=#1234
[STM] [step=5] READ  key=parking_spot  value=None
```

Diagnosis output:

```
✅  step=4  lunch_order = '#1234'
❌  step=5  parking_spot — memory_evicted
       Key 'parking_spot' was written at step 1
       Evicted at step 3 due to capacity_overflow
       Importance: 0.30 (normal)
```

---

# At the end im worried about that if we gave full control of llm for its own behaviour than whats the guarantee that it doesnt mess up that, but here is the try to optimize that thing with every update
guarantee 

## Requirements

- Python 3.8+
- `groq` — Groq API client
- `sentence-transformers` — local semantic model for diagnosis (auto-downloaded on first use, ~90MB, no API key needed)
- `python-dotenv`

```bash
pip install groq sentence-transformers python-dotenv
```

**Supported LLM backend**: Groq only (for now).  
Get a free API key: https://console.groq.com/keys

---

## License

MIT — see LICENSE file.

---

**Version**: 1.0.1 
**Status**: Active development  
**GitHub**: [Mahendra1706/MemTrace](https://github.com/Mahendra1706/MemTrace)
