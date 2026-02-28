"""
Abstract base class for all debate agents.

Provides shared logic for LLM invocation (sync and async),
streaming, and response parsing. Concrete agents only need
to define their prompt template and state field mappings.
"""

from abc import ABC, abstractmethod
from typing import AsyncIterator, Iterator

from langchain_google_genai import ChatGoogleGenerativeAI

from config.settings import LLMSettings
from core.llm_factory import create_llm
from core.response_parser import parse_agent_response
from models.state import AgentOutput, DebateState


class BaseAgent(ABC):
    """Base class for debate agents with sync and async support."""

    def __init__(self, llm_settings: LLMSettings, max_tokens: int | None = None) -> None:
        self._llm_settings = llm_settings
        self._max_tokens = max_tokens

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable agent identifier (e.g. 'PRO', 'CON')."""

    @property
    @abstractmethod
    def output_field(self) -> str:
        """Key in DebateState where this agent writes its AgentOutput."""

    @abstractmethod
    def build_prompt(self, state: DebateState) -> str:
        """Construct the full prompt string from current debate state."""

    from langchain_core.runnables import RunnableConfig

    # -- Sync execution --

    def invoke(self, state: DebateState, config: RunnableConfig | None = None) -> DebateState:
        """Run agent synchronously and update state."""
        llm = self._build_llm(streaming=False)
        prompt = self.build_prompt(state)
        # Pass config to enable callback propagation
        response = llm.invoke(prompt, config=config)
        output = parse_agent_response(response.content)
        return self._apply_output(state, output)

    def stream(self, state: DebateState, config: RunnableConfig | None = None) -> Iterator[str]:
        """Stream tokens synchronously, then update state."""
        llm = self._build_llm(streaming=True)
        prompt = self.build_prompt(state)
        accumulated = []

        # Pass config here too
        for chunk in llm.stream(prompt, config=config):
            text = chunk.content
            accumulated.append(text)
            yield text

        full_text = "".join(accumulated)
        output = parse_agent_response(full_text)
        self._apply_output(state, output)

    # -- Async execution --

    async def ainvoke(self, state: DebateState, config: RunnableConfig | None = None) -> DebateState:
        """Run agent asynchronously and update state."""
        llm = self._build_llm(streaming=False)
        prompt = self.build_prompt(state)
        response = await llm.ainvoke(prompt, config=config)
        output = parse_agent_response(response.content)
        return self._apply_output(state, output)

    async def astream(self, state: DebateState, config: RunnableConfig | None = None) -> AsyncIterator[str]:
        """Stream tokens asynchronously, then update state."""
        llm = self._build_llm(streaming=True)
        prompt = self.build_prompt(state)
        accumulated = []

        async for chunk in llm.astream(prompt, config=config):
            text = chunk.content
            accumulated.append(text)
            yield text

        full_text = "".join(accumulated)
        output = parse_agent_response(full_text)
        self._apply_output(state, output)

    # -- LangGraph node entry point --

    def __call__(self, state: DebateState, config: RunnableConfig | None = None) -> DebateState:
        """Entry point when used as a LangGraph node.
        
        LangGraph automatically injects 'config' if the signature accepts it.
        """
        if state.get("enable_streaming", False):
            # We still print to stdout for CLI, but we MUST pass config to stream() 
            # so the parent graph observer (astream_events) can see the tokens.
            print(f"\n[{self.name}] Thinking process:")
            for token in self.stream(state, config=config):
                print(token, end="", flush=True)
            print("\n")
            return state

        return self.invoke(state, config=config)

    # -- Internal helpers --

    def _build_llm(self, streaming: bool) -> ChatGoogleGenerativeAI:
        return create_llm(
            self._llm_settings,
            streaming=streaming,
            max_tokens=self._max_tokens,
        )

    def _apply_output(self, state: DebateState, output: AgentOutput) -> DebateState:
        state[self.output_field] = output
        state["history"].append(
            self._format_history_entry(state["round_number"], output)
        )
        return state

    def _format_history_entry(self, round_number: int, output: AgentOutput) -> str:
        return (
            f"\n[{self.name}] Round {round_number}\n"
            f"{'=' * 40}\n"
            f"Reasoning:\n{output['reasoning']}\n\n"
            f"Conclusion:\n{output['conclusion']}"
        )
