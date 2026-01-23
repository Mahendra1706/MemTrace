# tasks/recall_task.py

class RecallTask:
    def __init__(
        self,
        key: str,
        expected_value: str,
        write_step: int,
        recall_step: int,
    ):
        self.key = key
        self.expected_value = expected_value
        self.write_step = write_step
        self.recall_step = recall_step

    def evaluate(self, event_log):
        """
        Returns:
            (passed: bool, reason: str)
        """
        for event in event_log:
            if (
                event.event_type.value == "read"
                and event.key == self.key
                and event.step == self.recall_step
            ):
                if event.value == self.expected_value:
                    return True, "Recall succeeded as expected"
                else:
                    return False, "Recall failed at expected step"

        return False, "No recall attempt found at expected step"
