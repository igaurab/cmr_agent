import asyncio
import json
from dataclasses import dataclass
from typing import List, Optional

import streamlit as st
from langchain_openai import ChatOpenAI

from agents.cmr_agent import CMRAgent
from agents.events import MessageEvent, ToolEvent
from config import settings


@dataclass
class Message:
    role: str
    content: str
    tools: Optional[List[ToolEvent]] = None


def initialize_session_state():
    """Initializes streamlit session state variables"""
    st.session_state.setdefault("messages", [])
    st.session_state.setdefault("current_tools", {})

    if "cmr_agent" not in st.session_state:
        config = {"configurable": {"thread_id": "123"}}
        model = ChatOpenAI(model=settings.OPENAI_MODEL, streaming=True)
        st.session_state.cmr_agent = CMRAgent(config=config, model=model)


def display_message(message: Message):
    with st.chat_message(message.role):
        st.markdown(message.content)


def display_chat_history():
    for message in st.session_state.messages:
        display_message(message)


def format_tool_call(event: ToolEvent):
    """Format the tool call event for display."""
    assert isinstance(event, ToolEvent)
    return f"🔧 Calling tool: {event.name}\nInputs: {json.dumps(event.input_data, indent=2)}"


def handle_streamlit_message(prompt: str):
    """Handle user input"""

    user_message = Message(role="user", content=prompt)
    display_message(user_message)
    st.session_state.messages.append(user_message)

    assistant_message = Message(role="assistant", content="", tools=[])

    with st.chat_message("assistant"):
        tools_status = st.container()
        response_container = st.empty()

        async def process_and_display():
            content = ""
            async for event in st.session_state.cmr_agent.query(prompt):
                if isinstance(event, ToolEvent):
                    if event.status == "started":
                        with tools_status:
                            st.info(format_tool_call(event))
                    if event.status == "completed":
                        assistant_message.tools.append(event)
                if isinstance(event, MessageEvent):
                    content += event.content
                    response_container.markdown(content)
                    if event.status == "completed":
                        assistant_message.content = content
                        st.session_state.messages.append(assistant_message)
                        if assistant_message.tools:
                            with st.expander("🔍Debug Info", expanded=False):
                                for tool in assistant_message.tools:
                                    st.write(f"Tool {tool.name}")
                                    st.write(f"Input: {tool.data['input']}")
                                    st.write("Output:")
                                    st.write(tool.output_data)

        asyncio.run(process_and_display())


def streamlit_main():
    """Main streamlit applicaiton"""

    st.title("CMR Chat Interface")
    display_chat_history()
    if prompt := st.chat_input("Type your message here..."):
        handle_streamlit_message(prompt)


if __name__ == "__main__":
    initialize_session_state()
    streamlit_main()
