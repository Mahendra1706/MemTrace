import random


class Scenario:
    def __init__(self, name, actions, capacity):
        self.name = name
        self.actions = actions
        self.capacity = capacity


def importance_generator():
    """Generate random importance score between 0.0 and 1.0 (increments of 0.1)"""
    possible_values = [i / 10 for i in range(11)]  
    return random.choice(possible_values)


def generate_scenario(
    scenario_id: int,
    num_steps: int,
    num_keys: int,
    read_prob: float,
    capacities,
    seed=None,
):
    """
    Generates a random memory interaction scenario.

    capacities: list like [1, 2, 4, None]
    """

    if seed is not None:
        random.seed(seed + scenario_id)

    keys = [f"k{i}" for i in range(num_keys)]
    values = [f"v{i}" for i in range(num_keys)]

    actions = []

    for _ in range(num_steps):
        if random.random() < read_prob:
            # READ action
            action = {
                "action": "read",
                "key": random.choice(keys),
                "importance": importance_generator(),  # For tracking
            }
        else:
            # WRITE action
            layer = "LTM" if random.random() < 0.2 else "STM"
            action = {
                "action": "write",
                "key": random.choice(keys),
                "value": random.choice(values),
                "layer": layer,
                "importance": importance_generator(),
            }

        actions.append(action)

    capacity = random.choice(capacities)

    return Scenario(
        name=f"scenario_{scenario_id}",
        actions=actions,
        capacity=capacity,
    )
