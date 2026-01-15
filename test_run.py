# test_run.py

from events import MemoryLayer
from memory import MemoryStore

events = []

stm = MemoryStore(
    memory_layer=MemoryLayer.STM,
    event_log=events,
)

# Step 2: write memory
stm.write(
    key="deadline",
    value="Friday",
    step=2,
    metadata={"source": "user"},
)

# Step 7: read memory (simulate failure)
result = stm.read(
    key="deadline",
    step=7,
)

print("READ RESULT:", result)
print("\nMEMORY EVENTS:")
for e in events:
    print(e)
