from core.events import MemoryLayer
from core.memory import MemoryStore
from agent.StructuredAgent import StructuredAgent
from tasks.recall_task import auto_evaluate_all

from scenario import generate_scenario

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
    # Generate 50 random scenarios
    from scenario import generate_scenario
    
    print("\n" + "="*60)
    print("MEMTRACE RANDOM TESTING - 50 Scenarios")
    print("="*60)
    
    # Statistics counters
    stats = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "memory_evicted": 0,
        "memory_overwritten": 0,
        "llm_hallucination": 0,
        "invalid_read": 0,
        "unknown": 0,
    }
    
    # Generate 50 random scenarios
    for i in range(1000):
        scenario = generate_scenario(
            scenario_id=i,
            num_steps=10,
            num_keys=5,
            read_prob=0.3,
            capacities=[10,15,20,25,30],
            seed=42
        )
        
        capacity = scenario.capacity
        
        # Run scenario (commented out verbose output)
        # print(f"\n{'='*60}")
        # print(f"Scenario: {scenario.name}")
        # print(f"Capacity: {capacity}")
        # print('='*60)
        
        event_log = []
        
        memory = MemoryStore(
            capacity=capacity,
            event_log=event_log,
            memory_layer=MemoryLayer.STM,
        )
        
        agent = StructuredAgent(memory)
        
        # Execute all actions (commented out verbose output)
        # print("\nExecuting actions:")
        for action in scenario.actions:
            result = agent.execute_command(action)
            # print(f"  Command: {action}")
        
        # Show all events from event_log (commented out)
        # print("\nEvent Log (all memory operations):")
        # for event in event_log:
        #     print(f"  {event}")
        
        # Auto-diagnose all READ events
        results = auto_evaluate_all(event_log)
        
        # Update statistics
        for result in results:
            stats["total"] += 1
            if result["passed"]:
                stats["passed"] += 1
            else:
                stats["failed"] += 1
                failure_type = result["failure_type"]
                if failure_type in stats:
                    stats[failure_type] += 1
        
        # Print diagnosis (commented out)
        # print_diagnosis(results)
    
    # Print final statistics
    print("\n" + "="*60)
    print("FINAL STATISTICS")
    print("="*60)
    print(f"Total Reads: {stats['total']}")
    print(f"✅ Passed: {stats['passed']} ({stats['passed']/stats['total']*100:.1f}%)")
    print(f"❌ Failed: {stats['failed']} ({stats['failed']/stats['total']*100:.1f}%)")
    print("\nFailure Breakdown:")
    print(f"  • Memory Evicted: {stats['memory_evicted']}")
    print(f"  • Memory Overwritten: {stats['memory_overwritten']}")
    print(f"  • Invalid Read: {stats['invalid_read']}")
    print(f"  • LLM Hallucination: {stats['llm_hallucination']}")
    print(f"  • Unknown: {stats['unknown']}")
    
    # Calculate advanced metrics
    print("\n" + "-"*60)
    print("ADVANCED METRICS")
    print("-"*60)
    
    # 1. Valid Recall Rate (excludes "invalid_read")
    valid_attempts = stats['total'] - stats['invalid_read']
    if valid_attempts > 0:
        valid_recall_rate = (stats['passed'] / valid_attempts) * 100
        print(f"Valid Recall Rate: {valid_recall_rate:.1f}%")
        print(f"  (Excludes {stats['invalid_read']} invalid reads)")
    else:
        print("Valid Recall Rate: N/A (no valid attempts)")
    
    # 2. Memory Failure Rate (eviction + overwrite)
    memory_failures = stats['memory_evicted'] + stats['memory_overwritten']
    if stats['total'] > 0:
        memory_failure_rate = (memory_failures / stats['total']) * 100
        print(f"\nMemory Failure Rate: {memory_failure_rate:.1f}%")
        print(f"  (Eviction: {stats['memory_evicted']}, Overwrite: {stats['memory_overwritten']})")
    else:
        print("\nMemory Failure Rate: N/A")
    
    # 3. Dominant Failure Mode (argmax over failure types)
    failure_types = {
        'Memory Evicted': stats['memory_evicted'],
        'Memory Overwritten': stats['memory_overwritten'],
        'Invalid Read': stats['invalid_read'],
        'LLM Hallucination': stats['llm_hallucination'],
        'Unknown': stats['unknown']
    }
    
    if stats['failed'] > 0:
        dominant_mode = max(failure_types, key=failure_types.get)
        dominant_count = failure_types[dominant_mode]
        dominant_pct = (dominant_count / stats['failed']) * 100
        print(f"\nDominant Failure Mode: {dominant_mode}")
        print(f"  ({dominant_count}/{stats['failed']} failures, {dominant_pct:.1f}%)")
    else:
        print("\nDominant Failure Mode: N/A (no failures)")
    
    print("="*60)


if __name__ == "__main__":
    main()
