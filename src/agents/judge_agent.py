"""Judge Agent -- evaluates all arguments and renders a verdict."""

from agents.base_agent import BaseAgent
from models.state import AgentOutput, DebateState


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

        is_final_round = state["round_number"] >= state["max_rounds"]

        context = (
            f"Proposition: {state['topic']}\n"
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
            "You are the presiding judge of a formal debate.\n\n"
            "EVALUATION CRITERIA (score each side 1-10):\n"
            "1. Evidence Quality: Are claims backed by data, examples, or precedents?\n"
            "2. Logical Rigor: Is the reasoning internally consistent and free of fallacies?\n"
            "3. Persuasiveness: Would a neutral audience find this compelling?\n"
            "4. Rebuttal Strength: Did they effectively address the opponent's points?\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON.\n"
            "- Respond in the SAME LANGUAGE as the proposition.\n"
            "- Judge ONLY the arguments presented, not the topic itself.\n"
            "- Be decisive. No hedging.\n"
            "- Consider NEUTRAL's observations as an additional lens.\n\n"
            f"{context}"
            "=== TASK ===\n"
            "Evaluate this round.\n\n"
            "[REASONING]\n"
            "<Score each side on the 4 criteria above. Explain which "
            "arguments landed and which fell flat. 6-10 lines.>\n\n"
            "[CONCLUSION]\n"
            "ROUND LEADER: [PRO / CON]\n"
            "REASON: [2 sentences on who argued better and why]\n"
            "SHOULD_CONTINUE: [YES / NO]\n"
        )

    def _build_final_prompt(self, context: str, state: DebateState) -> str:
        history_text = self._extract_history_text(state)
        history_section = ""
        if history_text:
            history_section = (
                f"=== DEBATE RECORD (conclusions only) ===\n{history_text}\n\n"
            )

        return (
            "You are the supreme judge. This is the FINAL ROUND.\n"
            "You MUST deliver an ABSOLUTE, BINDING verdict. No ties. No ambiguity.\n\n"
            "RULES:\n"
            "- Speak in FIRST PERSON.\n"
            "- Respond in the SAME LANGUAGE as the proposition.\n"
            "- You MUST pick ONE winner: PRO or CON. 'Balanced' is NOT allowed.\n"
            "- Verdict based on argument quality, NOT personal opinion.\n"
            "- The FINAL ANSWER must directly address the proposition.\n\n"
            f"{context}"
            f"{history_section}"
            "=== TASK ===\n"
            "Deliver your final verdict.\n\n"
            "[REASONING]\n"
            "<Comprehensive review (10-15 lines):\n"
            "1. Each side's strongest argument across all rounds.\n"
            "2. The decisive factor that tips the scale.\n"
            "3. Acknowledge the loser's best point.\n"
            "4. Why the winner's case was ultimately more compelling.>\n\n"
            "[CONCLUSION]\n"
            "WINNER: [PRO or CON] (mandatory, no ties)\n"
            "DECISIVE FACTOR: [1-2 sentences]\n"
            "FINAL ANSWER: [3-5 sentences synthesizing the best arguments "
            "into a practical, well-reasoned answer.]\n"
            "SHOULD_CONTINUE: NO\n"
        )

    def _extract_history_text(self, state: DebateState) -> str:
        items = state.get("history", [])
        parts = []
        for item in items:
            if isinstance(item, str):
                parts.append(item)
            elif hasattr(item, "content"):
                parts.append(item.content)
        return "\n".join(parts)

    def _apply_output(self, state: DebateState, output: AgentOutput) -> DebateState:
        state[self.output_field] = output
        state["history"].append(
            self._format_history_entry(state["round_number"], output)
        )

        is_within_round_limit = state["round_number"] < state["max_rounds"]
        judge_wants_continuation = self.CONTINUE_MARKER in output["conclusion"]
        state["should_continue"] = is_within_round_limit and judge_wants_continuation
        state["round_number"] += 1

        return state
