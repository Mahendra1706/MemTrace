# run.py

from core.events import MemoryLayer, MemoryEventType
from core.memory import MemoryStore
from agent.toy_agent import ToyAgent
from analysis.explain import explain_failure


def print_separator(title: str):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_events(event_log):
    print("\n--- Event Trace ---")
    for event in event_log:
        print(event)


def scenario_1_eviction():
    """Test eviction due to capacity overflow"""
    print_separator("SCENARIO 1: Eviction (Capacity Overflow)")
    
    event_log = []
    stm = MemoryStore(
        memory_layer=MemoryLayer.STM,
        event_log=event_log,
        capacity=2,  # Can only hold 2 items
    )
    agent = ToyAgent(memory=stm)
    
    # Write 3 different keys - first one should be evicted
    print("\nUSER: My deadline is Friday")
    print("AGENT:", agent.run_turn("My deadline is Friday"))
    
    print("\nUSER: My meeting is at 3pm")
    agent.observe("My meeting is at 3pm")
    step = agent._next_step()
    stm.write(key="meeting", value="3pm", step=step, metadata={"source": "user"})
    print("AGENT: Got it. I've noted your meeting.")
    
    print("\nUSER: My budget is $500")
    agent.observe("My budget is $500")
    step = agent._next_step()
    stm.write(key="budget", value="$500", step=step, metadata={"source": "user"})
    print("AGENT: Got it. I've noted your budget.")
    
    # Try to recall the deadline (should fail - evicted)
    print("\nUSER: What is my deadline?")
    response = agent.run_turn("What is my deadline?")
    print("AGENT:", response)
    
    print_events(event_log)
    
    # Find the failed read event
    failed_read = None
    for event in event_log:
        if (event.event_type == MemoryEventType.READ and 
            event.key == "deadline" and 
            event.value is None):
            failed_read = event
            break
    
    if failed_read:
        print("\n--- Failure Analysis ---")
        print(explain_failure(event_log, failed_read))


def scenario_2_overwrite():
    """Test overwrite/interference"""
    print_separator("SCENARIO 2: Overwrite/Interference")
    
    event_log = []
    stm = MemoryStore(
        memory_layer=MemoryLayer.STM,
        event_log=event_log,
        capacity=5,  # Large enough to avoid eviction
    )
    agent = ToyAgent(memory=stm)
    
    # Write deadline = Friday
    print("\nUSER: My deadline is Friday")
    print("AGENT:", agent.run_turn("My deadline is Friday"))
    
    # Overwrite deadline = Monday
    print("\nUSER: My deadline is Monday")
    print("AGENT:", agent.run_turn("My deadline is Monday"))
    
    # Read deadline (will get Monday, not Friday)
    print("\nUSER: What is my deadline?")
    print("AGENT:", agent.run_turn("What is my deadline?"))
    
    print_events(event_log)
    
    # Analyze the overwrite
    print("\n--- Interference Analysis ---")
    print("Note: The deadline was overwritten from 'Friday' to 'Monday'.")
    print("This demonstrates UPDATE events (interference), not eviction.")
    
    # Find UPDATE event
    for event in event_log:
        if event.event_type == MemoryEventType.UPDATE and event.key == "deadline":
            print(f"\nUPDATE detected at step {event.step}:")
            print(f"  Old value: {event.metadata.get('old_value')}")
            print(f"  New value: {event.value}")


def scenario_3_never_written():
    """Test reading a key that was never written"""
    print_separator("SCENARIO 3: Never Written")
    
    event_log = []
    stm = MemoryStore(
        memory_layer=MemoryLayer.STM,
        event_log=event_log,
        capacity=5,
    )
    agent = ToyAgent(memory=stm)
    
    # Try to read a key that was never written
    print("\nUSER: What is my meeting?")
    agent.observe("What is my meeting?")
    step = agent._next_step()
    value = stm.read(key="meeting", step=step, metadata={"reason": "answering_user"})
    
    if value is None:
        print("AGENT: I don't have any information about your meeting.")
    else:
        print(f"AGENT: Your meeting is {value}.")
    
    print_events(event_log)
    
    # Find the failed read event
    failed_read = None
    for event in event_log:
        if (event.event_type == MemoryEventType.READ and 
            event.key == "meeting" and 
            event.value is None):
            failed_read = event
            break
    
    if failed_read:
        print("\n--- Failure Analysis ---")
        print(explain_failure(event_log, failed_read))


def scenario_4_successful_read():
    """Test successful read (control scenario)"""
    print_separator("SCENARIO 4: Successful Read (Control)")
    
    event_log = []
    stm = MemoryStore(
        memory_layer=MemoryLayer.STM,
        event_log=event_log,
        capacity=5,
    )
    agent = ToyAgent(memory=stm)
    
    # Write and immediately read
    print("\nUSER: My deadline is Friday")
    print("AGENT:", agent.run_turn("My deadline is Friday"))
    
    print("\nUSER: What is my deadline?")
    print("AGENT:", agent.run_turn("What is my deadline?"))
    
    print_events(event_log)
    
    print("\n--- Success Analysis ---")
    print("✅ Read was successful - no failure to analyze.")


def main():
    """Run all test scenarios"""
    print("\n" + "🔹" * 30)
    print("  MemTrace: Memory Failure Diagnostics")
    print("🔹" * 30)
    
    scenario_1_eviction()
    scenario_2_overwrite()
    scenario_3_never_written()
    scenario_4_successful_read()
    
    print("\n" + "=" * 60)
    print("  All scenarios complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()
