"""
LangGraph debate pipeline construction.

Builds the state graph that orchestrates Pro -> Con -> Neutral -> Judge
with conditional looping until the judge terminates the debate.
"""

from langgraph.graph import END, StateGraph

from agents.con_agent import ConAgent
from agents.judge_agent import JudgeAgent
from agents.neutral_agent import NeutralAgent
from agents.pro_agent import ProAgent
from agents.summary_agent import SummaryAgent
from config.settings import AppSettings
from models.state import DebateState

NODE_PRO = "pro"
NODE_CON = "con"
NODE_NEUTRAL = "neutral"
NODE_JUDGE = "judge"
NODE_SUMMARY = "summary"

def _route_after_judge(state: DebateState) -> str:
    """Determine whether to loop back to PRO or route to SUMMARY."""
    return NODE_PRO if state["should_continue"] else NODE_SUMMARY


def build_debate_graph(settings: AppSettings) -> StateGraph:
    """Construct and compile the debate state graph.

    Args:
        settings: Application configuration for agent initialization.

    Returns:
        Compiled LangGraph runnable.
    """
    llm = settings.llm

    pro = ProAgent(llm)
    con = ConAgent(llm)
    neutral = NeutralAgent(llm)
    judge = JudgeAgent(llm, max_tokens=llm.judge_max_tokens)
    summary = SummaryAgent(llm, max_tokens=llm.judge_max_tokens)

    graph = StateGraph(DebateState)

    graph.add_node(NODE_PRO, pro)
    graph.add_node(NODE_CON, con)
    graph.add_node(NODE_NEUTRAL, neutral)
    graph.add_node(NODE_JUDGE, judge)
    graph.add_node(NODE_SUMMARY, summary)

    graph.add_edge(NODE_PRO, NODE_CON)
    graph.add_edge(NODE_CON, NODE_NEUTRAL)
    graph.add_edge(NODE_NEUTRAL, NODE_JUDGE)

    graph.add_conditional_edges(
        NODE_JUDGE,
        _route_after_judge,
        {NODE_PRO: NODE_PRO, NODE_SUMMARY: NODE_SUMMARY},
    )

    graph.add_edge(NODE_SUMMARY, END)

    graph.set_entry_point(NODE_PRO)

    return graph.compile()
