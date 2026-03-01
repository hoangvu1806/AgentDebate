"""Neutral Agent -- provides an independent third perspective."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class NeutralAgent(BaseAgent):
    """Agent that offers overlooked facts, nuances, and trade-offs."""

    @property
    def name(self) -> str:
        return "NEUTRAL"

    @property
    def output_field(self) -> str:
        return "neutral_output"

    def build_prompt(self, state: DebateState) -> str:
        pro_conclusion = state.get("pro_output", {}).get("conclusion", "N/A")
        con_conclusion = state.get("con_output", {}).get("conclusion", "N/A")

        context_section = ""
        if state["round_number"] == 1:
            user_context = state.get("user_context", "")
            if user_context:
                context_section = (
                    f"=== BACKGROUND CONTEXT ===\n{user_context}\n\n"
                )

        return (
            "You are an independent analyst in a structured debate. You do NOT "
            "judge who is winning. Instead, you provide a THIRD PERSPECTIVE that "
            "neither PRO nor CON has considered.\n\n"
            "YOUR ROLE:\n"
            "- Surface overlooked evidence, data, or real-world examples.\n"
            "- Identify hidden assumptions in BOTH sides.\n"
            "- Propose nuances, edge cases, or conditions under which "
            "each side's argument breaks down.\n"
            "- Offer a balanced, fact-driven viewpoint that enriches the debate.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON (I note, I observe, I suggest).\n"
            "- Respond in the SAME LANGUAGE as the topic.\n"
            "- NEVER use greetings, pleasantries, or address the audience (e.g., no 'Hello', 'Chào', 'Thưa quý vị', 'Ladies and gentlemen').\n"
            "- Do NOT declare a winner or say which side is stronger.\n"
            "- Do NOT repeat arguments already made by PRO or CON.\n"
            "- Every claim must cite concrete evidence or reasoning.\n"
            "- Be precise. No filler.\n\n"
            f"{context_section}"
            f"Proposition: {state['topic']}\n"
            f"Round: {state['round_number']} / {state['max_rounds']}\n\n"
            f"PRO's position:\n\"{pro_conclusion}\"\n\n"
            f"CON's position:\n\"{con_conclusion}\"\n\n"
            "=== TASK ===\n"
            "Provide your independent analysis.\n\n"
            "[REASONING]\n"
            "<Identify 3-4 overlooked factors, hidden assumptions, or "
            "real-world complications that neither side addressed.>\n\n"
            "[CONCLUSION]\n"
            "<Synthesize your findings into 2-3 sentences. State the key "
            "nuance or trade-off that the debate is missing.>\n"
        )
