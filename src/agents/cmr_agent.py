from typing import AsyncIterator

from langchain_core.language_models import LanguageModelLike
from langchain_core.messages import HumanMessage
from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import create_react_agent

from agents.events import Event, MessageEvent, ToolEvent
from agents.tools import search_collections, search_granules

SYSTEM_PROMPT = """
You are an AI assistant specialized in helping users discover and understand NASA Earth science data through the Common Metadata Repository (CMR) API. Your role is to:

Use tools to provide answers, and don't use your general knowledge. [IMPORTANT]

1. Core Capabilities:
- Interpret natural language queries about Earth science data.
- Translate user questions into appropriate CMR API calls.
- Process and explain results in user-friendly terms.

2. API Interaction Rules:
- Use the `search_collections` endpoint for dataset discovery. This returns a collection ID that will be used for further searches.
- The `search_granules` endpoint is used to search for file-level details, but it requires the `collection_id` returned by `search_collections`.
- When using `search_collections`, the parameter `keyword` should only have a single word passed onto it as the search term.
- For `search_granules`, support key parameters:
    * Temporal: `temporal[]=<start-date>,<end-date>`
    * Spatial: `bounding_box[]=<w,s,e,n>`
    * Keywords: `keyword=<search-term>`
"""


class CMRAgent:
    def __init__(self, model: LanguageModelLike, config: RunnableConfig | dict):
        self.config = config
        self.model = model
        self._tools = [search_collections, search_granules]
        self._memory = MemorySaver()
        self._agent_executor = create_react_agent(
            self.model, self._tools, state_modifier=SYSTEM_PROMPT, checkpointer=self._memory
        )

    async def query(self, user_input: str) -> AsyncIterator[Event]:
        message = {"messages": [HumanMessage(content=user_input)]}

        async for event in self._agent_executor.astream_events(
            message, config=self.config, stream_mode="updates", version="v1"
        ):
            if tool_event := ToolEvent.from_langchain_event(event):
                yield tool_event
                continue

            if message_event := MessageEvent.from_langchain_event(event):
                yield message_event
                continue
