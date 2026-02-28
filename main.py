"""
CLI entry point for the AI Debate System.

Usage:
    python main.py "Should AI replace teachers in education?"
    python main.py "Is remote work better than office work?" --rounds 3 --no-stream
    python main.py "Topic here" --async
"""

import argparse
import asyncio
import os
import sys

# Add 'src' to sys.path to ensure modules can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "src")))

from config.settings import load_settings
from runner import arun_debate, run_debate


def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="AI Debate System -- Multi-Agent Reasoning via LangGraph",
    )
    parser.add_argument(
        "topic",
        type=str,
        help="The debate topic or proposition to evaluate.",
    )
    parser.add_argument(
        "--rounds",
        type=int,
        default=None,
        help="Maximum number of debate rounds (overrides env config).",
    )
    parser.add_argument(
        "--no-stream",
        action="store_true",
        default=False,
        help="Disable streaming output.",
    )
    parser.add_argument(
        "--async",
        dest="use_async",
        action="store_true",
        default=False,
        help="Run the debate loop asynchronously.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()
    settings = load_settings()

    if args.rounds is not None:
        debate = settings.debate
        settings = settings.__class__(
            llm=settings.llm,
            debate=debate.__class__(
                max_rounds=args.rounds,
                enable_streaming=debate.enable_streaming and not args.no_stream,
                enable_neutral_agent=debate.enable_neutral_agent,
                language=debate.language,
            ),
        )
    elif args.no_stream:
        debate = settings.debate
        settings = settings.__class__(
            llm=settings.llm,
            debate=debate.__class__(
                max_rounds=debate.max_rounds,
                enable_streaming=False,
                enable_neutral_agent=debate.enable_neutral_agent,
                language=debate.language,
            ),
        )

    if args.use_async:
        asyncio.run(arun_debate(args.topic, settings))
    else:
        run_debate(args.topic, settings)


if __name__ == "__main__":
    main()
