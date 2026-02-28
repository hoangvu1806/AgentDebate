"""Pro Agent -- generates arguments supporting the proposition."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class ProAgent(BaseAgent):
    """Agent that argues in favor of the debate topic."""

    @property
    def name(self) -> str:
        return "PRO"

    @property
    def output_field(self) -> str:
        return "pro_output"

    def build_prompt(self, state: DebateState) -> str:
        con_prev = state.get("con_output", {}).get("conclusion", "")
        user_context = state.get("user_context", "")
        rebuttal_section = ""
        if con_prev and state["round_number"] > 1:
            rebuttal_section = (
                f"CON's previous argument you MUST directly counter:\n"
                f'"{con_prev}"\n\n'
            )
        context_section = ""
        if user_context:
            context_section = (
                f"=== BACKGROUND CONTEXT (from the user) ===\n"
                f"{user_context}\n\n"
            )

        return (
            "You are a skilled debater arguing IN FAVOR of the proposition.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON (I argue, I believe, I contend).\n"
            "- Respond in the SAME LANGUAGE as the topic.\n"
            "- Stay strictly on topic. No filler, no generic statements.\n"
            "- Every claim must have a concrete reason or evidence.\n"
            "- If additional context is provided, use it to make sharper arguments.\n"
            "- If responding to CON, directly address their specific points.\n"
            "- Be concise, sharp, and persuasive.\n\n"
            f"{context_section}"
            f"Debate Topic: {state['topic']}\n"
            f"Round: {state['round_number']} / {state['max_rounds']}\n\n"
            f"{rebuttal_section}"
            "=== TASK ===\n"
            "Build a focused supporting argument.\n\n"
            "[REASONING]\n"
            "<Your step-by-step reasoning (5-8 lines). Each point must directly "
            "support the proposition with evidence or logic.>\n\n"
            "[CONCLUSION]\n"
            "<Your final argument in 2-3 sharp sentences. First person. "
            "No hedging, no vague language.>\n"
        )
