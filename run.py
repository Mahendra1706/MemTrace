from core.events import MemoryLayer
from core.memory import MemoryStore
from agent.StructuredAgent import StructuredAgent
from tasks.recall_task import auto_evaluate_all

from scenario import (
    overwrite_scenario, 
    eviction_scenario, 
    successful_recall_scenario,
    mixed_operations_scenario,
    llm_error_scenario
)


def run_scenario(scenario, capacity):
    """
    Run a scenario with given memory capacity and return event log.
    """
    print(f"\n{'='*60}")
    print(f"Scenario: {scenario.name}")
    print(f"Capacity: {capacity}")
    print('='*60)
    
    event_log = []
    
    memory = MemoryStore(
        capacity=capacity,
        event_log=event_log,
        memory_layer=MemoryLayer.STM,
    )
    
    agent = StructuredAgent(memory)
    
    # Execute all actions
    print("\nExecuting actions: \n")
    for action in scenario.actions:
        result = agent.execute_command(action)
        print(f"  Command: {action}")
    
    # Show all events from event_log 
    print("\nEvent Log (all memory operations):")
    for event in event_log:
        print(f"  {event}")
    
    return event_log



def print_diagnosis(results):
    """
    Print diagnosis results in a readable format.
    """
    print("\n" + "-"*60)
    print("AUTO-DIAGNOSIS")
    print("-"*60)
    
    if not results:
        print("  ⚠️  No READ events found")
        return
    
    for i, result in enumerate(results, 1):
        key = result['key']
        read_step = result['read_step']
        read_value = result['read_value']
        expected = result['expected_value']
        
        print(f"\n[{i}] Key '{key}' (read at step {read_step})")
        
        if result['passed']:
            print(f"    ✅ PASSED: Successfully recalled '{key}'='{expected}'")
        else:
            print(f"    ❌ FAILED")
            print(f"       Expected: '{expected}'")
            print(f"       Got:      '{read_value}'")
            print(f"       Failure:  {result['failure_type']}")
            print(f"       Evidence:")
            for line in result['evidence']:
                print(f"         • {line}")
    
    # Summary
    passed = sum(1 for r in results if r['passed'])
    failed = sum(1 for r in results if not r['passed'])
    print(f"\n{'='*60}")
    print(f"Summary: {passed} passed, {failed} failed")
    print('='*60)


def main():
    """
    Run scenarios with different capacities and auto-diagnose.
    """
    # Test configurations
    configs = [
        # Overwrite scenarios
        (overwrite_scenario, 10),   # Large capacity - should show UPDATE events
        
        # Eviction scenarios
        (eviction_scenario, 1),     # Small capacity - should show EVICT events
        (eviction_scenario, 3),     # Exact capacity - no eviction
        
        # Successful recall (control)
        (successful_recall_scenario, 10),  # Should PASS
        
        # Mixed operations
        (mixed_operations_scenario, 10),   # Large capacity - mixed results
        (mixed_operations_scenario, 2),    # Small capacity - eviction + updates
        
        # Note: LLM hallucination detection is implemented in diagnose.py
        # but cannot be tested without real LLM integration
    ]
    
    for scenario, capacity in configs:
        # Run scenario
        event_log = run_scenario(scenario, capacity)
        
        # Auto-diagnose all READ events
        results = auto_evaluate_all(event_log)
        
        # Print diagnosis
        print_diagnosis(results)
    

if __name__ == "__main__":
    main()
