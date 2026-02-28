"""Summary Agent -- synthesizes the debate into a final answer."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class SummaryAgent(BaseAgent):
    """Agent that synthesizes all rounds into a definitive answer."""

    @property
    def name(self) -> str:
        return "SUMMARY"

    @property
    def output_field(self) -> str:
        return "summary_output"

    def _extract_history_text(self, state: DebateState) -> str:
        items = state.get("history", [])
        parts = []
        for item in items:
            if isinstance(item, str):
                parts.append(item)
            elif hasattr(item, "content"):
                parts.append(item.content)
        return "\n".join(parts)

    def build_prompt(self, state: DebateState) -> str:
        history_text = self._extract_history_text(state)
        history_section = ""
        if history_text:
            history_section = (
                f"=== DEBATE RECORD ===\n{history_text}\n\n"
            )

        return (
            "You are the master synthesizer. The debate has concluded. "
            "Your job is to distill ALL rounds into one authoritative answer.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON.\n"
            "- Respond in the SAME LANGUAGE as the proposition.\n"
            "- Be objective, practical, and definitive.\n"
            "- Credit the strongest arguments from each side.\n\n"
            f"Proposition: {state['topic']}\n\n"
            f"{history_section}"
            "=== TASK ===\n"
            "Deliver the final synthesis.\n\n"
            "[REASONING]\n"
            "<8-12 lines: Walk through the debate arc. Highlight the "
            "strongest arguments from PRO, CON, and NEUTRAL. Identify "
            "the defining moments that settled the outcome.>\n\n"
            "[CONCLUSION]\n"
            "<3-5 sentences: Declare the winning perspective and provide "
            "the best practical answer to the proposition.>\n"
        )
