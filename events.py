# events.py

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, Optional
import time
import uuid


class MemoryEventType(Enum):
    WRITE = "write"
    READ = "read"
    UPDATE = "update"
    EVICT = "evict"


class MemoryLayer(Enum):
    STM = "short_term"
    LTM = "long_term"
    WEIGHT = "weight"


@dataclass
class MemoryEvent:
    event_id: str
    event_type: MemoryEventType
    memory_layer: MemoryLayer
    step: int
    timestamp: float
    key: Optional[str] = None
    value: Optional[Any] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    @staticmethod
    def create(
        event_type: MemoryEventType,
        memory_layer: MemoryLayer,
        step: int,
        key: Optional[str] = None,
        value: Optional[Any] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        return MemoryEvent(
            event_id=str(uuid.uuid4()),
            event_type=event_type,
            memory_layer=memory_layer,
            step=step,
            timestamp=time.time(),
            key=key,
            value=value,
            metadata=metadata or {},
        )

    def __str__(self):
        return (
            f"[step={self.step}] {self.event_type.value.upper()} "
            f"({self.memory_layer.value}) key={self.key} meta={self.metadata}"
        )
