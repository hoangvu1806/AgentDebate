"""Judge Agent -- evaluates all arguments and renders a verdict."""

from agents.base_agent import BaseAgent
from models.state import DebateState


class JudgeAgent(BaseAgent):
    """Agent that evaluates debate quality and decides whether to continue."""

    CONTINUE_MARKER = "SHOULD_CONTINUE: YES"

    @property
    def name(self) -> str:
        return "JUDGE"

    @property
    def output_field(self) -> str:
        return "judge_output"

    def build_prompt(self, state: DebateState) -> str:
        pro_conclusion = state.get("pro_output", {}).get("conclusion", "N/A")
        con_conclusion = state.get("con_output", {}).get("conclusion", "N/A")
        neutral_conclusion = state.get("neutral_output", {}).get("conclusion", "N/A")
        user_context = state.get("user_context", "")
        context_section = f"=== BACKGROUND CONTEXT (from the user) ===\n{user_context}\n\n" if user_context else ""

        is_final_round = state["round_number"] >= state["max_rounds"]

        context = (
            f"{context_section}"
            f"Debate Topic: {state['topic']}\n"
            f"Round: {state['round_number']} / {state['max_rounds']}\n\n"
            f"PRO argues:\n\"{pro_conclusion}\"\n\n"
            f"CON argues:\n\"{con_conclusion}\"\n\n"
            f"NEUTRAL observes:\n\"{neutral_conclusion}\"\n\n"
        )

        if is_final_round:
            return self._build_final_prompt(context, state)
        return self._build_intermediate_prompt(context)

    def _build_intermediate_prompt(self, context: str) -> str:
        return (
            "You are the presiding judge of this debate.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON (I find, I rule, I determine).\n"
            "- Respond in the SAME LANGUAGE as the topic.\n"
            "- Judge ONLY the specific arguments presented, not the topic in general.\n"
            "- Evaluate evidence quality, logical rigor, and persuasiveness.\n"
            "- Be decisive, not wishy-washy.\n\n"
            f"{context}"
            "=== TASK ===\n"
            "Evaluate this round and decide if more debate is needed.\n\n"
            "[REASONING]\n"
            "<Your judicial analysis (8-12 lines). Score each side on: "
            "evidence strength, logical consistency, and persuasiveness.>\n\n"
            "[CONCLUSION]\n"
            "ROUND LEADER: [PRO / CON]\n"
            "REASON: [2 sentences on who argued better this round and why]\n"
            "SHOULD_CONTINUE: [YES / NO]\n"
        )

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

    def _build_final_prompt(self, context: str, state: DebateState) -> str:
        history_text = self._extract_history_text(state)
        history_section = ""
        if history_text:
            history_section = (
                f"=== FULL DEBATE RECORD ===\n{history_text}\n\n"
            )

        return (
            "You are the supreme judge. This is the FINAL ROUND.\n"
            "You MUST deliver an ABSOLUTE, BINDING verdict. No ties. No ambiguity.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON (I declare, I rule, I conclude).\n"
            "- Respond in the SAME LANGUAGE as the topic.\n"
            "- You MUST pick ONE winner: PRO or CON. 'Balanced' is NOT allowed.\n"
            "- Your verdict must be based on argument quality, NOT personal opinion.\n"
            "- The FINAL ANSWER must directly and objectively answer the topic question.\n\n"
            f"{context}"
            f"{history_section}"
            "=== TASK ===\n"
            "Deliver your final, irrevocable verdict.\n\n"
            "[REASONING]\n"
            "<Your comprehensive judicial review (12-18 lines).\n"
            "1. Summarize each side's strongest argument across all rounds.\n"
            "2. Identify the decisive factor that tips the scale.\n"
            "3. Acknowledge the loser's best point.\n"
            "4. Explain why the winner's case was ultimately more compelling.>\n\n"
            "[CONCLUSION]\n"
            "WINNER: [PRO or CON] (mandatory, no ties)\n"
            "DECISIVE FACTOR: [The single strongest reason the winner prevailed, 1-2 sentences]\n"
            "FINAL ANSWER: [A direct, objective answer to the topic question in 3-5 sentences. "
            "This must synthesize the best arguments from both sides into a practical, "
            "well-reasoned answer that anyone can use.]\n"
            "SHOULD_CONTINUE: NO\n"
        )

    def _apply_output(self, state: DebateState, output) -> DebateState:
        """Extend base to also handle round advancement and continuation logic."""
        state[self.output_field] = output
        state["history"].append(
            self._format_history_entry(state["round_number"], output)
        )

        is_within_round_limit = state["round_number"] < state["max_rounds"]
        judge_wants_continuation = self.CONTINUE_MARKER in output["conclusion"]
        state["should_continue"] = is_within_round_limit and judge_wants_continuation
        state["round_number"] += 1

        return state
