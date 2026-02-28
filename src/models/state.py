"""
Debate state definition used by the LangGraph orchestrator.
"""

import operator
from typing import Annotated, TypedDict


class AgentOutput(TypedDict):
    """Structured output from a single agent invocation."""

    reasoning: str
    conclusion: str


class DebateState(TypedDict):
    """
    Shared mutable state passed through the LangGraph debate pipeline.

    Each agent reads from and writes to specific fields.
    The `history` field accumulates across rounds via the `add_messages` reducer.
    """

    topic: str
    user_context: str       # Full original user input including any context provided
    round_number: int
    max_rounds: int
    enable_streaming: bool

    pro_output: AgentOutput
    con_output: AgentOutput
    neutral_output: AgentOutput
    judge_output: AgentOutput
    summary_output: AgentOutput

    history: Annotated[list[str], operator.add]
    should_continue: bool
