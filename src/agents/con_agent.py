"""Con Agent -- generates arguments opposing the proposition."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class ConAgent(BaseAgent):
    """Agent that argues against the debate proposition."""

    @property
    def name(self) -> str:
        return "CON"

    @property
    def output_field(self) -> str:
        return "con_output"

    def build_prompt(self, state: DebateState) -> str:
        pro_conclusion = state.get("pro_output", {}).get("conclusion", "N/A")

        context_section = ""
        if state["round_number"] == 1:
            user_context = state.get("user_context", "")
            if user_context:
                context_section = (
                    f"=== BACKGROUND CONTEXT ===\n{user_context}\n\n"
                )

        neutral_section = ""
        if state["round_number"] > 1:
            neutral_prev = state.get("neutral_output", {}).get("conclusion", "")
            if neutral_prev:
                neutral_section = (
                    f"NEUTRAL's observation to incorporate:\n"
                    f'"{neutral_prev}"\n\n'
                )

        return (
            "You are a world-class debater opposing the following proposition. "
            "Your goal is to dismantle PRO's case and build the strongest "
            "possible argument AGAINST it.\n\n"
            "STRATEGY:\n"
            "- Identify the weakest assumption in PRO's argument and attack it.\n"
            "- Use concrete counter-examples, data, or precedents.\n"
            "- Expose logical fallacies: false dichotomy, slippery slope, "
            "cherry-picked evidence, appeal to authority.\n"
            "- Leverage NEUTRAL's observations if they weaken PRO's position.\n"
            "- Present real-world consequences that PRO ignores.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON.\n"
            "- Respond in the SAME LANGUAGE as the proposition.\n"
            "- No filler, no hedging, no generic statements.\n"
            "- Every counter-claim needs concrete backing.\n\n"
            f"{context_section}"
            f"Proposition: {state['topic']}\n"
            f"Round: {state['round_number']} / {state['max_rounds']}\n\n"
            f"PRO's argument you MUST directly counter:\n"
            f'"{pro_conclusion}"\n\n'
            f"{neutral_section}"
            "=== TASK ===\n"
            "Dismantle PRO's argument and build your opposing case.\n\n"
            "[REASONING]\n"
            "<4-6 lines of step-by-step rebuttal. Each point must directly "
            "attack PRO's claims or present counter-evidence.>\n\n"
            "[CONCLUSION]\n"
            "<2-3 sharp sentences. First person. Directly refute PRO's core claim.>\n"
        )
