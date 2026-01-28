# Changelog

All notable changes to MemTrace will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] - 2026-01-28

### 🎉 Initial Release

**MemTrace v1.0** - A statistical testing framework for memory systems in LLM agents.

### Added

#### Core Features
- **Event Sourcing System**: Complete audit trail of all memory operations
  - `MemoryEvent` data structure with timestamp, step, and metadata
  - Event types: WRITE, READ, UPDATE, EVICT
  - Immutable event log as single source of truth

- **Short-Term Memory (STM)**: Capacity-constrained key-value store
  - FIFO eviction policy when capacity exceeded
  - Automatic UPDATE detection for key overwrites
  - OrderedDict-based implementation for deterministic behavior

- **Structured Agent**: Command processor for memory operations
  - JSON-based command interface
  - Support for WRITE and READ operations
  - LLM hallucination simulation via `returned_value` parameter

- **Automated Diagnosis**: Root cause analysis for memory failures
  - 4 failure types: eviction, overwriting, invalid read, hallucination
  - Evidence-based diagnosis with event references
  - 100% failure categorization (zero unknown failures)

- **Random Scenario Generation**: Configurable test case generation
  - Parameterized: num_steps, num_keys, read_prob, capacities
  - Seeded random generation for reproducibility
  - Support for 1000+ scenarios in single run

- **Statistical Analysis**: Aggregate metrics across scenarios
  - Pass/fail rates
  - Failure type distribution
  - Capacity impact analysis

#### Documentation
- Comprehensive README with architecture, API reference, and examples
- System invariants documentation
- Explicit claims and non-claims
- Usage examples for common scenarios

#### Testing
- Validated across 1000+ random scenarios
- 3000+ memory operations analyzed
- Statistical validation of capacity-eviction relationship

### Validated Invariants

```
Capacity ↑ → Eviction ↓
Overwrite ~ independent of capacity
Invalid Read = scenario artifact
Unknown = 0 always
```

### Statistical Baseline (1000 scenarios, capacity 10-30)

```
Total Reads: 3030
✅ Passed: 878 (29.0%)
❌ Failed: 2152 (71.0%)

Failure Breakdown:
  • Memory Evicted: 994 (32.8%)
  • Memory Overwritten: 343 (11.3%)
  • Invalid Read: 815 (26.9%)
  • LLM Hallucination: 0 (0.0%)
  • Unknown: 0 (0.0%)
```

### Known Limitations

- STM only (no LTM or consolidation)
- Simple FIFO eviction (no LRU, LFU, or importance-based)
- No semantic retrieval or embeddings
- Single-threaded execution only
- No external memory system integration

---

## [Unreleased]

### Planned for v1.1
- LLM hallucination in random scenarios
- Visualization (matplotlib charts)
- Export results to JSON
- Performance benchmarks

### Planned for v2.0
- Long-Term Memory (LTM) implementation
- STM → LTM consolidation with importance scoring
- Semantic retrieval with embeddings
- Multi-layer memory architecture
- LangChain/LlamaIndex integration

---

## Version History

- **v1.0.0** (2026-01-28) - Initial release with STM and statistical testing
