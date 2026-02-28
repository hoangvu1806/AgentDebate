import asyncio
import json
import logging
import os
import sys
from typing import AsyncGenerator

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from sse_starlette.sse import EventSourceResponse

from agents.topic_extractor_agent import TopicExtractor
from config.settings import load_settings
from graph.debate_graph import build_debate_graph
from models.state import AgentOutput, DebateState

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Debate API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class DebateRequest(BaseModel):
    topic: str          # raw user input (may be long, with context)
    max_rounds: int = 2
    enable_streaming: bool = True
    enable_neutral_agent: bool = True


@app.post("/api/debate/stream")
async def stream_debate(request: DebateRequest):
    """Start a debate and stream events via SSE.

    The raw user input is first processed by TopicExtractor to produce
    a crisp debate topic. The original input is preserved as user_context
    and passed to all agents.
    """
    settings = load_settings()
    graph = build_debate_graph(settings)
    extractor = TopicExtractor(settings.llm)

    async def event_generator() -> AsyncGenerator[dict, None]:
        # Phase 1: Extract a clean debate topic from raw user input
        raw_input = request.topic
        extracted_topic = await extractor.aextract(raw_input)

        yield {
            "data": json.dumps({
                "type": "topic_ready",
                "topic": extracted_topic,
                "user_context": raw_input,
            })
        }

        # Phase 2: Run the debate graph with full context
        empty_output = AgentOutput(reasoning="", conclusion="")
        initial_state = DebateState(
            topic=extracted_topic,
            user_context=raw_input,
            round_number=1,
            max_rounds=request.max_rounds,
            enable_streaming=request.enable_streaming,
            pro_output=empty_output,
            con_output=empty_output,
            neutral_output=empty_output,
            judge_output=empty_output,
            summary_output=empty_output,
            history=[],
            should_continue=True,
        )

        active_agent: str | None = None
        agent_names = ["pro", "con", "neutral", "judge", "summary"]

        try:
            async for event in graph.astream_events(
                initial_state,
                version="v1",
                include_names=agent_names,
            ):
                kind = event["event"]

                if kind == "on_chain_start" and event["name"] in agent_names:
                    active_agent = event["name"].upper()
                    yield {
                        "data": json.dumps({
                            "type": "node_start",
                            "agent": active_agent,
                        })
                    }

                elif kind == "on_chat_model_stream" and active_agent:
                    content = event["data"]["chunk"].content
                    if content:
                        yield {
                            "data": json.dumps({
                                "type": "stream_token",
                                "agent": active_agent,
                                "token": content,
                            })
                        }

                elif kind == "on_chain_end" and event["name"] in agent_names:
                    output_state = event["data"].get("output")
                    agent_name = event["name"]
                    output_field = f"{agent_name}_output"

                    reasoning = ""
                    conclusion = ""
                    round_number = 1

                    if output_state:
                        agent_data = output_state.get(output_field)
                        if agent_data:
                            reasoning = agent_data.get("reasoning", "")
                            conclusion = agent_data.get("conclusion", "")
                        round_number = output_state.get("round_number", 1)

                    yield {
                        "data": json.dumps({
                            "type": "node_end",
                            "agent": agent_name.upper(),
                            "reasoning": reasoning,
                            "conclusion": conclusion,
                            "round": round_number,
                        })
                    }
                    active_agent = None

            yield {
                "data": json.dumps({
                    "type": "debate_end",
                })
            }

        except Exception as e:
            logger.error(f"Error during graph execution: {e}")
            yield {
                "data": json.dumps({
                    "type": "debate_error",
                    "message": "Please try again later." if "429" in str(e) else str(e)
                })
            }

    return EventSourceResponse(event_generator())

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
