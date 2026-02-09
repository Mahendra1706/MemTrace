from typing import Any, Dict, List, Optional
from collections import OrderedDict
from core.events import MemoryEvent, MemoryEventType, MemoryLayer

class ShortTermMemory:
    def __init__(
        self,
        capacity: int,
        event_log: List[MemoryEvent],
    ):
        self.capacity = capacity
        self.layer = MemoryLayer.STM
        self._store = OrderedDict()  
        self._importance_map = {}  # Track importance for each key
        self._event_log = event_log 

    def stm_write(
        self,
        key: str,
        value: Any,
        step: int,
        layer: Optional[MemoryLayer] = MemoryLayer.STM,
        importance: float = 0.5,  # FIXED: Added importance parameter
        metadata: Optional[Dict[str, Any]] = None,
    ):
        target_layer = layer if layer is not None else MemoryLayer.STM
        
        # If key exists, overwrite (UPDATE)
        if key in self._store:
            old_value = self._store[key]
            old_importance = self._importance_map.get(key, 0.5)  
            
            self._store[key] = value
            self._importance_map[key] = importance  

            event = MemoryEvent.create(
                event_type=MemoryEventType.UPDATE,
                memory_layer=target_layer,
                step=step,
                key=key,
                value=value,
                metadata={
                    "old_value": old_value,
                    "old_importance": old_importance,  
                    "importance": importance,           
                    **(metadata or {}),
                },
            )
            self._event_log.append(event)
            return

        # If capacity exceeded, evict oldest
        if self.capacity is not None and len(self._store) >= self.capacity:
            evicted_key, evicted_value = self._store.popitem(last=False)
            evicted_importance = self._importance_map.pop(evicted_key, 0.5)  
            evict_event = MemoryEvent.create(
                event_type=MemoryEventType.EVICT,
                memory_layer=target_layer,
                step=step,
                key=evicted_key,
                value=evicted_value,
                metadata={
                    "reason": "capacity_overflow",
                    "importance": evicted_importance,  
                },
            )
            self._event_log.append(evict_event)

        # Write new value
        self._store[key] = value
        self._importance_map[key] = importance  

        write_event = MemoryEvent.create(
            event_type=MemoryEventType.WRITE,
            memory_layer=target_layer,
            step=step,
            key=key,
            value=value,
            metadata={
                "importance": importance,  
                **(metadata or {}),
            },
        )
        self._event_log.append(write_event)

    def stm_read(
        self,
        key: str,
        step: int,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Optional[Any]:
        value = self._store.get(key)

        read_event = MemoryEvent.create(
            event_type=MemoryEventType.READ,
            memory_layer=self.layer, 
            step=step,
            key=key,
            value=value,
            metadata=metadata,
        )
        self._event_log.append(read_event)

        return value
