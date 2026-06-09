"""
Diagnosis Engine — Analyzes event logs to determine WHY a memory recall failed.

Priority chain (no conflicts — first match wins):
  1. invalid_read      → Key was never written
  2. retrieval_miss    → Key not found, but a similar key exists (semantic)
  3. memory_evicted    → Key was evicted due to capacity
  4. memory_overwritten → Key was overwritten with a different value
  5. llm_hallucination → Value returned but doesn't match ground truth
  6. unknown           → Unable to determine cause

Semantic checks (optional): If an embedder is provided, Cases 1 and 5
get enhanced with semantic similarity to explain failures more deeply.
"""

from typing import List, Dict, Any, Optional, Callable
from core.events import MemoryEventType

try:
    from analysis.semantic import SemanticChecker, HAS_SEMANTIC
    _default_embedder = SemanticChecker() if HAS_SEMANTIC else None
except Exception:
    _default_embedder = None


def _collect_events(event_log, key: str):
    """Collect all events for a specific key, grouped by type."""
    writes = []
    evictions = []
    updates = []
    reads = []

    for event in event_log:
        if event.key != key:
            continue

        if event.event_type == MemoryEventType.WRITE:
            writes.append(event)
        elif event.event_type == MemoryEventType.EVICT:
            evictions.append(event)
        elif event.event_type == MemoryEventType.UPDATE:
            updates.append(event)
        elif event.event_type == MemoryEventType.READ:
            reads.append(event)

    return writes, evictions, updates, reads


def _get_all_stored_keys(event_log) -> Dict[str, Any]:
    """Extract all keys that were ever written, with their latest values."""
    stored = {}
    for event in event_log:
        if event.event_type in (MemoryEventType.WRITE, MemoryEventType.UPDATE):
            stored[event.key] = event.value
    return stored


def _semantic_find_similar(key: str, all_keys: Dict[str, Any], embedder) -> Optional[Dict]:
    """
    Use embedder to find a semantically similar key.
    Returns {"key": ..., "value": ..., "score": ...} or None.
    
    Never crashes — catches all exceptions.
    """
    if not embedder or not all_keys:
        return None

    try:
        result = embedder.find_similar(key, list(all_keys.keys()))
        if result:
            matched_key, score = result
            return {
                "key": matched_key,
                "value": all_keys[matched_key],
                "score": score,
            }
    except Exception:
        pass  

    return None


