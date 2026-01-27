# scenario.py

class Scenario:
    def __init__(self, name, actions):
        self.name = name
        self.actions = actions


# Scenario 1: Overwriting - same key written multiple times (triggers UPDATE)
overwrite_scenario = Scenario(
    name="Overwrite Single Key",
    actions=[
        {"action": "write", "key": "k1", "value": "v1"},
        {"action": "write", "key": "k1", "value": "v2"},
        {"action": "write", "key": "k1", "value": "v3"},
        {"action": "read",  "key": "k1"},
    ]
)

# Scenario 2: Eviction - different keys with limited capacity (triggers EVICT)
eviction_scenario = Scenario(
    name="Eviction Due to Capacity",
    actions=[
        {"action": "write", "key": "k1", "value": "v1"},
        {"action": "write", "key": "k2", "value": "v2"},
        {"action": "write", "key": "k3", "value": "v3"},
        {"action": "read",  "key": "k1"},  # k1 should be evicted if capacity < 3
    ]
)

# Scenario 3: Successful Recall - control case (should PASS)
successful_recall_scenario = Scenario(
    name="Successful Recall (Control)",
    actions=[
        {"action": "write", "key": "k1", "value": "v1"},
        {"action": "write", "key": "k2", "value": "v2"},
        {"action": "read",  "key": "k1"},  # Should succeed
        {"action": "read",  "key": "k2"},  # Should succeed
    ]
)

# Scenario 4: Mixed Operations - multiple reads with different outcomes
mixed_operations_scenario = Scenario(
    name="Mixed Operations",
    actions=[
        {"action": "write", "key": "k1", "value": "v1"},
        {"action": "write", "key": "k2", "value": "v2"},
        {"action": "read",  "key": "k1"},  # Should succeed
        {"action": "write", "key": "k1", "value": "v1_updated"},  # Update k1
        {"action": "read",  "key": "k1"},  # Should fail (value changed)
        {"action": "write", "key": "k3", "value": "v3"},
        {"action": "read",  "key": "k2"},  # Might fail if evicted
    ]
)

# Scenario 5: LLM Hallucination - memory works but we expect wrong value
llm_error_scenario = Scenario(
    name="LLM Hallucination (Simulated)",
    actions=[
        {"action": "write", "key": "user_name", "value": "Alice"},
        {"action": "write", "key": "user_age", "value": "25"},
        {"action": "read",  "key": "user_name"},  

    ]
)
