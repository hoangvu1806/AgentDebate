"""
Debate runner -- orchestrates graph execution and output display.
This module is the high-level API for running a debate session.
"""

import asyncio

from config.settings import AppSettings
from graph.debate_graph import build_debate_graph
from models.state import AgentOutput, DebateState
from output.formatter import (
    print_footer,
    print_header,
    print_history,
    print_reasoning_summary,
)


def _build_initial_state(
    topic: str,
    settings: AppSettings,
) -> DebateState:
    empty_output = AgentOutput(reasoning="", conclusion="")
    return DebateState(
        topic=topic,
        round_number=1,
        max_rounds=settings.debate.max_rounds,
        enable_streaming=settings.debate.enable_streaming,
        pro_output=empty_output,
        con_output=empty_output,
        neutral_output=empty_output,
        judge_output=empty_output,
        history=[],
        should_continue=True,
    )


def run_debate(topic: str, settings: AppSettings) -> DebateState:
    """Execute a full debate session synchronously.

    Args:
        topic: The proposition to debate.
        settings: Application configuration.

    Returns:
        Final debate state after all rounds complete.
    """
    print_header(topic, settings.debate.max_rounds, settings.debate.enable_streaming)

    graph = build_debate_graph(settings)
    initial_state = _build_initial_state(topic, settings)
    result = graph.invoke(initial_state)

    print_history(result)
    print_reasoning_summary(result)
    print_footer()

    return result


async def arun_debate(topic: str, settings: AppSettings) -> DebateState:
    """Execute a full debate session asynchronously.

    Args:
        topic: The proposition to debate.
        settings: Application configuration.

    Returns:
        Final debate state after all rounds complete.
    """
    print_header(topic, settings.debate.max_rounds, settings.debate.enable_streaming)

    graph = build_debate_graph(settings)
    initial_state = _build_initial_state(topic, settings)
    result = await graph.ainvoke(initial_state)

    print_history(result)
    print_reasoning_summary(result)
    print_footer()

    return result
