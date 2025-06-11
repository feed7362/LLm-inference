from fastapi import WebSocket, APIRouter
from fastapi.websockets import WebSocketDisconnect
from llm_manager import LLMEngine
from prompts import format_input, schema_validation

from utils.logger import CustomLogger
logger = CustomLogger(__name__)

websocket_router = APIRouter(
    prefix="",
    tags=["websocket"]
)

@websocket_router.websocket("/stream")
async def stream_websocket(websocket: WebSocket):
    try:
        await websocket.accept()
        while True:
            parsed_data = await websocket.receive_json()
            logger.debug("Data received from WebSocket: %s", parsed_data)

            if not isinstance(parsed_data, dict) or "messages" not in parsed_data:
                await websocket.send_json({
                    "error": "Must be Json object type: {'messages': [ ... ]}"
                })
                continue
                
            messages = parsed_data["messages"]

            await stream_model_response(messages, websocket)
    except WebSocketDisconnect:
        logger.exception("WebSocket disconnected.")
    except Exception as e:
        logger.exception(f"General error: {e}")
        try:
            await websocket.send_json({"error": str(e)})
        except Exception as send_error:
            logger.exception(f"Error sending error response: {send_error}")
    finally:
        await websocket.close()

async def stream_model_response(inputs: str, websocket: WebSocket):
    stream = True
    try:
        prompt_template = format_input(inputs)
        prompt = prompt_template.format(messages=inputs)

        logger.debug("Formatted prompt: %s", prompt)
        
        engine = LLMEngine()
        response = engine.infer(prompt, stream=stream)
        if stream:
            async for chunk in response:
                await websocket.send_json({"token": schema_validation(chunk["messages"][-1])})
        else:
            await websocket.send_json({"token": schema_validation(response["messages"][-1])})

    except Exception as e:
        logger.exception("Streaming error")
        if websocket.client_state.name == "CONNECTED":
            try:
                await websocket.send_json({"error": str(e)})
                await websocket.close(code=1011)
            except RuntimeError:
                pass
    