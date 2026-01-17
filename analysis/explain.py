# analysis/explain.py

from typing import List, Optional, Tuple
from core.events import MemoryEvent, MemoryEventType


def explain_failure(event_log: List[MemoryEvent], failed_read_event: MemoryEvent) -> str:
    """
    Explain WHY a memory read failed based on the event log.
    
    Returns a human-readable diagnosis that references:
    - key
    - step of WRITE (if applicable)
    - step of EVICT or UPDATE (if applicable)
    - step of READ
    
    No guessing - only evidence from logged events.
    """
    if failed_read_event.event_type != MemoryEventType.READ:
        return "Error: Not a READ event"
    
    if failed_read_event.value is not None:
        return "No failure detected - read was successful"
    
    key = failed_read_event.key
    read_step = failed_read_event.step
    
    # Check each failure mode in order
    
    # 1. Check if memory was never written
    never_written = _check_never_written(event_log, key, read_step)
    if never_written:
        return (
            f"Failure because memory was never written.\n"
            f"  Key: '{key}'\n"
            f"  Read at step: {read_step}\n"
            f"  No WRITE event found for this key before the read."
        )
    
    # 2. Check for eviction (capacity overflow)
    eviction_info = _check_eviction(event_log, key, read_step)
    if eviction_info:
        write_step, evict_step = eviction_info
        return (
            f"Failure due to STM eviction (capacity overflow).\n"
            f"  Key: '{key}'\n"
            f"  Written at step: {write_step}\n"
            f"  Evicted at step: {evict_step}\n"
            f"  Read at step: {read_step}\n"
            f"  Reason: Memory was evicted due to capacity constraints."
        )
    
    # 3. Check for overwrite/interference
    overwrite_info = _check_overwrite(event_log, key, read_step)
    if overwrite_info:
        write_step, update_step, old_value, new_value = overwrite_info
        return (
            f"Failure due to overwrite/interference.\n"
            f"  Key: '{key}'\n"
            f"  Originally written at step: {write_step}\n"
            f"  Overwritten at step: {update_step}\n"
            f"  Read at step: {read_step}\n"
            f"  Old value: {old_value}\n"
            f"  New value: {new_value}\n"
            f"  Note: This is interference, not eviction."
        )
    
    # 4. Check for retrieval miss (memory exists but not returned)
    retrieval_miss = _check_retrieval_miss(event_log, key, read_step)
    if retrieval_miss:
        write_step = retrieval_miss
        return (
            f"Failure due to retrieval miss.\n"
            f"  Key: '{key}'\n"
            f"  Written at step: {write_step}\n"
            f"  Read at step: {read_step}\n"
            f"  Memory existed but was not returned (possible bug in retrieval logic)."
        )
    
    return "Unknown failure mode - insufficient event data"


def _check_never_written(event_log: List[MemoryEvent], key: str, read_step: int) -> bool:
    """
    Check if the key was never written before the read.
    Returns True if no WRITE event exists for this key before read_step.
    """
    for event in event_log:
        if event.step >= read_step:
            break
        if event.key == key and event.event_type == MemoryEventType.WRITE:
            return False
    return True


def _check_eviction(event_log: List[MemoryEvent], key: str, read_step: int) -> Optional[Tuple[int, int]]:
    """
    Check if the key was evicted due to capacity overflow.
    Returns (write_step, evict_step) if eviction occurred, None otherwise.
    """
    write_step = None
    evict_step = None
    
    for event in event_log:
        if event.step >= read_step:
            break
        
        if event.key == key:
            if event.event_type == MemoryEventType.WRITE:
                write_step = event.step
            elif event.event_type == MemoryEventType.EVICT:
                evict_step = event.step
    
    # Eviction occurred if we have both write and evict
    if write_step is not None and evict_step is not None:
        return (write_step, evict_step)
    
    return None


def _check_overwrite(event_log: List[MemoryEvent], key: str, read_step: int) -> Optional[Tuple[int, int, any, any]]:
    """
    Check if the key was overwritten (UPDATE event).
    Returns (write_step, update_step, old_value, new_value) if overwrite occurred, None otherwise.
    
    Note: This is for detecting interference, not necessarily a "failure" in all cases,
    but it explains why the value changed.
    """
    write_step = None
    update_step = None
    old_value = None
    new_value = None
    
    for event in event_log:
        if event.step >= read_step:
            break
        
        if event.key == key:
            if event.event_type == MemoryEventType.WRITE:
                write_step = event.step
            elif event.event_type == MemoryEventType.UPDATE:
                update_step = event.step
                old_value = event.metadata.get("old_value")
                new_value = event.value
    
    # Overwrite occurred if we have an UPDATE event
    if update_step is not None:
        return (write_step or update_step, update_step, old_value, new_value)
    
    return None


def _check_retrieval_miss(event_log: List[MemoryEvent], key: str, read_step: int) -> Optional[int]:
    """
    Check if memory was written but not evicted or updated, yet still failed to retrieve.
    This indicates a bug in the retrieval logic.
    Returns write_step if retrieval miss detected, None otherwise.
    """
    write_step = None
    was_evicted = False
    
    for event in event_log:
        if event.step >= read_step:
            break
        
        if event.key == key:
            if event.event_type == MemoryEventType.WRITE:
                write_step = event.step
            elif event.event_type == MemoryEventType.EVICT:
                was_evicted = True
            elif event.event_type == MemoryEventType.UPDATE:
                # UPDATE means the key still exists, just with a different value
                # This is not a retrieval miss
                return None
    
    # Retrieval miss: memory was written, not evicted, but read returned None
    if write_step is not None and not was_evicted:
        return write_step
    
    return None
