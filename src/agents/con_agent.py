"""Con Agent -- generates arguments opposing the proposition."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class ConAgent(BaseAgent):
    """Agent that argues against the debate topic."""

    @property
    def name(self) -> str:
        return "CON"

    @property
    def output_field(self) -> str:
        return "con_output"

    def build_prompt(self, state: DebateState) -> str:
        pro_conclusion = state.get("pro_output", {}).get("conclusion", "N/A")
        user_context = state.get("user_context", "")
        context_section = f"=== BACKGROUND CONTEXT (from the user) ===\n{user_context}\n\n" if user_context else ""

        return (
            "You are a skilled debater arguing AGAINST the proposition.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON (I argue, I believe, I contend).\n"
            "- Respond in the SAME LANGUAGE as the topic.\n"
            "- Stay strictly on topic. No filler, no generic statements.\n"
            "- You MUST directly address PRO's specific argument below.\n"
            "- Point out flaws, weak evidence, or logical fallacies in PRO's case.\n"
            "- Every counter-claim must have a concrete reason or evidence.\n"
            "- If additional context is provided, use it to strengthen your rebuttal.\n"
            "- Be concise, sharp, and persuasive.\n\n"
            f"{context_section}"
            f"Debate Topic: {state['topic']}\n"
            f"Round: {state['round_number']} / {state['max_rounds']}\n\n"
            f"PRO's argument that you MUST directly counter:\n"
            f'"{pro_conclusion}"\n\n'
            "=== TASK ===\n"
            "Dismantle PRO's argument and build your opposing case.\n\n"
            "[REASONING]\n"
            "<Your step-by-step rebuttal (5-8 lines). Each point must directly "
            "attack PRO's claims or present counter-evidence.>\n\n"
            "[CONCLUSION]\n"
            "<Your final counter-argument in 2-3 sharp sentences. First person. "
            "Directly refute PRO's core claim.>\n"
        )
