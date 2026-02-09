# core/ltm.py
from typing import Any, Dict, List, Optional
from collections import OrderedDict
from core.events import MemoryEvent, MemoryEventType, MemoryLayer


class LongTermMemory:
    """Long-Term Memory - No eviction, unlimited capacity"""

    def __init__(self, event_log: List[MemoryEvent]):
        self.layer = MemoryLayer.LTM
        self._store = OrderedDict() 
        self._importance_map = {} 
        self._event_log = event_log  

    def ltm_write(
        self,
        key: str,
        value: Any,
        step: int,
        layer: Optional[MemoryLayer] = MemoryLayer.LTM,
        importance: float = 0.5,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        # Use provided layer or default to LTM
        target_layer = layer if layer is not None else self.layer
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

    def ltm_read(
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
