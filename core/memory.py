# memory.py

from typing import Any, Dict, List, Optional

from .events import MemoryEvent, MemoryEventType, MemoryLayer


class MemoryStore:
    def __init__(
        self,
        memory_layer: MemoryLayer,
        event_log: List[MemoryEvent],
    ):
        self.memory_layer = memory_layer
        self._store: Dict[str, Any] = {}
        self._event_log = event_log

    def write(
        self,
        key: str,
        value: Any,
        step: int,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        # store the value
        self._store[key] = value

        # record the write event
        event = MemoryEvent.create(
            event_type=MemoryEventType.WRITE,
            memory_layer=self.memory_layer,
            step=step,
            key=key,
            value=value,
            metadata=metadata,
        )

        self._event_log.append(event)

    def read(
        self,
        key: str,
        step: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        value = self._store.get(key)

        event = MemoryEvent.create(
            event_type=MemoryEventType.READ,
            memory_layer=self.memory_layer,
            step=step,
            key=key,
            value=value,
            metadata=metadata,
        )

        self._event_log.append(event)

        return value

    def store_deadline(self, deadline: str):
        step = self._next_step()
        self.memory.write(
            key="deadline",
            value=deadline,
            step=step,
            metadata={"source": "user"},
        )

    