def diagnose_failure(
    event_log,
    key: str,
    recall_step: int,
    importance_threshold: float = 0.7,
    embedder=_default_embedder, 
) -> Dict[str, Any]:
    """
    Diagnose why a memory recall failed.
    
    Args:
        event_log: Full list of MemoryEvents
        key: The key that was read
        recall_step: The step at which the read happened
        importance_threshold: Score above which a failure is "critical"
        embedder: Optional semantic checker (has .find_similar method)
    
    Returns:
        Dict with failure_type, is_critical, evidence[], and optional semantic_hint
    """

    writes, evictions, updates, reads = _collect_events(event_log, key)
    all_stored = _get_all_stored_keys(event_log)

    # ================================================================
    # CASE 1: Key was NEVER written
    # ================================================================
    if not writes:
        # Semantic enhancement: is there a similar key the LLM meant to read?
        hint = _semantic_find_similar(key, all_stored, embedder)

        if hint:
            return {
                "failure_type": "retrieval_miss",
                "is_critical": True,
                "importance": 0.0,
                "semantic_hint": hint,
                "evidence": [
                    f"Key '{key}' was never stored in memory",
                    f"Semantic match found: '{hint['key']}' (similarity: {hint['score']:.2f})",
                    f"Stored value: '{hint['value']}'",
                    f"LLM used the wrong key name — data exists under a different key",
                ],
            }

        return {
            "failure_type": "invalid_read",
            "is_critical": False,
            "importance": 0.0,
            "evidence": [
                f"No WRITE event found for key '{key}' before step {recall_step}",
                f"Attempted to read a key that was never stored",
            ],
        }

    # ================================================================
    # CASE 2: Key was EVICTED (explicit eviction event exists)
    # ================================================================
    for ev in evictions:
        if ev.step < recall_step:
            importance = ev.metadata.get("importance", 0.5)
            is_critical = importance >= importance_threshold

            return {
                "failure_type": "memory_evicted",
                "is_critical": is_critical,
                "importance": importance,
                "evidence": [
                    f"Key '{key}' was written at step {writes[0].step}",
                    f"Evicted at step {ev.step} due to {ev.metadata.get('reason')}",
                    f"Importance: {importance:.2f} {'(CRITICAL!)' if is_critical else '(normal)'}",
                    f"Recall attempted at step {recall_step}",
                ],
            }

    # ================================================================
    # CASE 3: Key was OVERWRITTEN with a different value
    # ================================================================
    for up in updates:
        if up.step < recall_step:
            old_value = up.metadata.get("old_value")
            new_value = up.value

            # Skip same-value "overwrites" 
            if old_value == new_value:
                continue

            old_importance = up.metadata.get("old_importance", 0.5)
            new_importance = up.metadata.get("importance", 0.5)
            is_critical = old_importance >= importance_threshold

            return {
                "failure_type": "memory_overwritten",
                "is_critical": is_critical,
                "old_importance": old_importance,
                "new_importance": new_importance,
                "evidence": [
                    f"Key '{key}' was overwritten at step {up.step}",
                    f"Old value: '{old_value}' → New value: '{new_value}'",
                    f"Old importance: {old_importance:.2f} {'(CRITICAL!)' if is_critical else '(normal)'}",
                    f"New importance: {new_importance:.2f}",
                    f"Recall attempted at step {recall_step}",
                ],
            }

    # ================================================================
    # CASE 4: READ returned None (indirect eviction — no explicit evict event)
    # ================================================================
    for rd in reads:
        if rd.step == recall_step and rd.value is None:
            importance = writes[0].metadata.get("importance", 0.5) if writes else 0.5
            is_critical = importance >= importance_threshold

            return {
                "failure_type": "memory_evicted",
                "is_critical": is_critical,
                "importance": importance,
                "evidence": [
                    f"Key '{key}' was written at step {writes[0].step}",
                    f"READ at step {recall_step} returned None",
                    f"Importance: {importance:.2f} {'(CRITICAL!)' if is_critical else '(normal)'}",
                    f"Likely evicted due to capacity overflow (indirect eviction)",
                ],
            }

    # ================================================================
    # CASE 5: Value returned but WRONG (hallucination or retrieval miss)
    # ================================================================
    for rd in reads:
        if rd.step == recall_step and rd.value is not None:
            importance = writes[0].metadata.get("importance", 0.5) if writes else 0.5
            is_critical = importance >= importance_threshold

            # Semantic enhancement: did the LLM read the WRONG key?
            # Check if another key in memory has the EXPECTED (original) value
            expected_value = writes[0].value if writes else None
            if embedder and expected_value:
                for stored_key, stored_val in all_stored.items():
                    if stored_val == expected_value and stored_key != key:
                        return {
                            "failure_type": "retrieval_miss",
                            "is_critical": is_critical,
                            "importance": importance,
                            "evidence": [
                                f"Key '{key}' returned '{rd.value}' instead of '{expected_value}'",
                                f"Correct value exists under key '{stored_key}'",
                                f"LLM read the wrong key — data is intact under a different name",
                            ],
                        }

            return {
                "failure_type": "llm_hallucination",
                "is_critical": is_critical,
                "importance": importance,
                "evidence": [
                    f"Key '{key}' was written at step {writes[0].step}",
                    f"READ at step {recall_step} returned '{rd.value}'",
                    f"Expected original value but got a different value",
                    f"Memory was not evicted or overwritten — LLM returned wrong data",
                ],
            }

    # ================================================================
    # FALLBACK: Unknown failure
    # ================================================================
    return {
        "failure_type": "unknown",
        "is_critical": False,
        "importance": 0.0,
        "evidence": ["Unable to determine failure cause from event log"],
    }
