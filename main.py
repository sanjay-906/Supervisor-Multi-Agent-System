import json
import traceback
import uuid
import pickle
from pathlib import Path
from datetime import datetime
from typing import AsyncGenerator, Optional
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from langchain_core.messages import HumanMessage, AIMessage, ToolMessage

from agentics import supervisor
from langfuse import get_client
from langfuse.langchain import CallbackHandler


langfuse = get_client()
langfuse_handler = CallbackHandler()


class ChatRequest(BaseModel):
    message: str
    thread_id: Optional[str] = None
    user_id: Optional[str] = "anonymous"


class ChatSession(BaseModel):
    thread_id: str


sessions: dict[str, list] = {}

STATE_DIR = Path("./state_snapshots")
STATE_DIR.mkdir(parents=True, exist_ok=True)


def save_state_snapshot(thread_id: str, state_snapshot) -> None:
    """Pickle the full LangGraph state snapshot for a thread, overwriting the previous save."""
    path = STATE_DIR / f"{thread_id}.pkl"
    try:
        with open(path, "wb") as f:
            pickle.dump(state_snapshot, f, protocol=pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        print(f"[state_snapshot] failed to save state for thread {thread_id}: {e}", flush=True)


def sse(event: str, data: dict) -> str:
    payload = json.dumps(data, default=str)
    return f"event: {event}\ndata: {payload}\n\n"


def map_message_to_event(msg) -> Optional[dict]:

    if isinstance(msg, AIMessage):
        name = getattr(msg, "name", "supervisor")
        is_handoff_back = msg.response_metadata.get("__is_handoff_back", False)

        if msg.tool_calls:
            calls = []
            for tc in msg.tool_calls:
                calls.append({
                    "id": tc.get("id"),
                    "name": tc["name"],
                    "args": tc.get("args", {}),
                })
            return {
                "type": "tool_call",
                "agent": name,
                "calls": calls,
                "is_handoff": any(
                    "transfer_to" in c["name"] or "transfer_back" in c["name"]
                    for c in calls
                ),
            }

        if is_handoff_back:
            return {
                "type": "handoff_back",
                "agent": name,
                "text": str(msg.content),
            }

        if msg.content:
            text = ""
            if isinstance(msg.content, list):
                for part in msg.content:
                    if isinstance(part, dict) and part.get("type") == "text":
                        text += part["text"]
            else:
                text = str(msg.content)

            usage = {}
            if hasattr(msg, "usage_metadata") and msg.usage_metadata:
                usage = {
                    "input_tokens": msg.usage_metadata.get("input_tokens", 0),
                    "output_tokens": msg.usage_metadata.get("output_tokens", 0),
                    "total_tokens": msg.usage_metadata.get("total_tokens", 0),
                }

            return {
                "type": "agent_message",
                "agent": name,
                "text": text,
                "usage": usage,
            }

    elif isinstance(msg, ToolMessage):
        try:
            content = json.loads(msg.content)
        except Exception:
            content = msg.content

        return {
            "type": "tool_result",
            "tool_name": msg.name,
            "tool_call_id": msg.tool_call_id,
            "content": content,
        }

    elif isinstance(msg, HumanMessage):
        return None

    return None


async def stream_graph(
    supervisor,
    state: dict,
    config: dict,
) -> AsyncGenerator[str, None]:
    """
    Run supervisor.astream_events() and yield SSE chunks.

    Event types emitted:
      - stream_start -> run begins
      - agent_start -> an agent node is entered
      - token -> incremental LLM token
      - tool_call -> agent decided to call a tool (incl. handoffs)
      - tool_result -> tool returned a result
      - agent_message -> full agent response (with usage stats)
      - handoff_back -> agent transferring control back to supervisor
      - stream_end -> run finished
      - error -> something went wrong
    """
    try:
        yield sse("stream_start", {"ts": datetime.utcnow().isoformat()})

        current_agent = None
        agent_token_buffers: dict[str, str] = {}
        agents_streamed: set[str] = set()
        emitted_msg_ids: set[str] = set()

        async for event in supervisor.astream_events(
            state,
            config=config,
            version="v2",
        ):
            kind = event.get("event")
            name = event.get("name", "")
            # tags = event.get("tags", [])
            data = event.get("data", {})

            if kind == "on_chain_start" and event.get("metadata", {}).get("langgraph_node"):
                node = event["metadata"]["langgraph_node"]
                KNOWN_AGENTS = {"supervisor", "flight_agent", "hotel_agent", "itinerary_agent"}
                if node in KNOWN_AGENTS and node != current_agent:
                    current_agent = node
                    yield sse("agent_start", {"agent": node})

            elif kind == "on_chat_model_stream":
                chunk = data.get("chunk")
                if chunk:
                    token_text = ""
                    if hasattr(chunk, "content"):
                        c = chunk.content
                        if isinstance(c, str):
                            token_text = c
                        elif isinstance(c, list):
                            for part in c:
                                if isinstance(part, dict) and part.get("type") == "text":
                                    token_text += part.get("text", "")

                    if token_text:
                        agent_key = current_agent or "supervisor"
                        agent_token_buffers.setdefault(agent_key, "")
                        agent_token_buffers[agent_key] += token_text
                        agents_streamed.add(agent_key)
                        yield sse("token", {"agent": agent_key, "token": token_text})

            elif kind == "on_tool_start":
                tool_name = name
                tool_input = data.get("input", {})
                is_handoff = "transfer_to" in tool_name or "transfer_back" in tool_name
                yield sse("tool_call", {
                    "agent": current_agent or "supervisor",
                    "tool_name": tool_name,
                    "args": tool_input,
                    "is_handoff": is_handoff,
                })

            elif kind == "on_tool_end":
                tool_name = name
                output = data.get("output")
                if output is not None:
                    if hasattr(output, "content"):
                        try:
                            content = json.loads(output.content)
                        except Exception:
                            content = str(output.content)
                    else:
                        content = str(output)

                    yield sse("tool_result", {
                        "agent": current_agent or "supervisor",
                        "tool_name": tool_name,
                        "content": content,
                    })

            elif kind == "on_chain_end" and event.get("metadata", {}).get("langgraph_node"):
                node = event["metadata"]["langgraph_node"]

                out = data.get("output", {})
                if not isinstance(out, dict):
                    continue
                msgs = out.get("messages", [])
                if not isinstance(msgs, list):
                    continue

                for msg in msgs:
                    msg_id = getattr(msg, "id", None)
                    if msg_id and msg_id in emitted_msg_ids:
                        continue

                    payload = map_message_to_event(msg)
                    if not payload:
                        continue

                    evt_type = payload.pop("type")
                    agent_name = payload.get("agent", node)

                    if evt_type == "agent_message":
                        if msg_id:
                            emitted_msg_ids.add(msg_id)
                        if agent_name in agents_streamed:
                            yield sse("agent_message_meta", {
                                "agent": agent_name,
                                "usage": payload.get("usage", {}),
                            })
                            agents_streamed.discard(agent_name)
                        else:
                            yield sse("agent_message", payload)

                    elif evt_type == "handoff_back":
                        if msg_id and msg_id in emitted_msg_ids:
                            continue
                        if msg_id:
                            emitted_msg_ids.add(msg_id)
                        yield sse("handoff_back", payload)

        yield sse("stream_end", {
            "ts": datetime.utcnow().isoformat(),
            "final_state": None,
        })

    except Exception as e:
        yield sse("error", {"message": str(e)})


app = FastAPI(
    title="Travel Planner AI",
    description="LangGraph multi-agent travel planner with real-time streaming",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post("/chat/session")
async def create_session() -> ChatSession:
    thread_id = str(uuid.uuid4())
    sessions[thread_id] = {"messages": []}
    return ChatSession(thread_id=thread_id)


@app.post("/chat/stream")
async def chat_stream(req: ChatRequest):
    thread_id = req.thread_id or str(uuid.uuid4())
    if thread_id not in sessions:
        sessions[thread_id] = {"messages": []}

    session = sessions[thread_id]

    session["messages"].append(HumanMessage(content=req.message))

    state = {"messages": session["messages"]}
    config = {
        "configurable": {
            "thread_id": thread_id,
            "user_id": req.user_id,
        },
        "callbacks": [langfuse_handler]
    }

    async def event_stream():
        graph = supervisor

        async for chunk in stream_graph(graph, state, config):
            yield chunk

        try:
            new_state = await graph.aget_state(config)
            sessions[thread_id]["messages"] = new_state.values.get("messages", session["messages"])
            save_state_snapshot(thread_id, new_state)
        except Exception:
            traceback.print_exc()
            pass

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )


@app.get("/chat/{thread_id}/history")
async def get_history(thread_id: str):
    if thread_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    msgs = sessions[thread_id]["messages"]
    history = []
    for m in msgs:
        if isinstance(m, HumanMessage):
            history.append({"role": "user", "content": m.content})
        elif isinstance(m, AIMessage) and m.content:
            name = getattr(m, "name", "supervisor")
            content = m.content
            if isinstance(content, list):
                text = " ".join(p.get("text", "") for p in content if isinstance(p, dict))
            else:
                text = str(content)
            history.append({"role": "assistant", "agent": name, "content": text})
    return {"thread_id": thread_id, "history": history}
