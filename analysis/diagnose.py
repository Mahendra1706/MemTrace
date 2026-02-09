# analysis/diagnose.py

from typing import List, Dict, Any
from core.events import MemoryEventType


def diagnose_failure(event_log, key: str, recall_step: int, importance_threshold: float = 0.7) -> Dict[str, Any]:
    """
    Diagnose why a memory recall failed and determine if it's a critical failure.
    
    Returns a dict with:
    - failure_type
    - evidence (list of strings)
    """

    writes = []
    evictions = []
    updates = []
    reads = []

    # Collect relevant events for this key
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

    # Never written - Invalid read operation
    if not writes:
        return {
            "failure_type": "invalid_read",
            "is_critical": False,  # Not a critical failure (key never existed)
            "importance": 0.0,
            "evidence": [
                f"No WRITE event found for key '{key}' before step {recall_step}",
                f"Attempted to read a key that was never stored"
            ],
        }

    # Case 2: Evicted before recall
    for ev in evictions:
        if ev.step < recall_step:
            importance = ev.metadata.get('importance', 0.5)
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

    # Case 3: Overwritten before recall
    for up in updates:
        if up.step < recall_step:
            old_importance = up.metadata.get('old_importance', 0.5)
            new_importance = up.metadata.get('importance', 0.5)
            is_critical = old_importance >= importance_threshold
            
            return {
                "failure_type": "memory_overwritten",
                "is_critical": is_critical,
                "old_importance": old_importance,
                "new_importance": new_importance,
                "evidence": [
                    f"Key '{key}' was overwritten at step {up.step}",
                    f"Old importance: {old_importance:.2f} {'(CRITICAL!)' if is_critical else '(normal)'}",
                    f"New importance: {new_importance:.2f}",
                    f"Recall attempted at step {recall_step}",
                ],
            }

    # Case 4: READ returned None (indirect eviction)
    for rd in reads:
        if rd.step == recall_step and rd.value is None:
            # Try to find importance from original write
            importance = writes[0].metadata.get('importance', 0.5) if writes else 0.5
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

    # Fallback: Unknown failure
    return {
        "failure_type": "unknown",
        "is_critical": False,
        "importance": 0.0,
        "evidence": ["Unable to determine failure cause from event log"],
    }
