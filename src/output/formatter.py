"""
Console output formatting for debate results.
Separates display concerns from business logic.
"""

from models.state import AgentOutput, DebateState


_SEPARATOR = "=" * 72


def print_header(topic: str, max_rounds: int, streaming: bool) -> None:
    """Print debate session header."""
    print(f"\n{_SEPARATOR}")
    print(f"  DEBATE TOPIC: {topic}")
    print(f"  Max Rounds: {max_rounds} | Streaming: {streaming}")
    print(_SEPARATOR)


def print_agent_header(agent_name: str, round_number: int) -> None:
    """Print header before an agent starts generating."""
    print(f"\n[{agent_name}] Round {round_number}")
    print("-" * 40)


def print_round_result(state: DebateState) -> None:
    """Print a summary of the current round from state."""
    round_num = state.get("round_number", 0) - 1
    print(f"\n{_SEPARATOR}")
    print(f"  ROUND {round_num} COMPLETE")
    print(_SEPARATOR)

    _print_agent_section("PRO", state.get("pro_output"))
    _print_agent_section("CON", state.get("con_output"))
    _print_agent_section("NEUTRAL", state.get("neutral_output"))
    _print_agent_section("JUDGE", state.get("judge_output"))


def print_history(state: DebateState) -> None:
    """Print the full debate history accumulated across all rounds."""
    print(f"\n{_SEPARATOR}")
    print("  FULL DEBATE HISTORY")
    print(_SEPARATOR)
    for entry in state.get("history", []):
        print(entry)


def print_reasoning_summary(state: DebateState) -> None:
    """Print a condensed view of each agent's reasoning chain."""
    print(f"\n{_SEPARATOR}")
    print("  REASONING CHAINS SUMMARY")
    print(_SEPARATOR)

    labels = [
        ("PRO", "pro_output"),
        ("CON", "con_output"),
        ("NEUTRAL", "neutral_output"),
        ("JUDGE", "judge_output"),
    ]

    for label, field in labels:
        output = state.get(field)
        if output and output.get("reasoning"):
            preview = output["reasoning"][:500]
            print(f"\n  [{label} REASONING]\n{preview}\n")


def print_footer() -> None:
    """Print session end marker."""
    print(f"\n{_SEPARATOR}")
    print("  DEBATE COMPLETED")
    print(_SEPARATOR)


def _print_agent_section(label: str, output: AgentOutput | None) -> None:
    if not output:
        return
    print(f"\n  [{label}]")
    print(f"  Conclusion: {output.get('conclusion', 'N/A')}")
