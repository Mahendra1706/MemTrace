from core.events import MemoryLayer
from agent.StructuredAgent import StructuredAgent
from tasks.recall_task import auto_evaluate_all
from scenario import generate_scenario


def main():
    """
    Run scenarios with different capacities and auto-diagnose.
    """
    
    print("\n" + "="*60)
    print("MEMTRACE RANDOM TESTING - 1000 Scenarios")
    print("="*60)
    
    # Statistics counters
    stats = {
        "total": 0,
        "passed": 0,
        "failed": 0,
        "memory_evicted": 0,
        "memory_overwritten": 0,
        "invalid_read": 0,
        "unknown": 0,
        "critical_failures": 0,
        "critical_evictions": 0,
        "critical_overwrites": 0,
    }
    
    # Generate 1000 random scenarios
    for i in range(1000):
        scenario = generate_scenario(
            scenario_id=i,
            num_steps=10,
            num_keys=5,
            read_prob=0.3,
            capacities=[10, 15, 20, 25, 30],
            seed=42
        )
        
        capacity = scenario.capacity
        event_log = []
        
        # Create agent with STM capacity
        agent = StructuredAgent(
            stm_capacity=capacity,
            event_log=event_log
        )
        
        # Execute all actions
        for action in scenario.actions:
            result = agent.execute_command(action)
        
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
                
                # Count critical failures
                if result.get("is_critical", False):
                    stats["critical_failures"] += 1
                    
                    if failure_type == "memory_evicted":
                        stats["critical_evictions"] += 1
                    elif failure_type == "memory_overwritten":
                        stats["critical_overwrites"] += 1
    
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
    print(f"  • Unknown: {stats['unknown']}")
    
    # Advanced metrics
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
    
    # 3. Dominant Failure Mode
    failure_types = {
        'Memory Evicted': stats['memory_evicted'],
        'Memory Overwritten': stats['memory_overwritten'],
        'Invalid Read': stats['invalid_read'],
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
    
    # 4. Critical Failures (NEW!)
    print("\n" + "-"*60)
    print("CRITICAL FAILURES (High-Importance Data Loss)")
    print("-"*60)
    print(f"Total Critical Failures: {stats['critical_failures']}")
    print(f"  • Critical Evictions: {stats['critical_evictions']}")
    print(f"  • Critical Overwrites: {stats['critical_overwrites']}")
    
    if memory_failures > 0:
        critical_rate = (stats['critical_failures'] / memory_failures) * 100
        print(f"\nCritical Failure Rate: {critical_rate:.1f}%")
        print(f"  ({stats['critical_failures']}/{memory_failures} memory failures were critical)")
    
    print("="*60)


if __name__ == "__main__":
    main()
