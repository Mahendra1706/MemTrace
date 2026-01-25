# analysis/diagnose.py

from typing import List, Dict, Any
from core.events import MemoryEventType


def diagnose_failure(event_log, key: str, recall_step: int) -> Dict[str, Any]:
    """
    Diagnose why a memory recall failed.

    for now we have basic and few diagnoses available

    Returns a dict with:
    - failure_type
    - evidence (list of strings)
    """

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

    # 1️⃣ Never written
    if not writes:
        return {
            "failure_type": "memory_never_written",
            "evidence": [
                f"No WRITE event found for key '{key}' before step {recall_step}"
            ],
        }

    # 2️⃣ Evicted before recall
    for ev in evictions:
        if ev.step < recall_step:
            return {
                "failure_type": "memory_evicted",
                "evidence": [
                    f"Key '{key}' was written at step {writes[0].step}",
                    f"Evicted at step {ev.step} due to {ev.metadata.get('reason')}",
                    f"Recall attempted at step {recall_step}",
                ],
            }

    # 3️⃣ Overwritten before recall
    for up in updates:
        if up.step < recall_step:
            return {
                "failure_type": "memory_overwritten",
                "evidence": [
                    f"Key '{key}' was overwritten at step {up.step}",
                    f"Old value replaced before recall at step {recall_step}",
                ],
            }

    # 4️⃣ Retrieval miss
    for rd in reads:
        if rd.step == recall_step and rd.value is None:
            return {
                "failure_type": "retrieval_miss",
                "evidence": [
                    f"READ at step {recall_step} returned None",
                    f"Memory existed but was not retrieved",
                ],
            }

    # Fallback (should not happen often)
    return {
        "failure_type": "unknown",
        "evidence": ["Unable to determine failure cause from event log"],
    }
