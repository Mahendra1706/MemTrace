# MemTrace

**Automated Memory Diagnosis Framework for LLM Agents**

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

---

## 🎯 Overview

**MemTrace** is a diagnostic framework for detecting and analyzing memory failures in LLM-based agents. It uses **event sourcing** to track every memory operation and provides **automated root cause analysis** with statistical insights.

### Key Features

- ✅ **Automated Testing** - Generate and run 1000+ random scenarios
- ✅ **Smart Diagnosis** - Automatic root cause analysis for all failures
- ✅ **Importance Tracking** - Detect critical data loss (high-importance memories)
- ✅ **Multi-Layer Memory** - STM (Short-Term) and LTM (Long-Term) support
- ✅ **Statistical Analysis** - Comprehensive metrics and failure breakdowns
- ✅ **Event Sourcing** - Complete audit trail of all memory operations

### What Problems Does It Solve?

- **Memory Eviction**: Data lost due to capacity constraints
- **Memory Overwriting**: Important data replaced by new writes
- **Invalid Reads**: Attempts to read non-existent keys
- **Critical Failures**: Loss of high-importance information

---

## 🚀 Quick Start

### Installation

```bash
git clone -b ltm https://github.com/Mahendra1706/MemTrace.git
cd MemTrace
pip install -e .
```

> **Note**: The `ltm` branch contains the latest version with importance tracking and critical failure detection.

### Run Tests

```bash
python3 run.py
```

**Sample Output:**
```
============================================================
MEMTRACE RANDOM TESTING - 1000 Scenarios
============================================================

============================================================
FINAL STATISTICS
============================================================
Total Reads: 4993
✅ Passed: 741 (14.8%)
❌ Failed: 4252 (85.2%)

Failure Breakdown:
  • Memory Evicted: 2261
  • Memory Overwritten: 240
  • Invalid Read: 1708
  • Unknown: 43

------------------------------------------------------------
ADVANCED METRICS
------------------------------------------------------------
Valid Recall Rate: 22.6%
  (Excludes 1708 invalid reads)

Memory Failure Rate: 50.1%
  (Eviction: 2261, Overwrite: 240)

Dominant Failure Mode: Memory Evicted
  (2261/4252 failures, 53.2%)

------------------------------------------------------------
CRITICAL FAILURES (High-Importance Data Loss)
------------------------------------------------------------
Total Critical Failures: 892
  • Critical Evictions: 798
  • Critical Overwrites: 94

Critical Failure Rate: 35.7%
  (892/2501 memory failures were critical)
============================================================
```

---

## 🧠 Core Concepts

### The Central Question

**Did the agent return what was originally stored?**

MemTrace compares:
- **Expected Value**: First WRITE event for a key
- **Actual Value**: What the agent returned during READ

### Event Sourcing

Every memory operation generates an immutable event:

```python
MemoryEvent(
    event_id="uuid",
    event_type=MemoryEventType.WRITE,
    memory_layer=MemoryLayer.STM,
    step=1,
    key="deadline",
    value="Friday",
    importance=0.8,  # NEW: Importance score (0.0-1.0)
    timestamp=1706345678.123,
    metadata={}
)
```

**Event Types:**
- `WRITE` - New key-value pair stored
- `READ` - Value retrieved (or attempted)
- `UPDATE` - Existing key overwritten
- `EVICT` - Key removed due to capacity constraints

### Importance Tracking

Each memory has an **importance score** (0.0-1.0):
- **High importance (≥0.7)**: Critical data (deadlines, user preferences, key facts)
- **Medium importance (0.4-0.6)**: Useful context
- **Low importance (<0.4)**: Transient information

**Critical failures** occur when high-importance data is lost.

---

## 🏗️ Architecture

```
MemTrace/
├── core/
│   ├── events.py          # Event data structures
│   ├── memory.py          # Base memory store
│   ├── stm.py             # Short-term memory (capacity-limited)
│   └── ltm.py             # Long-term memory (unlimited)
├── agent/
│   └── StructuredAgent.py # Command processor with STM/LTM routing
├── tasks/
│   └── recall_task.py     # Auto-evaluation and diagnosis
├── analysis/
│   └── diagnose.py        # Root cause analysis
├── scenario.py            # Random scenario generation
└── run.py                 # Main orchestrator with statistics
```

### Data Flow

```
User Command
    ↓
StructuredAgent.execute_command()
    ↓
Route to STM or LTM based on layer
    ↓
MemoryStore.write() / read()
    ↓
MemoryEvent created (with importance)
    ↓
Event appended to event_log
    ↓
auto_evaluate_all() finds all READ events
    ↓
Compare expected vs actual
    ↓
If mismatch → diagnose_failure()
    ↓
Return failure type + evidence + is_critical
```

---

## 🔍 Failure Types

### 1. Memory Evicted
**Cause**: Key removed due to capacity constraints

**Example**:
```python
WRITE k1=v1 (step 1, importance=0.9)
EVICT k1=v1 (step 3, reason: capacity_overflow)
READ k1=None (step 5)
# Result: CRITICAL FAILURE (high importance lost)
```

