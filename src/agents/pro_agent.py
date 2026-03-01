"""Pro Agent -- generates arguments supporting the proposition."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class ProAgent(BaseAgent):
    """Agent that argues in favor of the debate proposition."""

    @property
    def name(self) -> str:
        return "PRO"

    @property
    def output_field(self) -> str:
        return "pro_output"

    def build_prompt(self, state: DebateState) -> str:
        is_first_round = state["round_number"] == 1

        context_section = ""
        if is_first_round:
            user_context = state.get("user_context", "")
            if user_context:
                context_section = (
                    f"=== BACKGROUND CONTEXT ===\n{user_context}\n\n"
                )

        rebuttal_section = ""
        if not is_first_round:
            con_prev = state.get("con_output", {}).get("conclusion", "")
            neutral_prev = state.get("neutral_output", {}).get("conclusion", "")
            if con_prev:
                rebuttal_section += (
                    f"CON's argument you MUST directly counter:\n"
                    f'"{con_prev}"\n\n'
                )
            if neutral_prev:
                rebuttal_section += (
                    f"NEUTRAL's observation to incorporate:\n"
                    f'"{neutral_prev}"\n\n'
                )

        return (
            "You are a world-class debater defending the following proposition. "
            "Your goal is to build the strongest possible case FOR it.\n\n"
            "STRATEGY:\n"
            "- Lead with your strongest evidence or data point.\n"
            "- Use concrete examples, statistics, or historical precedents.\n"
            "- Anticipate and preempt obvious counterarguments.\n"
            "- If rebutting CON, attack the weakest link in their chain of logic.\n"
            "- Leverage NEUTRAL's observations if they support your position.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON.\n"
            "- Respond in the SAME LANGUAGE as the proposition.\n"
            "- NEVER use greetings, pleasantries, or address the audience (e.g., no 'Hello', 'Chào', 'Thưa quý vị', 'Ladies and gentlemen').\n"
            "- No filler, no hedging, no generic statements.\n"
            "- Every claim needs concrete backing.\n\n"
            f"{context_section}"
            f"Proposition: {state['topic']}\n"
            f"Round: {state['round_number']} / {state['max_rounds']}\n\n"
            f"{rebuttal_section}"
            "=== TASK ===\n"
            "Build a focused supporting argument.\n\n"
            "[REASONING]\n"
            "<4-6 lines of step-by-step reasoning. Each point must directly "
            "support the proposition with evidence or logic.>\n\n"
            "[CONCLUSION]\n"
            "<2-3 sharp sentences. First person. No hedging.>\n"
        )
