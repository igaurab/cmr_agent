from abc import ABC
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class Event(ABC):
    name: str
    data: Dict[str, Any]


@dataclass
class ToolEvent(Event):
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    status: str = "started"

    @classmethod
    def from_langchain_event(cls, event: Dict[str, Any]) -> Optional["ToolEvent"]:
        if event["event"] not in ("on_tool_start", "on_tool_end"):
            return None

        status = "started" if event["event"] == "on_tool_start" else "completed"
        input_data = event["data"].get("input") if status == "started" else None
        output_data = event["data"].get("output") if status == "completed" else None

        return cls(
            name=event["name"], data=event["data"], input_data=input_data, output_data=output_data, status=status
        )


@dataclass
class MessageEvent(Event):
    content: str
    role: str = "assistant"
    status: str = "started"

    @classmethod
    def from_langchain_event(cls, event: Dict[str, Any]) -> Optional["MessageEvent"]:
        if event["event"] == "on_chat_model_stream":
            content = event["data"]["chunk"].content
            if content:
                return cls(
                    name="chat_message",
                    data=event["data"],
                    content=content,
                )
            if not content:
                chunk = event["data"]["chunk"]
                if hasattr(chunk, "response_metadata"):
                    if chunk.response_metadata.get("finish_reason") == "stop":
                        return cls(name="chat_message", data=event["data"], content=content, status="completed")
        elif event["event"] in ("on_chain_start", "on_chain_end") and event["name"] == "Agent":
            content = ""
            if event["event"] == "on_chain_start":
                content = f"Starting agent with input: {event['data'].get('input')}"
            else:
                content = f"Agent completed with output: {event['data'].get('output', {}).get('output')}"

            return cls(
                name="agent_message",
                data=event["data"],
                content=content,
            )
        return None
