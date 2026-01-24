from analysis.diagnose import diagnose_failure


class RecallTask:

    def __init__(
        self,
        key: str,
        expected_value: str,
        write_step: int,
    ):
        self.key = key
        self.expected_value = expected_value
        self.write_step = write_step


    def evaluate(self, event_log):
        # Find the first READ of this key
        recall_event = None

        for event in event_log:
            if (
                event.event_type.value == "read"
                and event.key == self.key
            ):
                recall_event = event
                break

        # No recall attempt at all
        if recall_event is None:
            diagnosis = diagnose_failure(
                event_log=event_log,
                key=self.key,
                recall_step=None,
            )
            return False, diagnosis

        # Recall attempt found — judge correctness
        if recall_event.value == self.expected_value:
            return True, {
                "result": "passed",
                "reason": "Recall succeeded on first read",
                "recall_step": recall_event.step,
            }

        # Recall happened but failed → diagnose
        diagnosis = diagnose_failure(
            event_log=event_log,
            key=self.key,
            recall_step=recall_event.step,
        )
        return False, diagnosis

