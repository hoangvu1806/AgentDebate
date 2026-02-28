"""Summary Agent -- hypothesizes and synthesizes the debate."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class SummaryAgent(BaseAgent):
    """Agent that summarizes the debate and declares the final answer."""

    @property
    def name(self) -> str:
        return "SUMMARY"

    @property
    def output_field(self) -> str:
        return "summary_output"

    def _extract_history_text(self, state: DebateState) -> str:
        """Safely extract history as plain text regardless of message type."""
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
                f"=== FULL DEBATE RECORD ===\n{history_text}\n\n"
            )

        return (
            "You are the master summarizer of this debate.\n"
            "The debate has concluded. Your job is to synthesize everything.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON (I summarize, I conclude).\n"
            "- Respond in the SAME LANGUAGE as the topic.\n"
            "- Be objective, practical, and highly clear.\n\n"
            f"Topic: {state['topic']}\n\n"
            f"{history_section}"
            "=== TASK ===\n"
            "Provide a final, master summary of the debate.\n\n"
            "[REASONING]\n"
            "<Your step-by-step synthesis (10-15 lines). Briefly walk through the "
            "evolution of the debate. Highlight the strongest arguments from PRO and CON. "
            "Identify the defining points that settled the debate.>\n\n"
            "[CONCLUSION]\n"
            "<Your final summary (3-5 sentences). Clearly declare the winning perspective "
            "and provide the best, most practical answer to the topic question.>\n"
        )
