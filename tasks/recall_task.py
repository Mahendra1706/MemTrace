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


def auto_evaluate_all(event_log):
    """
    Automatically evaluate all READ events in the event log.
    
    For each READ event:
    1. Find the original WRITE event for that key
    2. Create a RecallTask with the original value
    3. Evaluate using existing logic
    
    Returns:
        List of results for each READ event
    """
    results = []
    
    # Find all READ events
    read_events = [e for e in event_log if e.event_type.value == "read"]
    
    if not read_events:
        return []
    
    for read_event in read_events:
        key = read_event.key
        
        # Find the FIRST WRITE event for this key
        original_write = None
        for event in event_log:
            if (event.event_type.value == "write" and event.key == key):
                original_write = event
                break
        
        # If no write found, diagnose as never_written
        if original_write is None:
            diagnosis = diagnose_failure(
                event_log=event_log,
                key=key,
                recall_step=read_event.step,
            )
            results.append({
                "key": key,
                "read_step": read_event.step,
                "read_value": read_event.value,
                "expected_value": None,
                "passed": False,
                "failure_type": diagnosis["failure_type"],
                "evidence": diagnosis["evidence"]
            })
            continue
        
        # Create RecallTask with original write value
        task = RecallTask(
            key=key,
            expected_value=original_write.value,
            write_step=original_write.step
        )
        
        # Evaluate
        passed, info = task.evaluate(event_log)
        
        results.append({
            "key": key,
            "read_step": read_event.step,
            "read_value": read_event.value,
            "expected_value": original_write.value,
            "passed": passed,
            "failure_type": info.get("failure_type", "N/A"),
            "is_critical": info.get("is_critical", False), 
            "importance": info.get("importance", 0.0),      
            "evidence": info.get("evidence", []),
            "info": info
        })
    
    return results
