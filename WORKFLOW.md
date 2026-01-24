# MemTrace Workflow Documentation

This document explains the complete workflow of the MemTrace system, from start to finish.

---

## 🚀 Entry Point: `run.py`

**Purpose**: Main orchestrator that sets up and runs memory test scenarios

**What it does**:
1. Creates an empty `event_log` list (ground truth of all memory operations)
2. Initializes a `MemoryStore` (STM) with specific capacity
3. Creates a `ToyAgent` that uses this memory
4. Runs conversation turns with the agent
5. Creates a `RecallTask` to evaluate if the agent remembered correctly
6. Prints events and diagnosis results

**Flow**:
```
run.py
  ├─> Creates MemoryStore (core/memory.py)
  ├─> Creates ToyAgent (agent/toy_agent.py)
  ├─> Runs agent turns → generates MemoryEvents
  ├─> Creates RecallTask (tasks/recall_task.py)
  └─> Evaluates and prints results
```

---

## 📦 Core Components

### 1. **`core/events.py`**
**Role**: Defines the data structures for memory events

**Key Classes**:
- `MemoryLayer`: Enum (STM, LTM, etc.)
- `MemoryEventType`: Enum (WRITE, READ, UPDATE, EVICT)
- `MemoryEvent`: Data class that records each memory operation

**Used by**: Everything! All components use these to log operations

---

### 2. **`core/memory.py`**
**Role**: The actual memory storage system

**Key Class**: `MemoryStore`

**What it does**:
- Stores key-value pairs in an `OrderedDict`
- Tracks capacity limits
- Logs every operation to `event_log`

**Operations**:
- `write(key, value, step)`:
  - If key exists → UPDATE event (overwriting scenario)
  - If capacity exceeded → EVICT event (eviction scenario)
  - Always creates WRITE event for new entries
  
- `read(key, step)`:
  - Retrieves value from store
  - Creates READ event (even if key not found, value=None)

**Flow**:
```
MemoryStore.write("deadline", "Friday", step=2)
  ├─> Checks if "deadline" exists
  ├─> Checks if capacity exceeded
  ├─> Stores in _store dict
  └─> Appends MemoryEvent to event_log
```

---

### 3. **`agent/toy_agent.py`**
**Role**: Simple agent that extracts and stores information

**Key Class**: `ToyAgent`

**What it does**:
- Takes user input
- Extracts key-value pairs (simple keyword matching)
- Writes to memory using `MemoryStore.write()`
- Reads from memory using `MemoryStore.read()`
- Increments step counter for each operation

**Example**:
```
User: "My deadline is Friday"
  ├─> Agent extracts: key="deadline", value="Friday"
  ├─> Calls memory.write("deadline", "Friday", step=2)
  └─> Returns: "Got it, deadline = Friday"

User: "What is my deadline?"
  ├─> Agent detects recall request
  ├─> Calls memory.read("deadline", step=6)
  └─> Returns: "Your deadline is Friday" (or "I don't remember")
```

---

## 🧪 Evaluation & Diagnosis

### 4. **`tasks/recall_task.py`**
**Role**: Evaluates if the agent correctly recalled information

**Key Class**: `RecallTask`

**Parameters**:
- `key`: What should be recalled (e.g., "deadline")
- `expected_value`: What the correct answer is (e.g., "Friday")
- `write_step`: When the information was first written

**What it does**:
1. Searches `event_log` for the **first READ event** with matching key
2. If no read found → FAIL (no recall attempt)
3. If read found but wrong value → FAIL (incorrect recall)
4. If read found with correct value → PASS ✅

**On failure**: Automatically calls `diagnose_failure()` to explain why

**Flow**:
```
RecallTask.evaluate(event_log)
  ├─> Loop through event_log
  ├─> Find first READ event for key="deadline"
  ├─> Compare event.value with expected_value
  ├─> If mismatch → call diagnose_failure()
  └─> Return (passed: bool, info: dict)
```

---

### 5. **`analysis/diagnose.py`**
**Role**: Root cause analysis - explains WHY recall failed

**Key Function**: `diagnose_failure(event_log, key, recall_step)`

**What it does**:
1. Searches for WRITE events for the key
2. Checks for EVICT events (was it removed due to capacity?)
3. Checks for UPDATE events (was it overwritten?)
4. Generates human-readable evidence

**Failure Types**:
- `"never_written"`: Key was never stored
- `"evicted"`: Key was written but later evicted
- `"overwritten"`: Key was written but later updated with different value
- `"unknown"`: Something else went wrong

