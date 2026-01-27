# MemTrace Workflow Documentation

This document explains the complete workflow of the MemTrace system, from start to finish.

---

## 🚀 Entry Point: `run.py`

**Purpose**: Main orchestrator that sets up and runs memory test scenarios

**What it does**:
1. Creates an empty `event_log` list (ground truth of all memory operations)
2. Initializes a `MemoryStore` (STM) with specific capacity
3. Creates a `StructuredAgent` that uses this memory
4. Sends JSON commands to the agent
5. Creates a `RecallTask` to evaluate if the agent remembered correctly
6. Prints events and diagnosis results

**Flow**:
```
run.py
  ├─> Creates MemoryStore (core/memory.py)
  ├─> Creates StructuredAgent (agent/StructuredAgent.py)
  ├─> Sends JSON commands → generates MemoryEvents
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

### 3. **`agent/StructuredAgent.py`**
**Role**: Agent that processes structured JSON commands

**Key Class**: `StructuredAgent`

**What it does**:
- Accepts JSON commands with action, key, and value
- Executes write and read operations on memory
- Returns structured results
- Increments step counter for each operation

**Supported Commands**:
- `{"action": "write", "key": "k1", "value": "v1"}` - Write to memory
- `{"action": "read", "key": "k1"}` - Read from memory

**Example**:
```python
agent.execute_command({"action": "write", "key": "k1", "value": "v1"})
# Returns: {"status": "success", "action": "write", "key": "k1", "value": "v1", "step": 1}

agent.execute_command({"action": "read", "key": "k1"})
# Returns: {"status": "success", "action": "read", "key": "k1", "value": "v1", "step": 2}
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

3. Create StructuredAgent
   └─> memory=MemoryStore

4. Command 1: {"action": "write", "key": "k1", "value": "v1"}
   └─> agent.execute_command()
       └─> memory.write("k1", "v1", step=1)
           └─> event_log.append(WRITE event)

5. Command 2: {"action": "write", "key": "k1", "value": "v2"}
   └─> agent.execute_command()
       └─> memory.write("k1", "v2", step=2)
           └─> Detects key exists → UPDATE
           └─> event_log.append(UPDATE event)

6. Command 3: {"action": "write", "key": "k1", "value": "v3"}
   └─> agent.execute_command()
       └─> memory.write("k1", "v3", step=3)
           └─> event_log.append(UPDATE event)

7. Command 4: {"action": "read", "key": "k1"}
   └─> agent.execute_command()
       └─> memory.read("k1", step=4)
           └─> Returns "v3"
           └─> event_log.append(READ event)

8. Create RecallTask
   └─> key="k1", expected_value="v1", write_step=1

9. Evaluate
   └─> RecallTask.evaluate(event_log)
       └─> Finds READ event at step=4
       └─> value="v3" ≠ expected="v1"
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
    MemoryEvent(type=WRITE, layer=STM, step=1, key="k1", value="v1"),
    MemoryEvent(type=UPDATE, layer=STM, step=2, key="k1", value="v2", metadata={"old_value": "v1"}),
    MemoryEvent(type=UPDATE, layer=STM, step=3, key="k1", value="v3", metadata={"old_value": "v2"}),
    MemoryEvent(type=READ, layer=STM, step=4, key="k1", value="v3"),
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
| `run.py` | **Orchestrator** | Sets up scenario, sends commands, evaluates results |
| `core/events.py` | **Data Models** | Defines event types and structures |
| `core/memory.py` | **Storage Engine** | Manages memory operations and logging |
| `agent/StructuredAgent.py` | **Agent Logic** | Processes JSON commands, interacts with memory |
| `tasks/recall_task.py` | **Evaluator** | Checks if recall was correct |
| `analysis/diagnose.py` | **Diagnostician** | Explains why recall failed |

---

## 🚦 Quick Start

1. **Run the scenario**:
   ```bash
   python run.py
   ```

2. **Observe**:
   - JSON command execution
   - Memory events log
   - Task evaluation result
   - Failure diagnosis (if failed)

3. **Modify scenarios** in `run.py`:
   - Change capacity for different behaviors
   - Add more JSON commands
   - Test different recall expectations

---

## 💡 Tips

- **event_log is the source of truth**: Everything is recorded here
- **Step numbers matter**: They show temporal ordering
- **RecallTask auto-finds reads**: No need to specify exact step
- **Diagnosis is automatic**: Just check the failure info
- **Use JSON commands**: Structured format makes testing easier

---

**Last Updated**: 2026-01-27
