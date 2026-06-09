import os
from agent.LLMAgent import LLMAgent
from tasks.recall_task import auto_evaluate_all


# helpers

def _sep(title=""):
    print("\n" + "=" * 50)
    if title:
        print(title)
        print("=" * 50)


def _print_diagnosis(event_log):
    _sep("DIAGNOSIS")
    results = auto_evaluate_all(event_log)

    if not results:
        print("  (no recall events to evaluate)")
        return

    passed = sum(1 for r in results if r["passed"])
    failed  = len(results) - passed

    for r in results:
        if r["passed"]:
            print(f"  ✅  step={r['read_step']}  {r['key']} = '{r['read_value']}'")
        else:
            print(f"  ❌  step={r['read_step']}  {r['key']} — {r['failure_type']}")
            for ev in r.get("evidence", []):
                print(f"       {ev}")
            hint = r.get("info", {}).get("semantic_hint")
            if hint:
                print(f" similar key: '{hint['key']}' (score {hint['score']})")

    print(f"\n   {passed} passed / {failed} failed / {len(results)} total reads")


# Library class

class MemTrace:
    """
    Parameters
    ----------
    api_key      : str   — Groq API key
    model        : str   — Groq model name (default: llama-3.3-70b-versatile)
    stm_capacity : int   — STM size before eviction starts (default: 10)
    """

    def __init__(
        self,
        api_key: str,
        model: str = "llama-3.3-70b-versatile",
        stm_capacity: int = 70,
    ):
        self.event_log = []
        self._agent = LLMAgent(
            stm_capacity=stm_capacity,
            event_log=self.event_log,
            api_key=api_key,
            model=model,
        )
        self._logged_up_to = 0

    def _send(self, message: str) -> str:
        return self._agent.process(message)

    def run(self, conversations: list):
        """Batch mode — run all messages, print event log + diagnosis at end."""
        if not conversations:
            print(" No messages provided.")
            return

        cap = self._agent.stm.capacity
        print(f"\n Running {len(conversations)} message(s)  [stm_capacity={cap}]")

        for msg in conversations:
            try:
                self._send(msg)
            except Exception as e:
                print(f"  ❌ '{msg[:50]}' → {e}")

        _sep("EVENT LOG")
        for e in self.event_log:
            print(f"  {e}")

        _print_diagnosis(self.event_log)
        _sep("DONE")

    def chat(self):
        """Live mode — type in terminal, events logged after each message."""
        cap = self._agent.stm.capacity
        _sep("MemTrace — Live Chat")
        print(f"  model: {self._agent.model}   stm_capacity: {cap}")
        print("  Type your messages. Enter 'exit' to stop and see diagnosis.")
        print("=" * 60)

        try:
            while True:
                try:
                    user_input = input("\nYou: ").strip()
                except EOFError:
                    break

                if user_input.lower() in ("exit", "quit", ""):
                    break

                try:
                    response = self._send(user_input)
                    print(f"Agent: {response}")
                except Exception as e:
                    print(f"❌ Error: {e}")
                    continue

                # Print only NEW events since last message
                new = self.event_log[self._logged_up_to:]
                if new:
                    print()
                    for e in new:
                        print(f"  {e}")
                self._logged_up_to = len(self.event_log)

        except KeyboardInterrupt:
            print("\n(interrupted)")

        _print_diagnosis(self.event_log)
        _sep("DONE")


# Interactive CLI

def _cli():
    print("\n" + "=" * 60)
    print("  MemTrace — Interactive Setup")
    print("=" * 60)
    print("  Supported model provider: Groq")

    # API key
    api_key = os.environ.get("GROQ_API_KEY") or input("  Groq API key: ").strip()
    if not api_key:
        print("❌  API key required.")
        return

    # Model
    default_model = "llama-3.3-70b-versatile"
    model_input = input(f"  Model [{default_model}]: ").strip()
    model = model_input if model_input else default_model

    # STM capacity
    cap_input = input("  STM capacity [10]: ").strip()
    try:
        stm_capacity = int(cap_input) if cap_input else 10
    except ValueError:
        print("❌  STM capacity must be a number.")
        return

    # Mode
    print("\n  Modes:")
    print("    batch — you enter messages now, run all at once")
    print("    chat  — live terminal chat, events logged in real-time")
    mode = input("\n  Mode [chat]: ").strip().lower() or "chat"

    mt = MemTrace(api_key=api_key, model=model, stm_capacity=stm_capacity)

    if mode == "batch":
        print("\n  Enter your messages (blank line to finish):")
        messages = []
        while True:
            try:
                line = input("  > ").strip()
            except EOFError:
                break
            if not line:
                break
            messages.append(line)

        if not messages:
            print("⚠️  No messages entered.")
            return

        mt.run(messages)

    elif mode == "chat":
        mt.chat()

    else:
        print(f"❌  Unknown mode '{mode}'. Use 'batch' or 'chat'.")


if __name__ == "__main__":
    _cli()