**Output Example**:
```python
{
    "failure_type": "overwritten",
    "evidence": [
        "WRITE 'deadline'='Friday' at step=2",
        "UPDATE 'deadline'='Monday' at step=4 (old='Friday')",
        "UPDATE 'deadline'='Wednesday' at step=6 (old='Monday')",
        "READ 'deadline'='Wednesday' at step=8 (expected 'Friday')"
    ]
}
```

---

## 🔄 Complete Workflow Example

### Overwriting Scenario (Current `run.py`)

```
1. START: run.py
   └─> event_log = []

2. Create MemoryStore
   └─> capacity=10, event_log=event_log

3. Create ToyAgent
   └─> memory=MemoryStore

4. User Turn 1: "My deadline is Friday"
   └─> ToyAgent.run_turn()
       └─> memory.write("deadline", "Friday", step=2)
           └─> event_log.append(WRITE event)

5. User Turn 2: "Actually, my deadline is Monday"
   └─> ToyAgent.run_turn()
       └─> memory.write("deadline", "Monday", step=4)
           └─> Detects key exists → UPDATE
           └─> event_log.append(UPDATE event)

6. User Turn 3: "Wait, my deadline is Wednesday"
   └─> ToyAgent.run_turn()
       └─> memory.write("deadline", "Wednesday", step=6)
           └─> event_log.append(UPDATE event)

7. User Turn 4: "What is my deadline?"
   └─> ToyAgent.run_turn()
       └─> memory.read("deadline", step=8)
           └─> Returns "Wednesday"
           └─> event_log.append(READ event)

8. Create RecallTask
   └─> key="deadline", expected_value="Friday", write_step=2

9. Evaluate
   └─> RecallTask.evaluate(event_log)
       └─> Finds READ event at step=8
       └─> value="Wednesday" ≠ expected="Friday"
       └─> Calls diagnose_failure()
           └─> Detects UPDATE events
           └─> Returns failure_type="overwritten"

10. Print Results
    └─> Shows all events
    └─> Shows FAILED status
    └─> Shows diagnosis with evidence

11. END
```

---

## 📊 Event Log Structure

After running, the `event_log` contains a chronological record:

```python
[
    MemoryEvent(type=WRITE, layer=STM, step=2, key="deadline", value="Friday"),
    MemoryEvent(type=UPDATE, layer=STM, step=4, key="deadline", value="Monday", metadata={"old_value": "Friday"}),
    MemoryEvent(type=UPDATE, layer=STM, step=6, key="deadline", value="Wednesday", metadata={"old_value": "Monday"}),
    MemoryEvent(type=READ, layer=STM, step=8, key="deadline", value="Wednesday"),
]
```

---

## 🎯 Key Concepts

### Scenarios

1. **Eviction Scenario** (capacity=1):
   - Write key1 → WRITE event
   - Write key2 → EVICT key1, WRITE key2
   - Read key1 → READ with value=None
   - Diagnosis: "evicted"

2. **Overwriting Scenario** (capacity=10):
   - Write key1="A" → WRITE event
   - Write key1="B" → UPDATE event
   - Read key1 → READ with value="B"
   - Diagnosis: "overwritten"

### Step Counter
- Increments with each agent operation
- Used to track temporal ordering
- Helps diagnosis identify when things happened

---

## 🗂️ File Summary

| File | Role | Key Responsibility |
|------|------|-------------------|
| `run.py` | **Orchestrator** | Sets up scenario, runs agent, evaluates results |
| `core/events.py` | **Data Models** | Defines event types and structures |
| `core/memory.py` | **Storage Engine** | Manages memory operations and logging |
| `agent/toy_agent.py` | **Agent Logic** | Extracts info, interacts with memory |
| `tasks/recall_task.py` | **Evaluator** | Checks if recall was correct |
| `analysis/diagnose.py` | **Diagnostician** | Explains why recall failed |

---

## 🚦 Quick Start

1. **Run the scenario**:
   ```bash
   python run.py
   ```

2. **Observe**:
   - Agent conversations
   - Memory events log
   - Task evaluation result
   - Failure diagnosis (if failed)

3. **Modify scenarios** in `run.py`:
   - Change capacity for different behaviors
   - Add more conversation turns
   - Test different recall expectations

---

## 💡 Tips

- **event_log is the source of truth**: Everything is recorded here
- **Step numbers matter**: They show temporal ordering
- **RecallTask auto-finds reads**: No need to specify exact step
- **Diagnosis is automatic**: Just check the failure info

---

**Last Updated**: 2026-01-24
