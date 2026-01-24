from core.events import MemoryLayer
from core.memory import MemoryStore
from agent.toy_agent import ToyAgent
from tasks.recall_task import RecallTask


def main():
    # 1) Ground-truth event log
    event_log = []

    # 2) STM with larger capacity (no eviction, only overwriting)
    stm = MemoryStore(
        memory_layer=MemoryLayer.STM,
        event_log=event_log,
        capacity=10,  # Large enough to avoid eviction
    )

    # 3) Agent
    agent = ToyAgent(memory=stm)

    # 4) Overwriting scenario - same key updated multiple times
    print("USER: My deadline is Friday")
    print("AGENT:", agent.run_turn("My deadline is Friday"))

    print("\nUSER: Actually, my deadline is Monday")
    print("AGENT:", agent.run_turn("Actually, my deadline is Monday"))

    print("\nUSER: Wait, my deadline is Wednesday")
    print("AGENT:", agent.run_turn("Wait, my deadline is Wednesday"))

    print("\nUSER: What is my deadline?")
    print("AGENT:", agent.run_turn("What is my deadline?"))

    # 5) Evaluation task - expects the FIRST value (Friday)
    # This will fail because the value was overwritten
    task = RecallTask(
        key="deadline",
        expected_value="Friday",
        write_step=2,     # when deadline was first written
    )

    passed, info = task.evaluate(event_log)

    # 6) Output
    print("\n=== MEMTRACE EVENTS ===") 
    for e in event_log:
        print(e)

    print("\n=== TASK RESULT ===")
    print("STATUS:", "PASSED" if passed else "FAILED")

    if not passed:
        print("Failure Type:", info["failure_type"])
        print("Evidence:")
        for line in info["evidence"]:
            print(" -", line)
            


if __name__ == "__main__":
    main()