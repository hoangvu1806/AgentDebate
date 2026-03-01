"""Topic Extractor -- parses raw user input and extracts a crisp debate topic."""

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import LLMSettings
from core.llm_factory import create_llm


class TopicExtractor:
    """
    Single-call LLM that converts free-form user input (potentially long,
    with background context) into a sharp, well-formed debate topic question.

    Runs outside the LangGraph debate graph, before the graph is initialized.
    """

    def __init__(self, llm_settings: LLMSettings) -> None:
        self._llm_settings = llm_settings

    def _build_llm(self) -> ChatGoogleGenerativeAI:
        return create_llm(self._llm_settings, streaming=False, max_tokens=512)

    def extract(self, raw_input: str) -> str:
        """
        Extract and return a clear debate topic from raw user input.

        Args:
            raw_input: The full user message, which may contain context,
                       background, opinions, questions, or all of the above.

        Returns:
            A concise, well-formed debate topic question.
        """
        llm = self._build_llm()
        prompt = self._build_prompt(raw_input)
        response = llm.invoke(prompt)
        return response.content.strip()

    async def aextract(self, raw_input: str) -> str:
        """Async version of extract()."""
        llm = self._build_llm()
        prompt = self._build_prompt(raw_input)
        response = await llm.ainvoke(prompt)
        return response.content.strip()

    def _build_prompt(self, raw_input: str) -> str:
        return (
            "You are a debate topic specialist. Convert the user's input into a "
            "single declarative proposition — a clear statement that one side can "
            "defend (PRO) and the other can oppose (CON).\n\n"
            "RULES:\n"
            "- Output ONLY the proposition. No explanation, no preamble, no quotes.\n"
            "- Must be a declarative statement, NEVER a question.\n"
            "- Must be debatable with two clear opposing positions.\n"
            "- NEVER use greetings, pleasantries, or address the user (e.g., no 'Hello', 'Chào', 'Thưa quý vị', 'Ladies and gentlemen').\n"
            "- Keep it concise: one sentence, under 15 words.\n"
            "- Use the SAME LANGUAGE as the user's input.\n"
            "- If the input is already a clear proposition, return it as-is.\n\n"
            "EXAMPLES:\n"
            "Input: 'Is AI good or bad?' -> 'AI brings more benefit than harm to society?'\n"
            "Input: 'remote work vs office' -> 'Remote work is superior to traditional office work?'\n"
            "Input: 'Should we ban TikTok?' -> 'TikTok should be banned?'\n\n"
            f"User input:\n{raw_input}\n\n"
            "Proposition:"
        )
