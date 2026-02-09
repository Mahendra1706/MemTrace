# core/memory.py

from typing import Any, Dict, List, Optional
from collections import OrderedDict

from core.events import MemoryEvent, MemoryEventType, MemoryLayer


class MemoryStore:
    def __init__(
        self,
        event_log: List[MemoryEvent],
        capacity: Optional[int] = None,
    ):
        self.capacity = capacity
        self._store: OrderedDict[str, Any] = OrderedDict()
        self._event_log = event_log

  