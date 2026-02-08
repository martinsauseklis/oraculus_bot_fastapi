from fastapi import FastAPI, WebSocket
from dotenv import load_dotenv
from openai import AsyncOpenAI

from agents import Runner, SQLiteSession

from agents.exceptions import AgentsException
from MatrixTypes import MatrixRequest
import uuid
from server import codex_mcp, postgres_mcp, start_mcp_manager
from agent import agent_error_input, agent_input, initialize_assistant, validate_response
import logging
logger = logging.getLogger("uvicorn.error")

load_dotenv()

app = FastAPI()
client = AsyncOpenAI()


@app.websocket("/")
async def llm_websocket(ws: WebSocket):
    session = SQLiteSession(str(uuid.uuid4()))
    async with start_mcp_manager(
        postgres_mcp()
    ) as mcps:
        agent = initialize_assistant(mcps, session)

        await ws.accept()
        while True:
            data = await ws.receive_json()
            request = MatrixRequest(**data)
            logger.info(f"Got a message from user: {request}")
            try:
                input = await agent_input(session, request.prompt)
                response = Runner.run_streamed(agent, input=input, max_turns=20)
                # response = await Runner.run(agent, input=input)
            except AgentsException as e:
                input = await agent_error_input(e, session, request.prompt)
                response = Runner.run_streamed(agent, input=input, max_turns=20)
            finally:
                async for r in response.stream_events():
                    logger.info(f"event: {r}")
                if response.is_complete:
                    await session.add_items([item.to_input_item() for item in response.new_items])
                    validated_response = validate_response(
                        response, request.room_id, request.event_id)
                    await ws.send_json(validated_response.model_dump())
