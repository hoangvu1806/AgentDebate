"""
Parsing utilities for extracting structured reasoning and conclusions
from LLM responses that follow the [REASONING] / [CONCLUSION] format.
"""

import re

from models.state import AgentOutput

_REASONING_PATTERN = re.compile(
    r"\[REASONING\](.*?)\[CONCLUSION\]", re.DOTALL
)
_CONCLUSION_PATTERN = re.compile(
    r"\[CONCLUSION\](.*?)(?:\[|$)", re.DOTALL
)


def parse_agent_response(raw_text: str) -> AgentOutput:
    """Parse a raw LLM response into structured reasoning and conclusion.

    If the expected markers are absent, the full text is used as fallback
    for both fields to avoid data loss.
    """
    reasoning_match = _REASONING_PATTERN.search(raw_text)
    conclusion_match = _CONCLUSION_PATTERN.search(raw_text)

    reasoning = reasoning_match.group(1).strip() if reasoning_match else raw_text.strip()
    conclusion = conclusion_match.group(1).strip() if conclusion_match else raw_text.strip()

    return AgentOutput(reasoning=reasoning, conclusion=conclusion)
