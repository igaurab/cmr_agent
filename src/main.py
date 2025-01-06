import asyncio

from langchain_openai import ChatOpenAI
from loguru import logger

from agents.cmr_agent import CMRAgent
from agents.events import Event, MessageEvent, ToolEvent
from config import settings


async def handle_events(event: Event):
    if isinstance(event, ToolEvent):
        if event.status == "started":
            logger.info(f"\nStarting tool: {event.name} with inputs: {event.input_data}")
        else:
            logger.info(f"Done tool: {event.name}\n")

    elif isinstance(event, MessageEvent):
        print(event.content, end="", flush=True)


async def main():
    config = {"configurable": {"thread_id": "123"}}
    model = ChatOpenAI(model=settings.OPENAI_MODEL, streaming=True)
    agent_handler = CMRAgent(config=config, model=model)
    while True:
        user_input = input("User: ")
        logger.info("Assistant: ", end="")
        async for event in agent_handler.query(user_input):
            await handle_events(event)


if __name__ == "__main__":
    asyncio.run(main())
