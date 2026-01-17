# core/memory.py

from typing import Any, Dict, List, Optional
from collections import OrderedDict

from core.events import MemoryEvent, MemoryEventType, MemoryLayer


class MemoryStore:
    def __init__(
        self,
        memory_layer: MemoryLayer,
        event_log: List[MemoryEvent],
        capacity: Optional[int] = None,  # NEW
    ):
        self.memory_layer = memory_layer
        self.capacity = capacity
        self._store: OrderedDict[str, Any] = OrderedDict()
        self._event_log = event_log

    def write(
        self,
        key: str,
        value: Any,
        step: int,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        # If key exists, overwrite (UPDATE)
        if key in self._store:
            old_value = self._store[key]
            self._store[key] = value

            event = MemoryEvent.create(
                event_type=MemoryEventType.UPDATE,
                memory_layer=self.memory_layer,
                step=step,
                key=key,
                value=value,
                metadata={
                    "old_value": old_value,
                    **(metadata or {}),
                },
            )
            self._event_log.append(event)
            return

        # If capacity exceeded, evict oldest
        if self.capacity is not None and len(self._store) >= self.capacity:
            evicted_key, evicted_value = self._store.popitem(last=False)

            evict_event = MemoryEvent.create(
                event_type=MemoryEventType.EVICT,
                memory_layer=self.memory_layer,
                step=step,
                key=evicted_key,
                value=evicted_value,
                metadata={"reason": "capacity_overflow"},
            )
            self._event_log.append(evict_event)

        # Write new value
        self._store[key] = value

        write_event = MemoryEvent.create(
            event_type=MemoryEventType.WRITE,
            memory_layer=self.memory_layer,
            step=step,
            key=key,
            value=value,
            metadata=metadata,
        )
        self._event_log.append(write_event)

    def read(
        self,
        key: str,
        step: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        value = self._store.get(key)

        read_event = MemoryEvent.create(
            event_type=MemoryEventType.READ,
            memory_layer=self.memory_layer,
            step=step,
            key=key,
            value=value,
            metadata=metadata,
        )
        self._event_log.append(read_event)

        return value