### 2. Memory Overwritten
**Cause**: Key updated with different value

**Example**:
```python
WRITE k1=v1 (step 1, importance=0.8)
UPDATE k1=v2 (step 2, importance=0.3)
READ k1=v2 (step 3)
# Result: CRITICAL FAILURE (important data replaced)
```

### 3. Invalid Read
**Cause**: Attempted to read key that was never written

**Example**:
```python
READ k1=None (step 1)
# Result: Test artifact (not a memory failure)
```

---

## 💻 Usage Examples

### Example 1: Basic Usage

```python
from core.events import MemoryLayer
from agent.StructuredAgent import StructuredAgent
from tasks.recall_task import auto_evaluate_all

# Create agent with STM capacity
event_log = []
agent = StructuredAgent(stm_capacity=5, event_log=event_log)

# Execute commands
agent.execute_command({
    "action": "write",
    "key": "deadline",
    "value": "Friday",
    "layer": "STM",
    "importance": 0.9  # High importance
})

agent.execute_command({
    "action": "read",
    "key": "deadline"
})

# Auto-diagnose all reads
results = auto_evaluate_all(event_log)
for result in results:
    print(f"Key: {result['key']}")
    print(f"Passed: {result['passed']}")
    if result.get('is_critical'):
        print("⚠️ CRITICAL FAILURE!")
```

### Example 2: Random Scenario Testing

```python
from scenario import generate_scenario
from agent.StructuredAgent import StructuredAgent
from tasks.recall_task import auto_evaluate_all

# Generate random scenario
scenario = generate_scenario(
    scenario_id=1,
    num_steps=10,
    num_keys=5,
    read_prob=0.3,
    capacities=[5, 10, 15],
    seed=42
)

# Run scenario
event_log = []
agent = StructuredAgent(stm_capacity=scenario.capacity, event_log=event_log)

for action in scenario.actions:
    agent.execute_command(action)

# Evaluate
results = auto_evaluate_all(event_log)
```

---

## 📊 Key Metrics

### 1. Valid Recall Rate
**Formula**: `Passed / (Total - Invalid Reads)`

Measures recall success excluding invalid reads (test artifacts).

### 2. Memory Failure Rate
**Formula**: `(Evictions + Overwrites) / Total`

Percentage of failures caused by memory system issues.

### 3. Critical Failure Rate
**Formula**: `Critical Failures / Memory Failures`

Percentage of memory failures involving high-importance data.

### 4. Dominant Failure Mode
Most common failure type (guides optimization efforts).

---

## 🎓 Use Cases

### Research
- Analyze memory failure patterns in LLM agents
- Study impact of capacity constraints
- Benchmark different memory architectures

### Development
- Test memory systems during agent development
- Detect critical data loss before deployment
- Validate memory layer interactions (STM ↔ LTM)

### Debugging
- Diagnose why an agent forgot information
- Identify capacity bottlenecks
- Track importance-based failures

---

## 🛠️ API Reference

### StructuredAgent

```python
class StructuredAgent:
    def __init__(self, stm_capacity: int, event_log: List[MemoryEvent])
    
    def execute_command(self, command: Dict[str, Any]) -> Dict[str, Any]
```

**Command Format**:
```python
# Write to STM
{"action": "write", "key": "k1", "value": "v1", "layer": "STM", "importance": 0.8}

# Write to LTM
{"action": "write", "key": "k1", "value": "v1", "layer": "LTM", "importance": 0.9}

# Read (tries STM first, then LTM)
{"action": "read", "key": "k1"}
```

### auto_evaluate_all

```python
def auto_evaluate_all(event_log: List[MemoryEvent]) -> List[Dict[str, Any]]
```

**Returns**:
```python
[
    {
        "key": str,
        "read_step": int,
        "read_value": Any,
        "expected_value": Any,
        "passed": bool,
        "failure_type": str,
        "is_critical": bool,      # NEW
        "importance": float,      # NEW
        "evidence": List[str]
    }
]
```

---

## 🚧 Limitations

### What MemTrace Does NOT Do

1. **Real LLM Integration**: Uses structured commands, not actual LLM calls
2. **Semantic Understanding**: Simple key-value storage (no embeddings)
3. **Production Optimization**: Event logging has overhead
4. **Concurrency**: Single-threaded execution only
5. **External Memory**: No integration with vector databases

---

## 🤝 Contributing

Contributions welcome! Priority areas:

- [ ] Real LLM agent integration (LangChain, AutoGPT)
- [ ] Visualization dashboard
- [ ] Advanced eviction policies (LRU, LFU)
- [ ] Semantic retrieval (embeddings)
- [ ] Unit tests
- [ ] Performance optimization

---

## 📄 License

MIT License - See LICENSE file for details

---

## 📞 Contact

- **GitHub**: [Mahendra1706/MemTrace](https://github.com/Mahendra1706/MemTrace)
- **Branch**: `ltm` (latest features)
- **Main**: `main` (stable)

---

**Version**: 1.1.0 (LTM Branch)  
**Status**: Research Prototype  
**Last Updated**: 2026-02-09
