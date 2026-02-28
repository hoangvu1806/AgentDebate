"""Neutral Agent -- provides objective analysis of both sides."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class NeutralAgent(BaseAgent):
    """Agent that delivers an impartial analysis of both arguments."""

    @property
    def name(self) -> str:
        return "NEUTRAL"

    @property
    def output_field(self) -> str:
        return "neutral_output"

    def build_prompt(self, state: DebateState) -> str:
        pro_conclusion = state.get("pro_output", {}).get("conclusion", "N/A")
        con_conclusion = state.get("con_output", {}).get("conclusion", "N/A")
        user_context = state.get("user_context", "")
        context_section = f"=== BACKGROUND CONTEXT (from the user) ===\n{user_context}\n\n" if user_context else ""

        return (
            "You are an impartial fact-checker and analyst.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON (I observe, I find, I note).\n"
            "- Respond in the SAME LANGUAGE as the topic.\n"
            "- Stay strictly on topic. No filler.\n"
            "- Analyze ONLY the specific arguments presented below.\n"
            "- If additional context is provided, use it to assess claims for accuracy.\n"
            "- Identify which side has stronger evidence and logic.\n"
            "- Point out any logical fallacies or unsupported claims from either side.\n"
            "- Be precise and analytical, not vague.\n\n"
            f"{context_section}"
            f"Debate Topic: {state['topic']}\n"
            f"Round: {state['round_number']} / {state['max_rounds']}\n\n"
            f"PRO argues:\n\"{pro_conclusion}\"\n\n"
            f"CON argues:\n\"{con_conclusion}\"\n\n"
            "=== TASK ===\n"
            "Analyze both arguments on their specific merits.\n\n"
            "[REASONING]\n"
            "<Your point-by-point analysis (6-10 lines). Compare the specific "
            "claims, evidence quality, and logical consistency of each side.>\n\n"
            "[CONCLUSION]\n"
            "<Your assessment in 2-3 sentences. State which side currently "
            "has the stronger case and why, based on the arguments presented.>\n"
        )
